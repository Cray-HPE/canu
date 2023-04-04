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
"""Test NetworkFactory in the model."""
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import pytest


def mock_yaml_validate(self, schema_file, data_file):
    """Mock method override for NetworkNodeFactory.__yaml_validate."""


def test_node_factory_no_hardware_schema():
    """Test exception handling when the hardware schema file is not found."""
    with pytest.raises(Exception) as e:
        NetworkNodeFactory(architecture_version="network_v2", hardware_schema="bad_hardware_schema")
    assert e.type == Exception
    assert "No such file or directory: \'bad_hardware_schema\'" in str(e)


def test_node_factory_no_hardware_data():
    """Test exception handling when the hardware data file is not found."""
    with pytest.raises(Exception) as e:
        NetworkNodeFactory(architecture_version="network_v2", hardware_data="bad_hardware_data")
    assert e.type == Exception
    assert "No such file or directory: \'bad_hardware_data\'" in str(e)


def test_node_factory_no_architecture_schema():
    """Test exception handling when the architecture schema file is not found."""
    with pytest.raises(Exception) as e:
        NetworkNodeFactory(architecture_version="network_v2", architecture_schema="bad_architecture_schema")
    assert e.type == Exception
    assert "No such file or directory: \'bad_architecture_schema\'" in str(e)


def test_node_factory_no_architecture_data():
    """Test exception handling when the hardware data file is not found."""
    with pytest.raises(Exception) as e:
        NetworkNodeFactory(architecture_version="network_v2", architecture_data="bad_architecture_data")
    assert e.type == Exception
    assert "No such file or directory: \'bad_architecture_data\'" in str(e)


def test_node_factory_bad_architecture_version():
    """Test exception handling when the architecture version is not found."""
    with pytest.raises(Exception) as e:
        NetworkNodeFactory(architecture_version="bad_version")
    assert e.type == Exception
    assert "Error finding version bad_version in the architecture definition" in str(e)


def test_node_factory_bad_model_definition(tmp_path, monkeypatch):
    """Test failure when architecture model is not found in the hardware model.

    Args:
        tmp_path: built-in Path
        monkeypatch: built-in patcher

    Specifically test the function NetworkNodeFactory.__validate_model_definition.
    The "model" is used a s key to match hardware and architecture.
    """
    monkeypatch.setattr(NetworkNodeFactory, "_NetworkNodeFactory__yaml_validate", mock_yaml_validate)

    test_data_dir = tmp_path / "test_node_factory"
    test_data_dir.mkdir()

    architecture_data = """
---
test_architecture:
  name: "Test Architecture"
  description: "Test Architecture Description"
  version: 999
  components:
    - name: "test_node_not_found"
      model: "test_model_not_found"
      connections:
        - name: "none"
          speed: 100
    """
    test_arch_file = test_data_dir / "test_architecture_file.yaml"
    test_arch_file.write_text(architecture_data)

    with pytest.raises(Exception) as e:
        # Uses default hardware definitions and mock bypass of schema
        NetworkNodeFactory(
            architecture_version="test_architecture",
            architecture_data=test_arch_file,
        )
    assert e.type == Exception
    assert "model test_model_not_found for test_node_not_found not found in hardware data" in str(e)


def test_node_factory_bad_port_definitions(tmp_path, monkeypatch):
    """Test failure when the architecture model specifies port speeds not available in hardware.

    Args:
        tmp_path: built-in Path
        monkeypatch: built-in patcher

    Specifically test the function NetworkNodeFactory.__validate_definitions_definition.
    """
    monkeypatch.setattr(NetworkNodeFactory, "_NetworkNodeFactory__yaml_validate", mock_yaml_validate)

    test_data_dir = tmp_path / "test_node_factory"
    test_data_dir.mkdir()

    architecture_data = """
---
test_architecture:
  name: "Test Architecture"
  description: "Test Architecture Description"
  version: 999
  components:
    - name: "Test Node"
      model: "test_node"
      connections:
        - name: "test_node_2"
          speed: 999
    - name: "Test Node 2"
      model: "test_node_2"
      connections:
        - name: "test_node"
          speed: 1
    """
    test_arch_file = test_data_dir / "test_architecture_file.yaml"
    test_arch_file.write_text(architecture_data)

    hardware_data = """
network_hardware:
  - name: "Test Node"
    vendor: "Test Node Vendor"
    type: "test_node_type"
    model: "test_node"
    ports:
      - count: 1
        speed: 1
        slot: "mgmt"
  - name: "Test Node 2"
    vendor: "Test Node 2 Vendor"
    type: "test_node_2_type"
    model: "test_node_2"
    ports:
      - count: 1
        speed: 1
        slot: "mgmt"
    """
    test_hw_file = test_data_dir / "test_hardware_file.yaml"
    test_hw_file.write_text(hardware_data)

    with pytest.raises(Exception) as e:
        # Mock bypass of schema
        NetworkNodeFactory(
            architecture_version="test_architecture",
            architecture_data=test_arch_file,
            hardware_data=test_hw_file,
        )
    assert e.type == Exception
    assert "Validation of test_node architecture against hardware failed for speeds" in str(e)
