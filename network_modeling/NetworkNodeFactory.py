# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""NetworkNodeFactory to create a new network."""
import json
import logging
from os import path
from pathlib import Path
import re
import sys

import click
import jsonschema
from ruamel.yaml import YAML
import yamale

from .NetworkNode import NetworkNode


yaml = YAML()

log = logging.getLogger(__name__)

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent

# Schema and Data files
default_hardware_schema_file = path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-hardware-schema.yaml",
)
default_hardware_spec_file = path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-hardware.yaml",
)
default_architecture_schema_file = path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-architecture-schema.yaml",
)
default_architecture_spec_file = path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-architecture.yaml",
)
default_paddle_schema_file = path.join(
    project_root,
    "network_modeling",
    "schema",
    "paddle-schema.json",
)


class NetworkNodeFactory:
    """A class to create a new network.

    Attributes
    ----------
    hardware_schema :

    hardware_data :

    architecture_schema :

    architecture_data :

    architecture_version :


    Methods
    -------
    generate_node(node_type):
        Generate a new network node.
    lookup_mapper():
        Convert architecture yaml data to tuple.
    generate_node_from_paddle(ccj_node):
        Generate a new network node from paddle.
    validate_paddle(schema):
        Validate JSON
    """

    def __init__(
        self,
        architecture_version,
        hardware_schema=default_hardware_schema_file,
        hardware_data=default_hardware_spec_file,
        architecture_schema=default_architecture_schema_file,
        architecture_data=default_architecture_spec_file,
    ):
        """
        Construct the necessary attributes for the network factory object.

        Args:
            hardware_schema : hardware_schema
            hardware_data : hardware_data
            architecture_schema : architecture_schema
            architecture_data : architecture_data
            architecture_version : architecture_version
        """
        # Validate JSON data against the schema
        self.__yaml_validate(hardware_schema, hardware_data)
        self.__yaml_validate(architecture_schema, architecture_data)

        # Load yaml data as JSON
        with open(hardware_data) as file:
            self.__hardware_data = yaml.load(file)
            self.__hardware_data = self.__hardware_data["network_hardware"]  # TODO ?
        with open(architecture_data) as file:
            self.__architecture_data = yaml.load(file)

        # Perform any cleanup required
        self.__cleanup_hardware_port_speeds()

        # Initialize
        self.__architecture_version = architecture_version
        self.__node_id = -1

        # Defensively validate data for architecture/hardware mismatches
        # NOTE: Arguably this should be done more lazily outside of __init__
        self.__validate_architecture_version()
        self.__validate_model_definition()
        self.__validate_port_definitions()
        self.__validate_lookup_mapper()

        self.__warn_architecture_deprecation()

    def __yaml_validate(self, schema_file, data_file):
        try:
            schema = yamale.make_schema(schema_file)
            data = yamale.make_data(data_file)
            yamale.validate(schema, data)
        except Exception as err:
            raise Exception(
                f"{__name__}: Error validating {data_file} with {schema_file}: {err}",
            ) from err

    # For convenience to users the yamale schema allows port speeds as int or list.
    # Convert integers to lists here for consistency.
    def __cleanup_hardware_port_speeds(self):
        for component in self.__hardware_data:
            for port in component["ports"]:
                if isinstance(port["speed"], int):
                    port["speed"] = [port["speed"]]

    # The requested architectural version must exist in the architectural definition
    def __validate_architecture_version(self):
        architecture_data = self.__architecture_data
        architecture_version = self.__architecture_version
        found = False
        for named_version in architecture_data:
            if named_version == architecture_version:
                found = True
                break
        if not found:
            raise Exception(
                f"{__name__}: Error finding version {architecture_version} in the architecture definition",
            )
        log.debug(f"Using architecture version: {architecture_version}")

    # The model of a component used in the architecture MUST be a component model in the hardware.
    # This is used as the "primary key" to match up.
    def __validate_model_definition(self):
        hardware_data = self.__hardware_data
        architecture_data = self.__architecture_data
        architecture_version = self.__architecture_version
        hw_models = []
        hw_ports_by_model = []
        for component in hardware_data:
            hw_models.append(component["model"])
            hw_ports_by_model.append(component["ports"])

        for arch_component in architecture_data[architecture_version]["components"]:
            arch_name = arch_component["name"]
            arch_model = arch_component["model"]
            if arch_model not in hw_models:
                log.error(
                    "Architecture model {} for {} not found in hardware data".format(
                        arch_component["model"],
                        arch_name,
                    ),
                )
                log.error(
                    "    Models in the architectural definition must be represented in the hardware definition",
                )
                raise Exception(
                    f"{__name__}: Architecture model {arch_component['model']} for {arch_name} not found in hardware data",
                )

    # Port speeds listed in the architectural definition must actually exist on the hardware.
    def __validate_port_definitions(self):
        architecture_data = self.__architecture_data
        architecture_version = self.__architecture_version
        hardware_data = self.__hardware_data
        for arch_component in architecture_data[architecture_version]["components"]:
            arch_model = arch_component["model"]
            arch_connections = arch_component["connections"]

            for hw_component in hardware_data:
                hw_model = hw_component["model"]
                hw_connections = hw_component["ports"]

                if hw_model != arch_model:
                    continue

                # Now see if the arch defined speeds are allowed by the hardware
                found = False
                for arch_conn in arch_connections:
                    for hw_conn in hw_connections:
                        if arch_conn["speed"] in hw_conn["speed"]:
                            found = True
                            break

                if not found:
                    raise Exception(
                        f"{__name__}: Validation of {arch_model} architecture against hardware failed for speeds",
                    )
                log.debug(
                    f"Validated {arch_model} architecture against hardware for speeds",
                )

    def __validate_lookup_mapper(self):
        version = self.__architecture_version
        components = self.__architecture_data[version]["components"]
        lookup_mapper = self.__architecture_data[version]["lookup_mapper"]
        found = False
        # Ensure that all mapped devices actually have an architectural component definition
        for lookup in lookup_mapper:
            lookup_type = lookup["architecture_type"]
            # If there is a regex key, then we need to check for a match
            if "regex" in lookup:
                regex_search = True
            else:
                regex_search = False
            for component in components:
                if regex_search:
                    for pattern in lookup["lookup_name"]:
                        # check each pattern against the component name
                        if not bool(re.search(pattern, lookup_type)):
                            continue
                        found = True
                        break
                else:
                    if component["name"] != lookup_type:
                        continue
                    found = True
                    break
            if not found:
                raise Exception(
                    f"{__name__}: Device {lookup_type} in lookup_mapper not found in architecture components",
                )
            log.debug(
                f"Validated lookup_mapper device {lookup_type} in architecture definition",
            )

    def __warn_architecture_deprecation(self):
        architecture_data = self.__architecture_data
        architecture_version = self.__architecture_version
        name = architecture_data[architecture_version]["name"]
        if "deprecated" in architecture_data[architecture_version]:
            log.warning(f"Architecture {name} is deprecated")

    def __generate_node_id(self):
        self.__node_id += 1
        return self.__node_id

    def generate_node(self, node_type):
        """Generate a new network node."""
        version_name = self.__architecture_version

        # Start by finding the architectural definition
        # TODO:  Remove this section - it's already in a check but this should be
        # unnecessary if we pointed to the correct arch version in __init__
        architecture_data = self.__architecture_data
        node_architecture = None
        for k, v in architecture_data.items():
            if k == version_name:
                for component in v["components"]:
                    if component["name"] == node_type:
                        node_architecture = component
        if node_architecture is None:
            raise Exception(
                f"{__name__}: Error finding node architecture definition {node_type} in version {version_name}",
            )

        # The architectural "model" is the "primary key" for hardware
        model = node_architecture["model"]

        # Find the hardware definition based on model
        hardware_data = self.__hardware_data
        node_hardware = None
        for v in hardware_data:
            if v["model"] == model:
                node_hardware = v
        if node_hardware is None:
            raise Exception(
                f"{__name__}: Error finding node hardware definition {node_hardware} in hardware",
            )

        # Create a Network Node object based on the above definitions
        node_id = self.__generate_node_id()
        node = NetworkNode(
            id=node_id,
            hardware=node_hardware,
            architecture=node_architecture,
        )
        log.debug(
            "Successfully generated node {} of type {}".format(
                node_id,
                node.arch_type(),
            ),
        )

        return node

    def generate_node_from_paddle(self, ccj_node):
        """Generate a new network node from paddle."""
        common_name = ccj_node["common_name"]
        self.__node_id = ccj_node["id"]
        node_architecture_type = ccj_node["architecture"]
        model = ccj_node["model"]
        node_type = ccj_node["type"]

        # The architectural "model" is the "primary key" for hardware
        node_architecture = None
        components = self.__architecture_data[self.__architecture_version]["components"]
        for component in components:
            if component["name"] == node_architecture_type:
                node_architecture = component
        if node_architecture is None:
            raise Exception(
                f"{__name__}: Error finding node architecture definition {node_type} in version {self.__architecture_version}",
            )

        # Find the hardware definition based on model
        node_hardware = None
        for hardware_definition in self.__hardware_data:
            if hardware_definition["model"] == model:
                node_hardware = hardware_definition
        if node_hardware is None:
            raise Exception(
                f"{__name__}: Error finding node hardware definition {node_hardware} in hardware",
            )

        # Create a Network Node object based on the above definitions
        node = NetworkNode(
            id=self.__node_id,
            hardware=node_hardware,
            architecture=node_architecture,
        )
        log.debug(
            f"Successfully generated node {self.__node_id} of type {node.arch_type()}",
        )

        node.common_name(common_name)
        return node

    # In the future SHCD and device names should match Shasta naming, but for now
    # there is a map required.  Convert architecture yaml data to tuple.
    def lookup_mapper(self):
        """Convert architecture yaml data to tuple."""
        lookup_mapper = self.__architecture_data[self.__architecture_version][
            "lookup_mapper"
        ]
        lookup_mapper_as_tuple = []
        for lookup in lookup_mapper:
            lookup_mapper_as_tuple.append(
                (
                    lookup["lookup_name"] + [lookup["shasta_name"]],
                    lookup["shasta_name"],
                    lookup["architecture_type"],
                ),
            )
        return lookup_mapper_as_tuple

    def validate_paddle(self, ccj_json, ccj_schema_file=default_paddle_schema_file):
        """Validate that the CCJ works and passes schema validation checks."""
        with open(ccj_schema_file, "r") as file:
            ccj_schema = json.load(file)

        validator = jsonschema.Draft7Validator(ccj_schema)

        try:
            validator.check_schema(ccj_schema)
        except jsonschema.exceptions.SchemaError as err:
            click.secho(
                f"Schema {ccj_schema} is invalid: {[x.message for x in err.context]}\n"
                + "Cannot generate and write Topology JSON file.",
                fg="red",
            )
            sys.exit(1)

        errors = sorted(validator.iter_errors(ccj_json), key=str)

        if errors:
            click.secho("CCJ failed schema checks:", fg="red")
            for error in errors:
                click.secho(f"    {error.message}", fg="red")
            sys.exit(1)
