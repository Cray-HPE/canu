import pytest
from .main import get_running_version
import requests

class FakeDevice:
    def __init__(self, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def send_command(self, *args, **kwargs):
        return [
            {
                'version': '15.7(3)M5',
                'rommon': 'System',
                'hostname': 'LANRTR01',
                'uptime': '1 year, 42 weeks, 4 days, 1 hour, 18 minutes',
                'uptime_years': '1',
                'uptime_weeks': '42',
                'uptime_days': '4',
                'uptime_hours': '1',
                'uptime_minutes': '18',
                'reload_reason': 'Reload Command',
                'running_image': 'c2951-universalk9-mz.SPA.157-3.M5.bin',
                'hardware': ['CISCO2951/K9'],
                'serial': ['FGL2014508V'],
                'config_register': '0x2102',
                'mac': [],
                'restarted': '10:48:48 GMT Fri Mar 6 2020'
            }
        ]


@pytest.fixture()
def mock_netmiko(monkeypatch):
    """Mock netmiko."""
    monkeypatch.setattr(requests, "get", FakeDevice)