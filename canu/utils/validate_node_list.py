import click
import re


def validate_node_list(ctx, param, value):
    if value is None:
        return []

    node_pattern = re.compile(r"^[a-zA-Z0-9_]+$")
    range_pattern = re.compile(r"^([a-zA-Z0-9_]+)-?(\d+)?$")

    nodes = []
    for item in value.split(","):
        item = item.strip().lower()
        if node_pattern.match(item):
            match = re.match(r"^([a-zA-Z]+)(\d+)$", item)
            if match:
                prefix, num = match.groups()
                if prefix.startswith("cn"):
                    nodes.append(f"{prefix}{num.zfill(4)}")  # Add 4 digits padding
                else:
                    nodes.append(
                        f"{prefix}{num.zfill(3)}"
                    )  # Add normal 3 digits padding
            else:
                nodes.append(item)
        elif range_match := range_pattern.match(item):
            start_node = range_match.group(1)
            end_num = range_match.group(2)
            start_prefix = "".join(filter(str.isalpha, start_node))
            prefix_len = len(start_prefix)
            start_num = (
                int(re.search(r"\d+", start_node).group()) if start_prefix else 0
            )
            if end_num:
                end_num = int(end_num)
                if start_prefix.startswith("cn"):
                    nodes.extend(
                        [
                            f"{start_prefix}{i:0>4}"
                            for i in range(start_num, end_num + 1)
                        ]
                    )
                else:
                    nodes.extend(
                        [
                            f"{start_prefix}{i:0>3}"
                            for i in range(start_num, end_num + 1)
                        ]
                    )
            else:
                nodes.append(start_node)
        else:
            raise click.BadParameter(
                'Invalid node format. Use "NodeName" or "NodeName-5" for ranges.'
            )
    print(nodes)
    return nodes
