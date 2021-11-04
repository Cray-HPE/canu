# CANU Init

```{eval-rst}
.. click:: canu.cli:init
   :prog: canu init
```

## Examples

### 1. CSI

To get the switch IP addresses from CSI output, run the command:

```bash
$ canu init --sls-file SLS_FILE --out output.txt
8 IP addresses saved to output.txt
```

![](images/canu_init.png)

### 2. SLS Shasta API

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
$ canu init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
8 IP addresses saved to output.txt
```

---

<a href="/readme.md">Back To Readme</a><br>
