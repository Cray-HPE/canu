# Nox testing

To run full test suite: 

```text
nox
```

To run only sub section of tests:

```text
nox -rs tests 
```

To run only specific test from subsesction:

```text
nox -rs tests -- tests/test_generate_switch_config_aruba_csm_1_0.py
```

-r re-uses a previous testing virtual environment to save time.  should not be used for testing when you are adding or changing libraries.
-s specifies an overall session as defined in nox.py.  for canu currently these can be tests, lint, docs

To run the full set of tests, linting, coverage map, and docs building run:

  ```bash
  python3 -m pip install .[ci]
  ```

  ```bash
  nox
  ```

To just run tests:

  ```bash
  nox -s tests
  ```

To just run linting:

  ```bash
  nox -s lint
  ```

To run a specific test file:

  ```bash
  nox -s tests -- tests/test_report_switch_firmware.py
  ```

To reuse a session without reinstalling dependencies use the `-rs` flag instead of `-s`.
