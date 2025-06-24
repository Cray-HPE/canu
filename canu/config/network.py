"""CANU commands for configuring network features on switches."""
import logging
import json
from datetime import datetime

import click
import click_spinner
from nornir import InitNornir
from nornir.core.filter import F
from nornir_scrapli.tasks import send_config
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import urllib3

from canu.generate.switch.config.config import parse_sls_for_config
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping
from canu.utils.inventory import inventory
from canu.backup.network.network import backup_switches

# Define the network configuration profiles and their corresponding templates
PROFILES = {
    "nmn-isolation-1.7": {
        "description": "Applies the MANAGED_NODE_ISOLATION ACL to a CSM 1.7+ environment.",
        "templates": [
            "1.7/aruba/common/_acl_definitions.j2",
            "1.7/aruba/common/_acl_apply_nmn_isolation_1.7.j2",
        ],
    },
    "migrate-nmn-1.6-to-1.7": {
        "description": "Migrates switch ACLs from CSM 1.6 (nmn-hmn) to CSM 1.7 (MANAGED_NODE_ISOLATION).",
        "templates": [
            "1.7/aruba/common/_acl_cleanup_nmn_hmn_1.6.j2",
            "1.7/aruba/common/_acl_definitions.j2",
            "1.7/aruba/common/_acl_apply_nmn_isolation_1.7.j2",
        ],
    },
    "nmn-private-vlan": {
        "description": "Configures NMN private VLAN (isolated VLAN) for CSM 1.7+ environments.",
        "templates": [
            "1.7/aruba/common/_pvlan_definitions.j2",
        ],
    },
    "remove-private-vlan": {
        "description": "Removes NMN private VLAN configuration from CSM 1.7+ environments.",
        "templates": [
            "1.7/aruba/common/_pvlan_remove.j2",
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
    help="Target specific switch(es) by hostname or IP address. Can be used multiple times (e.g., --switch sw-spine-001 --switch 10.254.0.4)",
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
@click.option(
    "--private-vlan-id",
    type=int,
    help="Private VLAN ID to use (required for private VLAN profiles)",
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
    private_vlan_id,
):
    """Configure network features on switches using configuration profiles.

    This command uses profiles to apply specific, targeted network configurations including
    ACLs, private VLANs, and other network features.

    Example commands:

    Apply the CSM 1.7 NMN isolation ACL to all compatible switches:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile nmn-isolation-1.7

    Migrate a single switch's ACLs from CSM 1.6 to 1.7:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile migrate-nmn-1.6-to-1.7 --switch sw-leaf-001

    Configure private VLAN 502 on all switches:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile nmn-private-vlan --private-vlan-id 502

    Remove private VLAN configuration:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile remove-private-vlan --private-vlan-id 502

    Perform a dry run to see the configuration that would be generated:
        canu config network --csm 1.7 --architecture full --sls-file sls.json --profile nmn-private-vlan --private-vlan-id 502 --dry-run
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
    if "private-vlan" in profile and not private_vlan_id:
        click.secho(f"Error: --private-vlan-id is required for profile '{profile}'", fg="red")
        return
    
    # Display operation summary
    click.echo(f"Applying network configuration profile '{profile}':")
    click.echo(f"  Description: {selected_profile['description']}")
    click.echo(f"  CSM version: {csm}")
    click.echo(f"  Architecture: {architecture}")
    if private_vlan_id:
        click.echo(f"  Private VLAN ID: {private_vlan_id}")

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
        
        online_hosts = nr.filter(F(name__in=[h for h, r in result_dictionary.items() if r["tcp_ping"][22]]))
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
        
        # Add profile-specific variables
        if private_vlan_id:
            variables["NMN_ISOLATED_VLAN"] = private_vlan_id

        # Initialize Jinja2 environment
        project_root = "."
        network_templates_folder = f"{project_root}/network_modeling/configs/templates"
        env = Environment(
            loader=FileSystemLoader(network_templates_folder),
            undefined=StrictUndefined,
        )

        # Render the full configuration string from the profile's templates
        config_string = ""
        for template_path in selected_profile['templates']:
            template = env.get_template(template_path)
            config_string += template.render(variables=variables) + "\n"

        if dry_run:
            click.echo("\nDRY RUN MODE - Configuration will NOT be applied to switches")
        
        click.echo("=" * 70)
        click.echo(f"Generated configuration for profile '{profile}':")
        click.echo(config_string)
        click.echo("=" * 70)
        
        if dry_run:
            click.echo("DRY RUN COMPLETE - No changes were applied to switches\n")
            return
        
        if not click.confirm("Do you want to proceed with applying this configuration to all targeted switches?"):
            click.echo("Configuration cancelled.")
            return
        
        # Backup before applying changes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_backup_folder = f"{backup_folder}_{timestamp}"
        click.echo(f"Creating backup in {timestamped_backup_folder}/...")
        try:
            with click_spinner.spinner():
                saved_files = backup_switches(online_hosts, timestamped_backup_folder)
            click.echo(f"✓ Backed up {len(saved_files)} switch configurations to ./{timestamped_backup_folder}/")
        except Exception as e:
            click.secho(f"Warning: Backup failed: {str(e)}", fg="yellow")
            if not click.confirm("Continue without backup?"):
                click.echo("Configuration cancelled.")
                return
        
        # Apply configuration
        click.echo("\nApplying network configuration...")
        with click_spinner.spinner():
            config_result = online_hosts.run(
                name="Apply Network Config",
                task=send_config,
                config=config_string,
            )
        
        # Report results
        success_count = 0
        click.echo("--- Apply Results ---")
        for hostname, result in config_result.items():
            if not result.failed:
                click.secho(f"  ✓ {hostname}: Successfully applied network configuration", fg="green")
                success_count += 1
            else:
                click.secho(f"  ✗ {hostname}: Failed - {result.exception}", fg="red")
        
        click.echo(f"\nNetwork configuration completed on {success_count}/{len(config_result)} switches.")
        
    except Exception as e:
        click.secho(f"An error occurred: {e}", fg="red")
        import traceback
        traceback.print_exc()
        return
    finally:
        # Restore original logging level
        logging.getLogger().setLevel(old_level) 