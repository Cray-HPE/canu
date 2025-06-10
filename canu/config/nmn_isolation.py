"""CANU commands for configuring NMN isolation ACLs."""
import logging
import json
from datetime import datetime

import click
import click_spinner
from nornir import InitNornir
from nornir.core.filter import F
from nornir_scrapli.tasks import send_config
import urllib3

from canu.generate.switch.config.config import generate_switch_config, parse_sls_for_config
from canu.validate.paddle.paddle import node_model_from_paddle
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping
from canu.utils.inventory import inventory
from canu.backup.network.network import backup_switches
from canu.style import Style





@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.command()
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
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
    "--ccj",
    help="Paddle CCJ file (required for config generation)",
    type=click.File("rb"),
)

@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
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
    default="./canu_nmn_isolation_backups",
    show_default=True,
    help="Folder to store backup configurations before making changes",
)
@click.pass_context
def nmn_isolation(
    ctx,
    username,
    password,
    sls_file,
    sls_address,
    network,
    log_,
    csm,
    architecture,
    ccj,
    dry_run,
    switch,
    backup_folder,
):
    """Configure NMN isolation ACL rules on network switches.

    This command generates and applies NMN_ISOLATION access control list configuration
    that controls traffic between NCN nodes on the NMN network. The ACL includes
    an object-group with NCN IPs and the access-list rules applied to VLAN 2.
    
    Generate and apply NMN isolation ACL configuration:
        canu config nmn-isolation --csm 1.7 --architecture full --ccj ./ccj.json
    
    Target specific switch(es):
        canu config nmn-isolation --csm 1.7 --architecture full --ccj ./ccj.json --switch sw-spine-001
    
    Dry run to preview configuration without applying:
        canu config nmn-isolation --csm 1.7 --architecture full --ccj ./ccj.json --dry-run

    Args:
        ctx: CANU context settings
        username: Switch username
        password: Switch password
        sls_file: JSON file containing SLS data
        sls_address: The address of SLS
        network: The network that is used to connect to the switches
        log_: Enable logging
        csm: CSM version for config generation
        architecture: CSM architecture for config generation
        ccj: Paddle CCJ file for config generation
        dry_run: Show generated configuration without applying it
        switch: Target specific switch(es) by hostname or IP address
        backup_folder: Folder to store backup configurations
    """
    if not password and not dry_run:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )

    # Validate required parameters for config generation
    if not ccj:
        click.secho("--ccj is required for generating NMN isolation configuration", fg="red")
        return

    # Set up logging
    if log_:
        logging.basicConfig(level=logging.DEBUG)

    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Display operation summary
    click.echo("Generating and applying NMN_ISOLATION ACL configuration...")
    click.echo(f"  CSM version: {csm}")
    click.echo(f"  Architecture: {architecture}")

    # Build Nornir inventory and generate configuration
    click.echo("Building switch inventory...")
    
    # Build inventory using the same method as pvlan.py
    switch_inventory = inventory(username, password, network, sls_file)
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 10,
            },
        },
        inventory=switch_inventory,
        logging={"enabled": log_, "to_console": True, "level": "DEBUG"},
    )

    # Filter switches based on options (same as pvlan.py)
    if switch:
        # Target specific switches by hostname or IP address
        target_hosts = nr.filter(lambda host: host.name in switch or str(host.hostname) in switch)
        if not target_hosts.inventory.hosts:
            click.secho(f"Switch(es) '{', '.join(switch)}' not found in inventory", fg="red")
            available_switches = [f"{host.name} ({host.hostname})" for host in nr.inventory.hosts.values()]
            click.secho(f"Available switches: {', '.join(available_switches)}", fg="yellow")
            return
        
        # Verify all requested switches were found
        found_switches = [host.name for host in target_hosts.inventory.hosts.values()]
        found_ips = [str(host.hostname) for host in target_hosts.inventory.hosts.values()]
        missing_switches = [s for s in switch if s not in found_switches and s not in found_ips]
        if missing_switches:
            click.secho(f"Warning: Switch(es) not found: {', '.join(missing_switches)}", fg="yellow")
        
        nr = target_hosts
    else:
        # Apply to all switches except edge and CDU switches
        filtered_hosts = nr.filter(lambda host: not any(x in host.name.lower() for x in ["edge", "cdu"]))
        if not filtered_hosts.inventory.hosts:
            click.secho("No compatible switches found in inventory (excluding edge and CDU switches)", fg="red")
            return
        nr = filtered_hosts

    if not dry_run:
        # Check if switches are reachable before applying configuration
        click.echo("Checking switch connectivity...")
        ping_check = nr.run(task=tcp_ping)
        result_dictionary = ResultSerializer(ping_check)
        unreachable_hosts = []

        for hostname, result in result_dictionary.items():
            if result["tcp_ping"][22] is False:
                click.secho(
                    f"{hostname} is not reachable via SSH, skipping configuration.",
                    fg="red",
                )
                unreachable_hosts.append(hostname)

        online_hosts = nr.filter(~F(name__in=unreachable_hosts))
        
        if not online_hosts.inventory.hosts:
            click.secho("No switches are reachable. Exiting.", fg="red")
            return
    else:
        online_hosts = nr

    # Generate NMN isolation configuration using template system (same as pvlan.py)
    click.echo("Generating NMN isolation configuration from templates...")
    
    # Suppress verbose logging during config generation
    old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Parse input data (same logic as pvlan.py)
        if ccj:
            ccj_json = json.load(ccj)
            architecture_type = ccj_json.get("architecture", architecture.lower())
        else:
            architecture_type = architecture.lower()
            
        # Map architecture types
        if architecture_type.lower() == "full" or architecture_type == "network_v2":
            architecture_type = "network_v2"
        elif architecture_type.lower() == "tds" or architecture_type == "network_v2_tds":
            architecture_type = "network_v2_tds"
        elif architecture_type.lower() == "v1" or architecture_type == "network_v1":
            architecture_type = "network_v1"

        # Create Node factory
        factory = NetworkNodeFactory(architecture_version=architecture_type)
        
        # Get nodes from CCJ input
        network_node_list, _ = node_model_from_paddle(factory, ccj_json)
            
        # Parse SLS data
        if sls_file:
            sls_file.seek(0)  # Reset file pointer
            input_json = json.load(sls_file)
            sls_json = [
                network[x] for network in [input_json.get("Networks", {})] for x in network
            ]
            sls_variables = parse_sls_for_config(sls_json)
        else:
            # For now, require sls_file for NMN isolation
            click.secho("SLS file is required for NMN isolation configuration", fg="red")
            return
        
        # Get switch names to configure from the filtered inventory
        switch_names = [host.name for host in online_hosts.inventory.hosts.values()]
        
        # Generate NMN isolation ACL configuration for each switch
        nmn_isolation_configs = {}
        
        for switch_name in switch_names:
            if any(x in switch_name.lower() for x in ["edge", "cdu"]):
                continue  # Skip edge and CDU switches
                
            try:
                template_folder = "tds" if architecture_type == "network_v2_tds" else "full"
                vendor_folder = "aruba"
                
                # Generate full switch config using existing template system
                full_config, devices, unknown = generate_switch_config(
                    csm=csm,
                    architecture=architecture_type,
                    network_node_list=network_node_list,
                    factory=factory,
                    switch_name=switch_name,
                    sls_variables=sls_variables,
                    template_folder=template_folder,
                    vendor_folder=vendor_folder,
                    preserve=None,
                    custom_config=None,
                    edge="Arista",
                    reorder=False,
                    bgp_control_plane="CHN",
                    vrf="CSM",
                    bond_app_nodes=False,
                    nmn_pvlan=None,  # Not using private VLAN for NMN isolation
                )
                
                # Extract only NMN isolation ACL related configuration from the generated config
                nmn_isolation_config = []
                lines = full_config.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Look for object-group ip address NMN_NCN
                    if line.startswith('object-group ip address NMN_NCN'):
                        nmn_isolation_config.append(line)
                        i += 1
                        
                        # Collect all lines for this object-group
                        while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                            if lines[i].strip():
                                nmn_isolation_config.append(lines[i])
                            i += 1
                        continue
                    
                    # Look for access-list ip NMN_ISOLATION
                    elif line.startswith('access-list ip NMN_ISOLATION'):
                        nmn_isolation_config.append(line)
                        i += 1
                        
                        # Collect all lines for this access-list
                        while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                            if lines[i].strip():
                                nmn_isolation_config.append(lines[i])
                            i += 1
                        continue
                    
                    i += 1
                
                if nmn_isolation_config:
                    nmn_isolation_configs[switch_name] = nmn_isolation_config
                    
            except Exception as e:
                click.secho(f"Warning: Could not generate config for {switch_name}: {str(e)}", fg="yellow")
                continue
        
        if not nmn_isolation_configs:
            click.secho("No NMN isolation configuration generated", fg="red")
            return
        
        # Display configuration
        config_string = ""
        for switch_name, config_lines in nmn_isolation_configs.items():
            if config_string == "":  # First switch config
                config_string = '\n'.join(config_lines)
            # All switches should have the same NMN isolation config, so we just use the first one
            break
        
        if dry_run:
            click.echo("DRY RUN MODE - Configuration will NOT be applied to switches")
            click.echo("=" * 70)
        
        switch_count = len(switch_names) if switch else len(nmn_isolation_configs)
        click.echo(f"Generated NMN isolation configuration for {switch_count} switch(es):")
        click.echo("=" * 50)
        click.echo(config_string)
        click.echo("=" * 50)
        
        if dry_run:
            click.echo("\nDRY RUN COMPLETE - No changes were applied to switches")
            return
        
        if not click.confirm("Do you want to proceed with applying this configuration?"):
            click.echo("Configuration cancelled.")
            return
        
        # Create timestamped backup folder and backup configurations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_backup_folder = f"{backup_folder}_{timestamp}"
        
        click.echo(f"Creating backup in {timestamped_backup_folder}/...")
        with click_spinner.spinner():
            try:
                saved_files = backup_switches(online_hosts, timestamped_backup_folder)
                click.echo(f"✓ Backed up {len(saved_files)} switch configurations")
                if saved_files:
                    click.echo(f"  Backup location: ./{timestamped_backup_folder}/")
                    click.echo(f"  Files: {', '.join(saved_files)}")
            except Exception as e:
                click.secho(f"Warning: Backup failed: {str(e)}", fg="yellow")
                if not click.confirm("Continue without backup?"):
                    click.echo("Configuration cancelled.")
                    return
        
        # Apply configuration
        click.echo("\nApplying NMN_ISOLATION ACL configuration...")
        
        config_result = online_hosts.run(
            send_config,
            config=config_string,
        )
        
        # Report results
        success_count = 0
        for hostname, result in config_result.items():
            if not result.failed:
                click.echo(f"  ✓ {hostname}: Successfully applied NMN_ISOLATION ACL configuration")
                success_count += 1
            else:
                click.echo(f"  ✗ {hostname}: Failed - {result.exception}")
        
        click.echo(f"\nNMN_ISOLATION ACL configuration completed on {success_count}/{len(config_result)} switches.")
        click.echo("  Applied object-group ip address NMN_NCN")
        click.echo("  Applied access-list ip NMN_ISOLATION")
        
    except Exception as e:
        click.secho(f"Error generating configuration: {e}", fg="red")
        return
    finally:
        # Restore original logging level
        logging.getLogger().setLevel(old_level) 