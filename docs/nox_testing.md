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
