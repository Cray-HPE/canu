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
"""CANU node list utility."""

import re


def validate_node_list(value):
    """Takes a list of node ranges and returns a formatted list.

    Example: storage1-3, returns a list of [storage001, storage002, storage003]

    Args:
        value: node list

    Returns:
        nodes: formatted list of nodes.

    Raises:
        Exception: If the node list is invalid.
    """
    if value is None:
        return []

    node_pattern = re.compile(r"^[a-zA-Z0-9_]+$")
    range_pattern = re.compile(r"^([a-zA-Z0-9_]+)-?(\d+)?$")

    nodes = []
    for item in value:
        item = item.strip().lower()
        if node_pattern.match(item):
            match = re.match(r"^([a-zA-Z]+)(\d+)$", item)
            if match:
                prefix, num = match.groups()
                nodes.append(item)
        elif range_match := range_pattern.match(item):
            start_node = range_match.group(1)
            end_num = range_match.group(2)
            start_prefix = "".join(filter(str.isalpha, start_node))
            start_num = (
                int(re.search(r"\d+", start_node).group()) if start_prefix else 0
            )
            if end_num:
                end_num = int(end_num)
                nodes.extend(
                    [f"{start_prefix}{i}" for i in range(start_num, end_num + 1)],
                )
            else:
                nodes.append(start_node)
        else:
            raise Exception(
                'Invalid node format. Use "NodeName" or "NodeName1-5" for ranges.',
            )
    return nodes
