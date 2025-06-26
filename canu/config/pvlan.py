# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""CANU config PVLAN commands."""
import json
import logging
from datetime import datetime

import click
import click_spinner
from nornir import InitNornir
from nornir.core.filter import F
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping
from nornir_scrapli.tasks import send_command, send_config

from canu.backup.network.network import backup_switches
from canu.generate.switch.config.config import generate_switch_config, parse_sls_for_config
from canu.utils.inventory import inventory
from canu.validate.paddle.paddle import node_model_from_paddle
from network_modeling.NetworkNodeFactory import NetworkNodeFactory

# Backup function is now imported from canu.backup.network.network


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
    "--private-vlan",
    required=True,
    type=int,
    help="Private VLAN ID to create (e.g., 2800)",
)
@click.option(
    "--name",
    default="NMN_PRIVATE_VLAN",
    show_default=True,
    help="Name for the VLAN",
)
@click.option(
    "--primary-vlan",
    type=int,
    default=2,
    show_default=True,
    help="Primary VLAN ID for private VLAN",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.option(
    "--reconfigure-ports",
    is_flag=True,
    help="Reconfigure switch ports for private VLAN (requires --private-vlan and CCJ/SHCD input)",
    default=False,
)
@click.option(
    "--ccj",
    help="Paddle CCJ file (required for --reconfigure-ports)",
    type=click.File("rb"),
)
@click.option(
    "--csm",
    help="CSM version (required for --reconfigure-ports)",
    type=click.Choice(["1.0", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"]),
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
    help="CSM architecture (required for --reconfigure-ports)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show generated configuration without applying it to switches",
    default=False,
)
@click.option(
    "--switch",
    help="Target specific switch(es) by hostname or IP address. "
    "Can be used multiple times (e.g., --switch sw-spine-001 --switch 10.254.0.4)",
    type=str,
    multiple=True,
)
@click.option(
    "--remove-private-vlan",
    is_flag=True,
    help="Remove private VLAN configuration from switches",
    default=False,
)
@click.pass_context
def pvlan(
    ctx,
    username,
    password,
    sls_file,
    sls_address,
    network,
    log_,
    private_vlan,
    name,
    primary_vlan,
    reconfigure_ports,
    ccj,
    csm,
    architecture,
    dry_run,
    switch,
    remove_private_vlan,
):
    """Configure PVLAN (VLAN) on network switches.

    This command can create basic VLANs, configure private VLANs, and optionally
    reconfigure ports for private VLAN isolation.

    Basic VLAN creation (all switches):
        canu config pvlan --vlan 2800 --name "test_vlan"

    Private VLAN isolated type (spine, leaf, leaf-bmc switches):
        canu config pvlan --vlan 2770 --private-vlan

    Private VLAN with port reconfiguration (retroactive setup):
        canu config pvlan --vlan 2770 --private-vlan --reconfigure-ports --ccj ./ccj.json --csm 1.7 --architecture full

    Dry run to preview configuration without applying:
        canu config pvlan --vlan 2770 --private-vlan --reconfigure-ports --ccj ./ccj.json --csm 1.7 --architecture full --dry-run

    Target specific switch(es):
        canu config pvlan --vlan 2770 --private-vlan --switch sw-spine-001
        canu config pvlan --vlan 2770 --private-vlan --switch sw-spine-001 --switch sw-spine-002
        canu config pvlan --vlan 2770 --private-vlan --switch 10.254.0.4

    Remove private VLAN configuration:
        canu config pvlan --vlan 2770 --remove-private-vlan --switch sw-spine-001
        canu config pvlan --vlan 2770 --remove-private-vlan (removes from all switches)

    Private VLAN setup applies to all switches except edge and CDU switches.
    Port reconfiguration identifies node types and configures:
    - Compute/application nodes: isolated VLAN with secondary port type
    - NCN nodes: promiscuous port type
    - Uplink ports: add isolated VLAN to trunk allowed lists

    Args:
        ctx: CANU context settings
        username: Switch username
        password: Switch password
        sls_file: JSON file containing SLS data
        sls_address: The address of SLS
        network: The network that is used to connect to the switches
        log_: Enable logging
        name: Name for the VLAN
        private_vlan: Configure as private VLAN isolated type (applies to spine, leaf, leaf-bmc)
        primary_vlan: Primary VLAN ID for private VLAN
        reconfigure_ports: Reconfigure switch ports for private VLAN
        ccj: Paddle CCJ file for port reconfiguration
        csm: CSM version for port reconfiguration
        architecture: CSM architecture for port reconfiguration
        dry_run: Show generated configuration without applying it
        switch: Target specific switch(es) by hostname or IP address
        remove_private_vlan: Remove private VLAN configuration from switches
    """
    if not password and not dry_run and not remove_private_vlan:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )
    elif not password and remove_private_vlan:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )

    # Validate mutually exclusive options
    if remove_private_vlan and reconfigure_ports:
        click.secho(
            "--remove-private-vlan and --reconfigure-ports cannot be used together",
            fg="red",
        )
        return

    # Validate port reconfiguration options
    if reconfigure_ports:

        if not ccj:
            click.secho("--reconfigure-ports requires --ccj", fg="red")
            return

        if not csm:
            click.secho("--reconfigure-ports requires --csm", fg="red")
            return

        if not architecture:
            click.secho("--reconfigure-ports requires --architecture", fg="red")
            return

        if not sls_file:
            click.secho("--reconfigure-ports requires --sls-file", fg="red")
            return

    # Set to ERROR otherwise nornir plugin logs debug messages to the screen
    logging.basicConfig(level="ERROR")

    if remove_private_vlan:
        click.echo("Removing private VLAN configuration...")
        click.echo(f"  Isolated VLAN: {private_vlan}")
        click.echo(f"  Primary VLAN: {primary_vlan}")
        click.echo("  This will remove private VLAN settings and restore standard VLAN configuration")
    else:
        click.echo("Configuring private VLAN isolated type...")
        click.echo(f"  VLAN: {private_vlan}")
        click.echo(f"  Primary VLAN: {primary_vlan}")
        click.echo(f"  Name: {name}")

    # Build Nornir inventory (needed for remove_private_vlan and non-dry-run operations)
    # Skip inventory only for dry-run removal without SLS file
    if (
        (not dry_run)
        or (dry_run and reconfigure_ports and not remove_private_vlan)
        or (dry_run and remove_private_vlan and sls_file)
        or (dry_run and sls_file and not remove_private_vlan)  # Basic dry-run with SLS file
    ):
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

        # Filter switches based on options
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
                click.secho(
                    f"Warning: Switch(es) not found: {', '.join(missing_switches)}",
                    fg="yellow",
                )

            nr = target_hosts
        else:
            # For private VLAN, apply to all switches except edge and CDU switches
            filtered_hosts = nr.filter(lambda host: not any(x in host.name.lower() for x in ["edge", "cdu"]))
            if not filtered_hosts.inventory.hosts:
                click.secho(
                    "No compatible switches found in inventory (excluding edge and CDU switches)",
                    fg="red",
                )
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
    else:
        # For dry-run with reconfigure-ports, we don't need actual switch connectivity
        online_hosts = None

    # Handle private VLAN removal
    if remove_private_vlan:
        if dry_run and not sls_file:
            click.secho("Dry-run removal requires --sls-file to identify switches", fg="red")
            click.secho("Example: --sls-file /path/to/sls_input_file.json", fg="yellow")
            return

        if not online_hosts or not online_hosts.inventory.hosts:
            click.secho("No switches available for private VLAN removal", fg="red")
            return

        click.echo("Analyzing current private VLAN configuration...")

        # Get current running config from switches to identify ports with private VLAN config
        aruba_hosts = online_hosts.filter(platform="aruba_aoscx")
        if not aruba_hosts.inventory.hosts:
            click.secho(
                "No Aruba switches found. Private VLAN removal currently supports Aruba switches only.",
                fg="yellow",
            )
            return

        # Backup configurations before making changes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = f"switch_backup_{timestamp}"

        click.echo(f"Creating backup in {backup_folder}/...")
        with click_spinner.spinner():
            try:
                saved_files = backup_switches(aruba_hosts, backup_folder)
                click.echo(f"✓ Backed up {len(saved_files)} switch configurations")
                if saved_files:
                    click.echo(f"  Backup location: ./{backup_folder}/")
                    click.echo(f"  Files: {', '.join(saved_files)}")
            except Exception as e:
                click.secho(f"Warning: Backup failed: {str(e)}", fg="yellow")
                if not click.confirm("Continue without backup?"):
                    click.echo("Operation cancelled.")
                    return

        # Get current configuration to identify private VLAN ports
        click.echo("Retrieving current switch configurations...")
        with click_spinner.spinner():
            config_results = aruba_hosts.run(
                task=send_command,
                command="show running-config",
            )

        # Analyze configurations and generate removal commands
        removal_commands = {}
        for hostname, result in config_results.items():
            if result.failed:
                click.secho(f"Warning: Could not retrieve config from {hostname}", fg="yellow")
                continue

            config = result[0].result
            commands = []

            # Parse configuration to find private VLAN settings
            lines = config.split("\n")
            current_interface = None
            private_vlan_secondary_ports = []  # Ports with secondary port-type (compute nodes)
            private_vlan_promiscuous_ports = []  # Ports with promiscuous port-type (NCN nodes)

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Track current interface
                if line.startswith("interface "):
                    current_interface = line.replace("interface ", "")
                    i += 1
                    continue

                # Look for any private-vlan port-type configuration
                if current_interface and "private-vlan port-type" in line:
                    if "secondary" in line:
                        private_vlan_secondary_ports.append(current_interface)
                    elif "promiscuous" in line:
                        private_vlan_promiscuous_ports.append(current_interface)

                i += 1

            # Generate removal commands
            if private_vlan_secondary_ports or private_vlan_promiscuous_ports:
                # Remove isolated VLAN (only if it exists)
                commands.append(f"no vlan {private_vlan}")

                # Fix secondary ports (compute nodes) - restore to primary VLAN
                for port in private_vlan_secondary_ports:
                    commands.extend(
                        [
                            f"interface {port}",
                            "    no private-vlan port-type secondary",
                            f"    vlan access {primary_vlan}",
                        ],
                    )

                # Fix promiscuous ports (NCN nodes) - just remove the port-type
                for port in private_vlan_promiscuous_ports:
                    commands.extend(
                        [
                            f"interface {port}",
                            "    no private-vlan port-type promiscuous",
                        ],
                    )

                # Remove private-vlan primary from primary VLAN
                commands.extend(
                    [
                        f"vlan {primary_vlan}",
                        "    no private-vlan primary",
                    ],
                )

                removal_commands[hostname] = commands

        if not removal_commands:
            click.echo("No private VLAN configuration found to remove.")
            return

        # Display what will be removed
        click.echo("\nPrivate VLAN removal commands:")
        click.echo("=" * 50)
        for hostname, commands in removal_commands.items():
            click.echo(f"\n{hostname}:")
            for cmd in commands:
                click.echo(f"  {cmd}")
        click.echo("=" * 50)

        if not click.confirm("\nDo you want to proceed with removing the private VLAN configuration?"):
            click.echo("Operation cancelled.")
            return

        # Apply removal commands
        click.echo("Removing private VLAN configuration...")
        with click_spinner.spinner():
            removal_results = {}

            for hostname in removal_commands:
                commands_string = "\n".join(removal_commands[hostname])
                single_host = aruba_hosts.filter(name=hostname)
                result = single_host.run(
                    task=send_config,
                    config=commands_string,
                )
                removal_results[hostname] = result[hostname]

        # Display results
        click.echo("\nRemoval Results:")
        click.echo("=" * 50)

        success_count = 0
        for hostname, result in removal_results.items():
            if result.failed:
                click.secho(f"✗ {hostname}: FAILED", fg="red")
                if hasattr(result[0], "result") and result[0].result:
                    click.secho(f"  Error: {result[0].result}", fg="red")
            else:
                click.secho(f"✓ {hostname}: SUCCESS", fg="green")
                if hostname in removal_commands:
                    secondary_ports = len(
                        [cmd for cmd in removal_commands[hostname] if "no private-vlan port-type secondary" in cmd],
                    )
                    promiscuous_ports = len(
                        [cmd for cmd in removal_commands[hostname] if "no private-vlan port-type promiscuous" in cmd],
                    )

                    click.echo(f"  Removed private VLAN {private_vlan}")
                    if secondary_ports > 0:
                        click.echo(f"  Restored {secondary_ports} secondary ports to VLAN {primary_vlan}")
                    if promiscuous_ports > 0:
                        click.echo(f"  Removed promiscuous port-type from {promiscuous_ports} ports")
                    click.echo(f"  Removed private-vlan primary from VLAN {primary_vlan}")
                success_count += 1

        click.echo(f"\nPrivate VLAN removal completed on {success_count}/{len(removal_results)} switches.")
        return

    # Add port reconfiguration if requested
    port_configs = {}  # Dictionary to store per-switch port configurations
    base_vlan_configs = set()  # Store unique VLAN configurations from templates

    if reconfigure_ports and private_vlan:
        click.echo("Analyzing network topology for port reconfiguration...")

        # Parse input data (same logic as config generation)
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
        try:
            sls_file.seek(0)  # Reset file pointer
            input_json = json.load(sls_file)
            sls_json = [network[x] for network in [input_json.get("Networks", {})] for x in network]
            sls_variables = parse_sls_for_config(sls_json)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho("Invalid SLS JSON format", fg="red")
            return

        # Generate port configurations for each switch
        if switch:
            # If targeting specific switches, only process those
            switch_names = list(switch)
        elif online_hosts and online_hosts.inventory.hosts:
            switch_names = [host.name for host in online_hosts.inventory.hosts.values()]
        else:
            # For dry-run mode, extract actual switch names from network topology data
            switch_names = []
            for node in network_node_list:
                node_data = node.serialize()
                node_name = node_data.get("common_name", "")
                # Only include switches, skip compute nodes and other devices
                if node_name and any(x in node_name.lower() for x in ["sw-spine", "sw-leaf"]):
                    if node_name not in switch_names:
                        switch_names.append(node_name)

        for switch_name in switch_names:
            if any(x in switch_name.lower() for x in ["edge", "cdu"]):
                continue  # Skip edge and CDU switches

            switch_config = []

            # Use existing template system to generate full config, then extract private VLAN parts
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
                    nmn_pvlan=private_vlan,  # This enables private VLAN in templates
                )

                # Extract only private VLAN related configuration from the generated config
                switch_config = []
                lines = full_config.split("\n")
                i = 0
                while i < len(lines):
                    line = lines[i].strip()

                    # Look for VLAN configurations (including primary VLAN setup)
                    if line.startswith("vlan "):
                        vlan_config = [line]
                        i += 1

                        # Collect all lines for this VLAN
                        while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
                            if lines[i].strip():
                                vlan_config.append(lines[i])
                            i += 1

                        # Check if this VLAN has private VLAN configuration
                        has_pvlan_primary = any("private-vlan primary" in config_line for config_line in vlan_config)
                        has_pvlan_isolated = any("private-vlan isolated" in config_line for config_line in vlan_config)

                        if has_pvlan_primary or has_pvlan_isolated:
                            # Only include private VLAN specific lines, not ACLs or other configuration
                            filtered_vlan_config = [vlan_config[0]]  # Keep the "vlan X" line
                            for config_line in vlan_config[1:]:
                                if "private-vlan primary" in config_line or "private-vlan isolated" in config_line:
                                    filtered_vlan_config.append(config_line)

                            # Store filtered VLAN configuration for base config (will be deduplicated by set)
                            vlan_config_str = "\n".join(filtered_vlan_config)
                            base_vlan_configs.add(vlan_config_str)
                        continue

                    # Look for interface configurations
                    elif line.startswith("interface "):
                        interface_name = line.replace("interface ", "")
                        interface_config = [line]
                        i += 1

                        # Collect all lines for this interface
                        while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
                            if lines[i].strip():
                                interface_config.append(lines[i])
                            i += 1

                        # Check if this interface has private VLAN configuration
                        has_pvlan_config = any("private-vlan" in config_line for config_line in interface_config)
                        has_vlan_access = any(
                            f"vlan access {private_vlan}" in config_line for config_line in interface_config
                        )
                        has_trunk_allowed = any(
                            f"vlan trunk allowed" in config_line and str(private_vlan) in config_line
                            for config_line in interface_config
                        )

                        if has_pvlan_config or has_vlan_access or has_trunk_allowed:
                            # Extract only the private VLAN related lines
                            switch_config.append(f"interface {interface_name}")
                            for config_line in interface_config[1:]:  # Skip the interface line itself
                                if (
                                    "private-vlan" in config_line
                                    or f"vlan access {private_vlan}" in config_line
                                    or ("vlan trunk allowed" in config_line and str(private_vlan) in config_line)
                                ):
                                    # Remove existing VLAN access commands, we will add the correct one
                                    interface_config = [
                                        line for line in interface_config if not line.strip().startswith("vlan access")
                                    ]

                                    # Add the private VLAN access command
                                    interface_config.append(f"    vlan access {private_vlan}")
                                    switch_config.extend(interface_config)
                        continue

                    i += 1

                if switch_config:
                    port_configs[switch_name] = switch_config

            except Exception as e:
                if log_:
                    click.secho(f"Error generating config for {switch_name}: {e}", fg="yellow")
                continue

    # Build base configuration from template-generated VLAN configs or basic private VLAN config
    if base_vlan_configs:
        config_string = "\n".join(sorted(base_vlan_configs))
    else:
        # Generate basic private VLAN configuration when not using port reconfiguration
        config_string = f"""vlan {primary_vlan}
    private-vlan primary
vlan {private_vlan}
    private-vlan isolated {primary_vlan}
    name {name}"""

    if dry_run:
        click.echo("DRY RUN MODE - Configuration will NOT be applied to switches")
        click.echo("=" * 70)

    if switch:
        switch_count = len(switch)
        if switch_count == 1:
            switch_desc = f"switch '{switch[0]}'"
        else:
            switch_desc = f"{switch_count} switches ({', '.join(switch)})"
    else:
        switch_count = (
            len(online_hosts.inventory.hosts)
            if online_hosts and online_hosts.inventory.hosts
            else len(port_configs) if port_configs else 0
        )
        switch_desc = f"{switch_count} switches"

    if dry_run:
        click.echo(f"Generated configuration for {switch_desc}:")
    else:
        click.echo(f"Applying configuration to {switch_desc}...")

    if private_vlan and reconfigure_ports:
        click.echo("\nPrivate VLAN and port reconfiguration:")
    elif private_vlan:
        click.echo("\nPrivate VLAN isolated configuration:")
    else:
        click.echo("\nVLAN configuration:")
    click.echo("=" * 50)
    click.echo("Base VLAN configuration (applied to all switches):")
    click.echo(config_string)

    # Show per-switch port configurations if any
    if port_configs:
        click.echo("\nPer-switch port configurations:")
        for switch_name, switch_config in port_configs.items():
            click.echo(f"\n{switch_name}:")
            for line in switch_config:
                click.echo(f"  {line}")

    click.echo("=" * 50)

    if dry_run:
        click.echo("\nDRY RUN COMPLETE - No changes were applied to switches")
        if private_vlan and reconfigure_ports:
            click.echo("To apply this configuration, run the same command without --dry-run")
        return

    if not click.confirm("Do you want to proceed with this configuration?"):
        click.echo("Configuration cancelled.")
        return

    # Create timestamped backup folder and backup configurations
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"switch_backup_{timestamp}"

    click.echo(f"Creating backup in {backup_folder}/...")
    with click_spinner.spinner():
        try:
            saved_files = backup_switches(online_hosts, backup_folder)
            click.echo(f"✓ Backed up {len(saved_files)} switch configurations")
            if saved_files:
                click.echo(f"  Backup location: ./{backup_folder}/")
                click.echo(f"  Files: {', '.join(saved_files)}")
        except Exception as e:
            click.secho(f"Warning: Backup failed: {str(e)}", fg="yellow")
            if not click.confirm("Continue without backup?"):
                click.echo("Configuration cancelled.")
                return

    click.echo("Applying configuration...")
    with click_spinner.spinner():
        # Apply configuration only to Aruba switches (using scrapli)
        aruba_hosts = online_hosts.filter(platform="aruba_aoscx")

        if aruba_hosts.inventory.hosts:
            # Apply base VLAN configuration to all switches
            config_results = aruba_hosts.run(
                task=send_config,
                config=config_string,
            )

            # Apply per-switch port configurations
            if port_configs:
                for hostname in aruba_hosts.inventory.hosts:
                    if hostname in port_configs:
                        switch_config_string = "\n".join(port_configs[hostname])
                        single_host = aruba_hosts.filter(name=hostname)
                        port_results = single_host.run(
                            task=send_config,
                            config=switch_config_string,
                        )
                        # Merge results
                        if hostname in config_results:
                            config_results[hostname].extend(port_results[hostname])
                        else:
                            config_results[hostname] = port_results[hostname]

            # Display results
            click.echo("\nConfiguration Results:")
            click.echo("=" * 50)

            for hostname, result in config_results.items():
                if result.failed:
                    click.secho(f"✗ {hostname}: FAILED", fg="red")
                    if hasattr(result[0], "result") and result[0].result:
                        click.secho(f"  Error: {result[0].result}", fg="red")
                else:
                    click.secho(f"✓ {hostname}: SUCCESS", fg="green")
                    if private_vlan and reconfigure_ports:
                        click.echo(f"  Private VLAN {private_vlan} configured as isolated type")
                        click.echo(f"  Primary VLAN: {primary_vlan}")
                        click.echo(f"  Name: {name}")
                        if hostname in port_configs:
                            port_count = len([line for line in port_configs[hostname] if line.startswith("interface")])
                            click.echo(f"  Reconfigured {port_count} ports for private VLAN")
                    elif private_vlan:
                        click.echo(f"  Private VLAN {private_vlan} configured as isolated type")
                        click.echo(f"  Primary VLAN: {primary_vlan}")
                        click.echo(f"  Name: {name}")
                    else:
                        click.echo(f"  VLAN {private_vlan} configured with name '{name}'")

        # Handle non-Aruba switches
        non_aruba_hosts = online_hosts.filter(~F(platform="aruba_aoscx"))
        if non_aruba_hosts.inventory.hosts:
            click.secho(
                f"\nSkipped {len(non_aruba_hosts.inventory.hosts)} non-Aruba switches:",
                fg="yellow",
            )
            for hostname in non_aruba_hosts.inventory.hosts:
                platform = non_aruba_hosts.inventory.hosts[hostname].platform
                click.secho(f"  - {hostname} ({platform})", fg="yellow")
            click.secho(
                "Note: This command currently only supports Aruba AOS-CX switches.",
                fg="yellow",
            )

    if private_vlan and reconfigure_ports:
        click.echo(f"\nPrivate VLAN {private_vlan} configuration and port reconfiguration completed.")
        click.echo("Compute and application nodes are now isolated using secondary port types.")
        click.echo("NCN nodes can communicate with all systems using promiscuous port types.")
    elif private_vlan:
        click.echo(f"\nPrivate VLAN {private_vlan} configuration completed.")
    else:
        click.echo(f"\nVLAN {private_vlan} configuration completed.")
