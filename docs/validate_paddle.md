# Validate Paddle

## canu validate paddle

Validate a CCJ file.

Pass in a CCJ file to validate that it works architecturally. The validation will ensure that spine switches,
leaf switches, edge switches, and nodes all are connected properly.

```
canu validate paddle [OPTIONS]
```

### Options

### --ccj( <ccj>)

CCJ (CSM Cabling JSON) File containing system topology.

### --out( <out>)

Output results to a file

## Example

To check a paddle CCJ run: `canu validate paddle --ccj paddle.json`

```
$ canu validate paddle --ccj paddle.json

CCJ Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 6 nodes: [1, 2, 3, 4, 5, 6]
1: sw-spine-002 connects to 6 nodes: [0, 2, 3, 4, 5, 6]
2: sw-leaf-bmc-001 connects to 2 nodes: [0, 1]
3: uan001 connects to 2 nodes: [0, 1]
4: ncn-s001 connects to 2 nodes: [0, 1]
5: ncn-w001 connects to 2 nodes: [0, 1]
6: ncn-m001 connects to 2 nodes: [0, 1]

```

---

<a href="/readme.md">Back To Readme</a><br>
