"""CANU commands for configuring network features on switches."""

import json
import logging
from datetime import datetime

import click
import click_spinner
import urllib3
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from nornir import InitNornir
from nornir.core.filter import F
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping
from nornir_scrapli.tasks import send_config

from canu.backup.network.network import backup_switches
from canu.generate.switch.config.config import parse_sls_for_config
from canu.utils.inventory import inventory

# Define the network configuration profiles and their corresponding templates
PROFILES = {
    "nmn-isolation-1.7": {
        "description": ("Applies the MANAGED_NODE_ISOLATION ACL to a CSM 1.7+ environment."),
        "templates": [
            "1.7/aruba/common/_acl_definitions.j2",
            "1.7/aruba/common/_acl_apply_nmn_isolation_1.7.j2",
        ],
    },
    "migrate-nmn-1.6-to-1.7": {
        "description": ("Migrates switch ACLs from CSM 1.6 (nmn-hmn) to CSM 1.7 (MANAGED_NODE_ISOLATION)."),
        "templates": [
            "1.7/aruba/common/_acl_cleanup_nmn_hmn_1.6.j2",
            "1.7/aruba/common/_acl_definitions.j2",
            "1.7/aruba/common/_acl_apply_nmn_isolation_1.7.j2",
        ],
    },
    "migrate-nmn-1.7-to-1.6": {
        "description": "Migrates switch ACLs from CSM 1.7 to CSM 1.6.",
        "templates": [
            "1.7/aruba/common/_acl_revert.j2",
        ],
    },
}


