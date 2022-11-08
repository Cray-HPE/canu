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

"""Retrieve hosts that are reachable via SSH."""
from nornir.core.filter import F
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping


def host_alive(nornir_object):
    """Return Nornir inventory with alive hosts.

    Args:
        nornir_object: Nornir object

    Returns:
        Nornir object with online hosts, and a list of unreachable hosts.
    """
    ping_check = nornir_object.run(task=tcp_ping)
    result_dictionary = ResultSerializer(ping_check)
    unreachable_hosts = []

    for hostname, result in result_dictionary.items():
        if result["tcp_ping"][22] is False:
            unreachable_hosts.append(hostname)
    online_hosts = nornir_object.filter(~F(name__in=unreachable_hosts))
    return (online_hosts, unreachable_hosts)
