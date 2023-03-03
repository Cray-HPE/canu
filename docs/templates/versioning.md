# Versioning

The version is derived from Git by the `setuptools_scm` Python module and follows [PEP0440](https://peps.python.org/pep-0440/#abstract)'s version identification
and dependency specification for [final](https://peps.python.org/pep-0440/#final-releases) and [pre](https://peps.python.org/pep-0440/#pre-releases) releases.

## Classification

The items below denote how stable, pre-release, and unstable versions are classified through
version strings.

* ***(stable) final release***: A git-tag following the `X.Y.Z` semver format is considered a final release version.

    ```text
    # Format:
    # {tag}
    # X.Y.Z
    # X - Major
    # Y - Minor
    # Z - Micro (a.k.a. patch)
    0.1.2
    ```

- ***(unstable) pre-release***: A git-tag with an `a`(lpha), `b`(eta), or `r`(elease) `c`(andidate) annotation and an identification number `N` denotes a pre-release/preview.

  > For `canu`, these are sometimes created before an official release (e.g. 1.7.0a1 might exist before 1.7.0 is released).
  > Additionally the beta and release candidate tags may be skipped.
  > Whether an alpha, beta, or release candidate pre-release is taken is entirely up to the `canu` release management team.

    ```text
    # Format:
    # {tag}[{a|b|rc}N]
    0.1.2a1
    0.1.2b1
    0.1.2rc1
    ```

- ***(unstable) development***: Development builds **auto-increment** the micro version (the `Z` in `X.Y.Z`) or pre-release version (the `N` in `X.Y.Z{[a|b|rc]N}`), and
  then append a suffix based on whether the working directory was **clean**, **dirty**, or **mixed**.

    - ***clean***: When the version shows an appended `devN+{scm_letter}{revision_short_hash}`, that means there have been commits made since the previous git-tag.

        ```text
        # Format:
        # {next_version}.dev{distance}+{scm_letter}{revision_short_hash}
      
        # If the previous git-tag was 0.1.2:
                   0.1.3.dev4+g818da8a
        
        # If the previous get-tag was a pre-release of 0.1.3a1:
                 0.1.3a2.dev4+g818da8a
        ```

    - ***dirty*** When the version shows an appended `.d{YYYYMMDD}` datestamp, that means there were modified/uncommitted changes in the working directory when the application was built.

        ```text
        # Format:
        # {next_version}.d(datestamp}

        # If the previous git-tag was 0.1.2:
                   0.1.3.d20230123

        # If the previous get-tag was a pre-release of 0.1.3a1:
                 0.1.2a2.d20230123
        ```

    - ***mixed*** When the version shows a development tag with an appended datestamp, this means commits have been made but there were uncommitted changes present in the working directory when the application was built.

        ```text
        # Format:
        # {next_Version}.dev{distance}+{scm_letter}{revision_short_hash}.d{datestamp}

        # If the previous git-tag was 0.1.2:
                   0.1.3.dev3+g3071655.d20230123
        
        # If the previous get-tag was a pre-release of 0.1.3a1:
                 0.1.3a2.dev3+g3071655.d20230123
        ```

## Configuration

The `setuptools_scm` module is configured by `pyproject.toml`.

For more information regarding configuration of `setuptools_scm`, see [version number construction](https://github.com/pypa/setuptools_scm/#version-number-construction).