@click.command()
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
    required=True,
)
@click.option(
    "--network",
    default="HMN",
    show_default=True,
    type=click.Choice(["HMN", "CMN"], case_sensitive=False),
    help="The network that is used to connect to the switches.",
)
@click.option(
    "--log",
    "log_",
    is_flag=True,
    help="Enable logging.",
    required=False,
)
@click.option(
    "--csm",
    required=True,
    help="CSM version",
    type=click.Choice(["1.0", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"]),
)
@click.option(
    "--architecture",
    "-a",
    required=True,
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
    help="CSM architecture",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show generated configuration without applying it to switches",
    default=False,
)
@click.option(
    "--switch",
    help="Target specific switch(es) by hostname or IP address."
    "Can be used multiple times (e.g., --switch sw-spine-001 --switch 10.254.0.4)",
    type=str,
    multiple=True,
)
@click.option(
    "--backup-folder",
    default="./canu_network_backups",
    show_default=True,
    help="Folder to store backup configurations before making changes",
)
@click.option(
    "--profile",
    type=click.Choice(PROFILES.keys(), case_sensitive=False),
    required=True,
    help="The network configuration profile to apply.",
)
@click.pass_context
def network(
    ctx,
    username,
    password,
    sls_file,
    network,
    log_,
    csm,
    architecture,
    dry_run,
    switch,
    backup_folder,
    profile,
):
    """Configure network features on switches using configuration profiles.

    This command uses profiles to apply specific, targeted network configurations including
    ACLs, private VLANs, and other network features.

    Args:
        ctx: The click context.
        username: The switch username.
        password: The switch password.
        sls_file: The file containing system SLS JSON data.
        network: The network that is used to connect to the switches.
        log_: Enable logging.
        csm: The CSM version.
        architecture: The CSM architecture.
        dry_run: Show generated configuration without applying it to switches.
        switch: Target specific switch(es) by hostname or IP address.
        backup_folder: The folder to store backup configurations before making changes.
        profile: The network configuration profile to apply.


    Example commands:

    Apply the CSM 1.7 NMN isolation ACL to all compatible switches:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile nmn-isolation-1.7

    Migrate a single switch's ACLs from CSM 1.6 to 1.7:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile migrate-nmn-1.6-to-1.7 --switch sw-leaf-001

    Perform a dry run to see the configuration that would be generated:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile nmn-isolation-1.7 --dry-run
    """
    if not password and not dry_run:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )

    # Set up logging
    if log_:
        logging.basicConfig(level=logging.DEBUG)

    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Validate profile-specific requirements
    selected_profile = PROFILES[profile]

    # Display operation summary
    click.echo(f"Applying network configuration profile '{profile}':")
    click.echo(f"  Description: {selected_profile['description']}")
    click.echo(f"  CSM version: {csm}")
    click.echo(f"  Architecture: {architecture}")

    # Build Nornir inventory
    click.echo("Building switch inventory...")
    switch_inventory = inventory(username, password, network, sls_file)
    nr = InitNornir(
        runner={"plugin": "threaded", "options": {"num_workers": 10}},
        inventory=switch_inventory,
        logging={"enabled": log_, "to_console": True, "level": "DEBUG"},
    )

    # Filter switches
    if switch:
        target_hosts = nr.filter(lambda host: host.name in switch or str(host.hostname) in switch)
        if not target_hosts.inventory.hosts:
            click.secho(f"Switch(es) '{', '.join(switch)}' not found in inventory", fg="red")
            return
        nr = target_hosts
    else:
        # By default, apply to leaf and spine switches
        nr = nr.filter(lambda host: any(x in host.name.lower() for x in ["leaf", "spine"]))

    if not nr.inventory.hosts:
        click.secho("No target switches found in inventory.", fg="red")
        return

    online_hosts = nr
    if not dry_run:
        # Check connectivity
        click.echo("Checking switch connectivity...")
        with click_spinner.spinner():
            ping_check = nr.run(task=tcp_ping)
            result_dictionary = ResultSerializer(ping_check)
            unreachable_hosts = [h for h, r in result_dictionary.items() if not r["tcp_ping"][22]]

        for hostname in unreachable_hosts:
            click.secho(f"{hostname} is not reachable via SSH, skipping.", fg="red")

        online_hosts = nr.filter(
            F(name__in=[h for h, r in result_dictionary.items() if r["tcp_ping"][22]]),
        )
        if not online_hosts.inventory.hosts:
            click.secho("No switches are reachable. Exiting.", fg="red")
            return

    # Generate network configuration using templates from the selected profile
    click.echo("Generating network configuration from templates...")

    # Suppress verbose logging during config generation
    old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.ERROR)

    try:
        # Parse SLS data
        sls_file.seek(0)
        input_json = json.load(sls_file)
        sls_json = [network[x] for network in [input_json.get("Networks", {})] for x in network]
        sls_variables = parse_sls_for_config(sls_json)

        # Initialize Jinja2 environment
        project_root = "."
        network_templates_folder = f"{project_root}/network_modeling/configs/templates"
        env = Environment(
            loader=FileSystemLoader(network_templates_folder),
            undefined=StrictUndefined,
        )

        # Generate configuration for each host
        configs_to_apply = {}
        for host in online_hosts.inventory.hosts.values():
            # Setup variables for templates
            variables = {
                "NMN_VLAN": sls_variables["NMN_VLAN"],
                "NMN_IPs": sls_variables["NMN_IPs"],
                "SPINE_SWITCH_IPs": sls_variables["SPINE_SWITCH_IPs"],
                "ALL_SWITCH_IPs": sls_variables["ALL_SWITCH_IPs"],
                "RGW_VIP": sls_variables["RGW_VIP"],
                "KUBEAPI_VIP": sls_variables["KUBEAPI_VIP"],
                "NMN_NETWORK_IP": sls_variables["NMN_NETWORK_IP"],
                "NMN_NETMASK": sls_variables["NMN_NETMASK"],
                "NMNLB_NETWORK_IP": sls_variables["NMNLB_NETWORK_IP"],
                "NMNLB_NETMASK": sls_variables["NMNLB_NETMASK"],
                "NMNLB_TFTP": sls_variables["NMNLB_TFTP"],
            }
            config_to_apply = ""
            for template_file in selected_profile["templates"]:
                template = env.get_template(template_file)
                rendered_template = template.render(variables=variables)
                if config_to_apply and not config_to_apply.endswith('\n'):
                    config_to_apply += '\n'
                config_to_apply += rendered_template

            configs_to_apply[host.name] = config_to_apply

            if dry_run:
                click.secho(
                    f"Generated configuration for {host.name}:",
                    fg="green",
                )
                click.echo(config_to_apply)

        if dry_run:
            return

        # Backup switch configurations before making changes (once for all switches)
        backup_folder_path = f"{backup_folder}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        click.echo(f"Creating backup in {backup_folder_path}/...")
        try:
            backup_switches(online_hosts, backup_folder_path)
            click.secho("✓ Switch configurations backed up successfully", fg="green")
        except Exception as e:
            click.secho(f"Warning: Backup failed: {str(e)}", fg="yellow")
            if not click.confirm("Continue without backup?"):
                click.echo("Configuration cancelled.")
                return

        # Apply configuration to each host individually
        for host in online_hosts.inventory.hosts.values():
            if host.name not in configs_to_apply:
                continue

            click.echo(f"Applying configuration to {host.name}...")

            # Create a single-host nornir object for this specific host
            def create_host_filter(target_name):
                return lambda h: h.name == target_name
            single_host = online_hosts.filter(create_host_filter(host.name))
            result = single_host.run(
                task=send_config,
                config=configs_to_apply[host.name],
            )

            if host.name in result and result[host.name].failed:
                click.secho(
                    f"Failed to apply configuration to {host.name}: {result[host.name].exception}",
                    fg="red",
                )
            elif host.name in result:
                click.secho(
                    f"Successfully applied configuration to {host.name}",
                    fg="green",
                )
            else:
                click.secho(
                    f"Failed to apply configuration to {host.name}: No result returned",
                    fg="red",
                )

    finally:
        # Restore logging level
        logging.getLogger().setLevel(old_level)
