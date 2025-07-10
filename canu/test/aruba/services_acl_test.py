# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""parse aruba mgmt ACL config for Services ACLs."""


def services_acl(result, vlan_ips=None, vrf=None, mtn_acls=None, services_acl=None):
    """Verify services ACLs on the switch.

    Args:
        result: show access-list ip nmn-hmn command
        vlan_ips: None
        vrf: None
        mtn_acls: rendered ACLs for MTN cabinets
        services_acl: rendered acls for Services

    Returns:
        Pass or fail
    """
    running_acls = str(result)

    exception = None
    result = "PASS"
    success = True

    # Comparing the rendered Services ACLs
    required_services_acls = []
    for required_acl in services_acl.splitlines():
        if required_acl == "":
            continue
        for string in ["comment", "permit", "deny"]:
            index = required_acl.find(string)
            if index != -1:
                required_services_acls.append(required_acl[index:])

    total_required_services_acls = len(required_services_acls)

    found_acls = 0
    for required_acl in required_services_acls:
        if running_acls.find(required_acl) != -1:
            found_acls += 1

    if found_acls < total_required_services_acls:
        exception = f"Only {found_acls} of the required {total_required_services_acls} ACLs found to isolate services"
        result = "FAIL"
        success = False

    return {
        "exception": exception,
        "result": result,
        "success": success,
    }
