import pathlib
import re
from setuptools import find_packages, setup

# YOU SHOULDN'T CALL THIS FILE USING "python setup.py ..."
# INSTEAD SEE THE Makefile FOR TARGET "pip"
# E.g. run: `make pip`

this = pathlib.Path(__file__).parent

def find_version(version_file):
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="ELF2deb",
    version=find_version((this / "elf2deb/__main__.py").read_text()),
    description="Convert any single (or multiple) executable file(s) to .deb package",
    long_description=(this / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/NicolaiSoeborg/ELF2deb/",
    author="Nicolai Søborg",
    author_email="elf2deb@xn--sb-lka.org",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Installation/Setup",
    ],
    packages=["elf2deb"],
    include_package_data=True,
    install_requires=find_packages(),
    entry_points={
        "console_scripts": [
            "elf2deb=elf2deb.__main__:main",
        ]
    },
)
