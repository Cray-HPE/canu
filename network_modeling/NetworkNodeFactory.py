import logging

import ruamel.yaml
import yamale

from .NetworkNode import NetworkNode


yaml = ruamel.yaml.YAML()

log = logging.getLogger(__name__)


class NetworkNodeFactory:
    __class_singleton = None

    def __init__(
        self,
        hardware_schema,
        hardware_data,
        architecture_schema,
        architecture_data,
        architecture_version,
    ):
        if NetworkNodeFactory.__class_singleton is None:
            NetworkNodeFactory.__class_singleton = self

            # Validate JSON data against the schema
            self.__yaml_validate(hardware_schema, hardware_data)
            self.__yaml_validate(architecture_schema, architecture_data)

            # Load yaml data as JSON
            with open(hardware_data) as file:
                self.__hardware_data = yaml.load(file)
                # self.__hardware_data = yaml.load(file, Loader=yaml.FullLoader)
                self.__hardware_data = self.__hardware_data[
                    "network_hardware"
                ]  # TODO ?
            with open(architecture_data) as file:
                self.__architecture_data = yaml.load(file)
                # self.__architecture_data = yaml.load(file, Loader=yaml.FullLoader)

            # Perform any cleanup required
            self.__cleanup_hardware_port_speeds(self.__hardware_data)

            # Initialize
            self.__architecture_version = architecture_version
            self.__node_id = -1

            # Defensively validate data for architecture/hardware mismatches
            # NOTE: Arguably this should be done more lazily outside of __init__
            self.__validate_architecture_version(
                self.__architecture_data, architecture_version
            )
            self.__validate_model_definition(
                self.__hardware_data, self.__architecture_data, architecture_version
            )
            self.__validate_port_definitions(
                self.__hardware_data, self.__architecture_data, architecture_version
            )
        else:
            raise Exception("Cannot create more than one singleton NetworkNodeFactory")

    # For convenience to users the yamale schema allows port speeds as int or list.
    # Convert ints to lists here for consistency.
    def __cleanup_hardware_port_speeds(self, hardware_data):
        for component in hardware_data:
            for port in component["ports"]:
                if isinstance(port["speed"], int):
                    port["speed"] = [port["speed"]]

    # The requested architectural version must exist in the architectural definition
    def __validate_architecture_version(self, architecture_data, architecture_version):
        found = False
        for named_version in architecture_data:
            if named_version == architecture_version:
                found = True
                break

        if not found:
            raise Exception(
                "Error finding version {} in the architecture definition".format(
                    architecture_version
                )
            )

    # The model of a component used in the architecture MUST be a component model in the hardware.
    # This is used as the "primary key" to match up.
    def __validate_model_definition(
        self, hardware_data, architecture_data, architecture_version
    ):
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
                        arch_component["model"], arch_name
                    )
                )
                log.error(
                    "    Models in the architectural definition must be represented in the hardware definition"
                )
                raise Exception(
                    "Architecture model {} for {} not found in hardware data".format(
                        arch_component["model"], arch_name
                    )
                )

    # Port speeds listed in the architectural definition must actually exist on the hardware.
    def __validate_port_definitions(
        self, hardware_data, architecture_data, architecture_version
    ):
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
                        "Validation of {} architecture against hardware failed for speeds".format(
                            arch_model
                        )
                    )
                log.debug(
                    "Validated {} architecture against hardware for speeds".format(
                        arch_model
                    )
                )

    def __yaml_validate(self, schema_file, data_file):
        try:
            schema = yamale.make_schema(schema_file)
            data = yamale.make_data(data_file)
            yamale.validate(schema, data)
        except Exception as err:
            raise Exception(
                "Error validating {} with {}: {}".format(data_file, schema_file, err)
            )

    def __generate_node_id(self):
        self.__node_id += 1
        return self.__node_id

    @staticmethod
    def get_factory(**kwargs):
        if not NetworkNodeFactory.__class_singleton:
            NetworkNodeFactory(**kwargs)
        return NetworkNodeFactory.__class_singleton

    def generate_node(self, node_type):
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
                "Error finding node architecture definition {} in version {}".format(
                    node_type, version_name
                )
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
                "Error finding node hardware definition {} in hardware".format(
                    node_hardware
                )
            )

        # Create a Network Node object based on the above definitions
        node_id = self.__generate_node_id()
        node = NetworkNode(
            id=node_id, hardware=node_hardware, architecture=node_architecture
        )
        log.debug(
            "Successfully generated node {} of type {}".format(
                node_id, node.arch_type()
            )
        )

        return node
