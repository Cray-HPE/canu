from setuptools import setup

with open("requirements.txt") as req_file:
    REQUIREMENTS = req_file.read()

setup(
    name="canu",
    author="Brooks Vinyard",
    author_email="brooks.vinyard@broadwing.io",
    description="CSM Automatic Network Utility",
    long_description="CANU will float through a new Shasta network and make setup a breeze.",
    version=open(".version").readline().strip(),
    py_modules=["canu"],
    install_requires=REQUIREMENTS,
    entry_points="""
        [console_scripts]
        canu=canu.cli:cli
    """,
)
