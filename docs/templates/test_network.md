# Test Network

```{eval-rst}
.. click:: canu.test.test:test
   :prog: canu test
```

# Testing The Network

CANU has the ability to run a set of tests against all of the switches in the management network.
It is utilizing the nornir automation framework and additional nornir plugins to do this.

More info can be found at

- <https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/>
- <https://github.com/nornir-automation/nornir>
- <https://github.com/dmulyalin/salt-nornir>

Required Input
You can either use an SLS file or pull the SLS file from the API-Gateway using a token.

- `--sls-file`
- `--auth-token`

Options

- `--log` outputs the nornir debug logs
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--json` outputs the results in json format.
- `--password` prompts if password is not entered
- `--username` defaults to admin

# Adding tests

Additional tests can be easily added by updating the .yaml file at `canu/test/*/test_suite.yaml`
More information on tests and how to write them can be found at <https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/>

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

This test logs into the cdu, leaf, leaf-bmc, and spine switches and runs the command `show version` and checks that `10.09.0010` is in the output.  If it's not the test fails.
