# Installation

- To run CANU inside a container:

  - Prerequisites:
    - docker
    - docker-compose

    ```bash
    sh canu_docker.sh up
    ```

  - CANU source files can be found inside the container at /app/canu
  - shared folder between local disk is call `files` and is mounted in the container at `/files`
  - When you are finished with the container and `exit` the container:

    ```bash
    sh canu_docker.sh down
    ```

- To run CANU in a Python Virtualenv:

  - Prerequisites:
    - python3
    - pip3
    - Python Virtualenv

      ```bash
      python3 -m venv .venv
      source ./.venv/bin/activate
      python3 -m pip install 'setuptools_scm[toml]'
      python3 -m pip install .
      ```

  - When you are done working in the Python Virtualenv.
    Use the following command to exit out of the Python Virtualenv:

    ```bash
    deactivate
    ```

- To install the development build of CANU type:

  ```bash
  python3 -m pip install --editable .
  ```

- To install SLES RPM versions

{doc}`RPM Install <rpm_install>`

To run, just type `canu`, it should run and display help. To see a list of commands and arguments, just append `--help`.




