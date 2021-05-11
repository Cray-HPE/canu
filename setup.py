from setuptools import setup, find_packages

with open("requirements.txt") as req_file:
    REQUIREMENTS = req_file.read()

setup(
    name="canu",
    author="Brooks Vinyard",
    author_email="brooks.vinyard@broadwing.io",
    description="CSM Automatic Network Utility",
    long_description="CANU floats through a new Shasta network and makes setup a breeze.",
    version="0.0.4",
    py_modules=["canu"],
    packages=find_packages(exclude=("tests",)),
    package_data={"canu": ["canu.yaml", "canu/canu.yaml"]},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points="""
        [console_scripts]
        canu=canu.cli:cli
    """,
)
