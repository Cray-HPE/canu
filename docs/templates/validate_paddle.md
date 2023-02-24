# Validate Paddle

```{eval-rst}
.. click:: canu.validate.paddle.paddle:paddle
   :prog: canu validate paddle
```

## Example

To validate a paddle CCJ run: `canu validate paddle --ccj paddle.json`

```bash
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


CANU can be used to validate that a CCJ (CSM Cabling JSON) passes basic validation checks.

To validate a paddle CCJ run: `canu validate paddle --ccj paddle.json`

```bash
canu validate paddle --ccj paddle.json
```

Potential output:

```text
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

