# ELF*2*deb
<img align="right" src="https://raw.githubusercontent.com/NicolaiSoeborg/ELF2deb/master/.github/logo-small.png" alt="logo" />

Convert any single (or multiple) executable file(s) to deb-package.

I.e. this is a script to convert *AppImage|ELF|executable script* to `.deb`.

The script will place the binary file(s) in `/usr/bin/`.

## Setup

You want to setup `DEBEMAIL` and `DEBFULLNAME` for the *deb* tools to work properly:

```bash
$ cat >>~/.bashrc <<EOF
DEBEMAIL="email@example.org"
DEBFULLNAME="John Doe"
export DEBEMAIL DEBFULLNAME
EOF
$ . ~/.bashrc
```

Then it's as simple as downloading `elf2deb.pyz` from [releases](https://github.com/NicolaiSoeborg/ELF2deb/releases) **or** download it from PyPi: `pip3 install elf2deb` and `elf2deb --help`.

## Example

In this example I'm first downloading the [skaffold](https://skaffold.dev/) binary and packing it as a `.deb` file:

```bash
# Download ./skaffold binary to empty folder:
$ curl -Lo ./skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64

# Run the tool:
$ ./elf2deb.pyz --license apache-2.0 --license_year 2018 --license_holder "The Skaffold Authors" \
> --package_name skaffold --package_version 0.28.0 --homepage "https://skaffold.dev/" ./skaffold

# Fix description and use debuild:
$ cd skaffold-0.28.0/
$ vim debian/control  # add description
$ debuild -us -uc
[... lots of debuild output ...]
$ cd ../

# Finally the .deb file is ready to be uploaded, or installed:
$ sudo dpkg -i skaffold_0.28.0_amd64.deb
```

## Arguments

```
usage: elf2deb [-h] [--version]
               --package_name PACKAGE_NAME
               --package_version PACKAGE_VERSION
               [--homepage HOMEPAGE]
               [--dependencies DEPENDENCIES]
               [--license {MIT,LGPL-3.0,MPL-2.0,AGPL-3.0,unlicense,apache-2.0,GPL-3.0} | --license_file LICENSE_FILE]
               [--license_year LICENSE_YEAR]
               [--license_holder LICENSE_HOLDER]
               binary_files [binary_files ...]

positional arguments:
  binary_files          The binaries you want to package.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

package info:
  --package_name PACKAGE_NAME
                        The name of the deb package
  --package_version PACKAGE_VERSION
                        The version of the package
  --homepage HOMEPAGE   The webpage of the package
  --dependencies DEPENDENCIES
                        Dependencies specified in the deb package

license info:
  --license {MIT,LGPL-3.0,MPL-2.0,AGPL-3.0,unlicense,apache-2.0,GPL-3.0}
                        Select a standard license.
  --license_file LICENSE_FILE
                        ... or use a LICENSE text file.
  --license_year LICENSE_YEAR
                        If using a standard license: year
  --license_holder LICENSE_HOLDER
                        If using a standard license: owner
```

## Common warnings

If you are running Ubuntu, you might get `E: bad-distribution-in-changes-file unstable`.
In this case edit `debian/changelog` and change `unstable` to your distributions codename (find it by running `lsb_release -c`).
Then run `debuild -us -uc` from source directory, to recompile the `.deb`.

If you are missing the `dch`-tool, then run: `sudo apt install --no-install-recommends devscripts libdistro-info-perl`.

You can safely ignore the following warnings from lintian:

 * `source-is-missing`

 * `binary-without-manpage`

(you will probably get a longer list of errors and warnings, no worries)

## Packaging for other/more formats

If you want to distribute your software in more formats -- or your source isn't a list of binaries -- then consider using a tool like "[**E**ffing **p**ackage **m**anagement](https://github.com/jordansissel/fpm)". FPM is a much more mature tool that allows for advanced packaging.

The advantages of ELF*2*deb is;

 * can be installed using `pip install elf2deb` or used a as a standalone executable `./elf2deb.pyz`

 * simple, small size (7 kB), and few dependencies (python3 and requests)
