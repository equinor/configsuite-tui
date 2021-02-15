import os
from setuptools import setup

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def _load_readme():
    readme = os.path.join(PROJECT_ROOT, "README.md")
    with open(readme) as f:
        return f.read()


setup(
    name="configsuite-tui",
    author="Equinor ASA",
    url="https://github.com/equinor/configsuite-tui",
    description="Text-based user interface for Config Suite",
    long_description=_load_readme(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["configsuite_tui"],
    use_scm_version={"write_to": "configsuite_tui/_version.py"},
    setup_requires=["setuptools_scm", "setuptools_scm_about"],
    install_requires=[
        "pyyaml",
        "npyscreen",
        "configsuite",
        "fastnumbers",
        "pluggy",
        "python-dateutil",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["configsuite_tui=configsuite_tui.tui:tui"]},
)
