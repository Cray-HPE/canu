"""parse aruba ip route output and return pass or fail."""
from ntc_templates.parse import parse_output


def run(result):
    """Test TFTP route.

    Args:
        result: show ip route all-vrfs output

    Returns:
        Pass or fail
    """
    routes = str(result)
    result_parsed = (
        parse_output(
            platform="aruba_aoscx",
            command="show ip route all-vrfs",
            data=routes,
        ),
    )
    for route in result_parsed:
        if route["ip"] == "10.92.100.60/32" and len(route["iface"]) > 1:
            return {
                "exception": "Multiple Routes to tftp server",
                "result": "FAIL",
                "success": False,
            }
