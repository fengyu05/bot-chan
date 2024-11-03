# setup.py

from setuptools import find_packages, setup

setup(
    name="botchan",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "botchan=botchan.cli:main",
        ],
    },
)
