# Test Network

## canu test

Run tests against the network.

Args:

    ctx: CANU context settings
    username: Switch username
    csm: CSM version
    password: Switch password
    sls_file: JSON file containing SLS data
    sls_address: The address of SLS
    network: The network that is used to connect to the switches.


    ```
    log_
    ```

    : enable logging


    ```
    json_
    ```

    : output test results in JSON format
    ping: run the ping test suite

```shell
canu test [OPTIONS]
```

### Options


### --sls-file( <sls_file>)
File containing system SLS JSON data.


### --network( <network>)
The network that is used to connect to the switches.


* **Default**

    `HMN`



* **Options**

    HMN | CMN



### --log()
enable logging.


### --json()
JSON output.


### --ping()
Ping test from all mgmt switches to all NCNs.


### --sls-address( <sls_address>)

* **Default**

    `api-gw-service-nmn.local`



### --password( <password>)
Switch password


### --csm( <csm>)
**Required** CSM version


* **Options**

    1.0 | 1.2 | 1.3



### --username( <username>)
Switch username


* **Default**

    `admin`


# Testing The Network

CANU has the ability to run a set of tests against all of the switches in the management network.
It is utilizing the nornir automation framework and additional nornir plugins to do this.

More info can be found at


* [https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/](https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/)


* [https://github.com/nornir-automation/nornir](https://github.com/nornir-automation/nornir)


* [https://github.com/dmulyalin/salt-nornir](https://github.com/dmulyalin/salt-nornir)

Required Input
You can either use an SLS file or pull the SLS file from the API-Gateway using a token.


* `--sls-file`


* `--auth-token`

Options


* `--log` outputs the nornir debug logs


* `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.


* `--json` outputs the results in json format.


* `--password` prompts if password is not entered


* `--username` defaults to admin

# Adding tests

Additional tests can be easily added by updating the .yaml file at `canu/test/\*/test_suite.yaml`
More information on tests and how to write them can be found at [https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/](https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/)

Example test

```yaml
- name: Software version test
  task: show version
  test: contains
  pattern: "10.08.1021"
  err_msg: Software version is wrong
  device:
    - cdu
    - leaf
    - leaf-bmc
    - spine
```

This test logs into the cdu, leaf, leaf-bmc, and spine switches and runs the command `show version` and checks that `10.09.0010` is in the output.  If it’s not the test fails.
