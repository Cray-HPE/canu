# Setup A Virtual Environment

Besides using the CANU container, setting up a Python virtual environment and installing canu from this repo is another option for using and developing CANU.

```shell
git clone
cd canu
python3 -m venv .venv
source ./.venv/bin/activate
python3 -m pip install 'setuptools_scm[toml]'
python3 -m pip install . 
# or python3 -m pip install --editable . 
```

## Development Build

You can install CANU in editable mode, which allows for changes you make in the code to show up immediately when running CANU.

```bash
python3 -m pip install --editable .
```

## Install Extras

You may also want to install some CANU's extras if you are developing it.  For example, you may want to run some of the unit tests, or generate new documentation.  These extras can be seen in `pyproject.toml`.  

```
python3 -m pip install '.[docs,lint,test]'
```

### Exiting The Virtual Environment

When you are done working in the virtual environment, exit out it:

```bash
deactivate
```
