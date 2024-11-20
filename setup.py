# setup.py

from setuptools import find_packages, setup

setup(
    name="fluctlight",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fluctlight=fluctlight.cli:main",
            "fluctlight_async=fluctlight.async_cli:main",
            "fluctlight_api=fluctlight.web_server.api:main",
        ],
    },
)
