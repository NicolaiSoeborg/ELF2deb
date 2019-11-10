# ELF*2*deb
<img align="right" src="https://raw.githubusercontent.com/NicolaiSoeborg/ELF2deb/master/.github/logo-small.png" alt="logo" />

Convert any single (or multiple) executable file(s) to deb-package.

I.e. this is a script to convert *AppImage|ELF|executable script* to `.deb`.

The script will place the binary file(s) in `/usr/bin/`.

## Setup

You want to set `DEBEMAIL` and `DEBFULLNAME` for the *deb tools* to work properly:

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

 * simple, small size (< 10 kB), and few dependencies:
   - `>= python3.5` (+ `requests` if need to download a license file).
   - `debhelper` and `devscripts` (`apt install --no-install-recommends debhelper devscripts`).

## More examples (interactive!)

In version 1.2.0 a interactive menu was added to ELF*2*deb:

```bash
$ git clone https://github.com/NicolaiSoeborg/ELF2deb.git && cd ELF2deb/
$ make  # to make 'elf2deb.pyz' (or use pip to install globally, or carry/copy elf2deb.pyz around)
$ ./elf2deb.pyz elf2deb.pyz  # package 'elf2deb.pyz' using elf2deb (very meta!)
Package info:
author_mail: git@xn--sb-lka.org
author_name: Nicolai Søborg
binary_files: ['elf2deb.pyz']
dependencies: 
homepage: None
license: None
license_file: <_io.TextIOWrapper name='/.../ELF2deb/LICENSE' mode='r' encoding='UTF-8'>
license_holder: None
license_year: None
package_name: ELF2deb
package_version: 0.0.1
==> Does this look correct? (y/n/q): n

Properties:
[1] author_mail
[2] author_name
[3] binary_files
[4] dependencies
[5] homepage
[6] license
[7] license_file
[8] license_holder
[9] license_year
[10] package_name
[11] package_version
==> Which property to change? (1..11): 4
==> Which value should dependencies be changed to? python3, python3-requests

Package info:
author_mail: git@xn--sb-lka.org
author_name: Nicolai Søborg
binary_files: ['elf2deb.pyz']
dependencies: python3, python3-requests
homepage: None
license: None
license_file: <_io.TextIOWrapper name='/home/nsq/pakker/test/ELF2deb/LICENSE' mode='r' encoding='UTF-8'>
license_holder: None
license_year: None
package_name: ELF2deb
package_version: 0.0.1
==> Does this look correct? (y/n/q): n
[...]
==> Which value should package_version be changed to? 1.2.0
[...]
==> Does this look correct? (y/n/q): y
Copying templates... done!
Copying files... done!
Run:
 * cd elf2deb-1.2.0
 * vim debian/control  # change description, dont add empty lines
 * debuild -us -uc  # remove -us -uc if you want to sign the deb file

$ cd elf2deb-1.2.0
$ vim debian/control
$ debuild -us -uc
[...]
dpkg-deb: building package 'elf2deb' in '../elf2deb_1.2.0_amd64.deb'.

$ dpkg-deb --info ../elf2deb_1.2.0_amd64.deb
 new Debian package, version 2.0.
 size 5100 bytes: control archive=624 bytes.
     383 bytes,    12 lines      control
     189 bytes,     3 lines      md5sums
 Package: elf2deb
 Version: 1.2.0
 Architecture: amd64
 Maintainer: Nicolai Søborg <git@xn--sb-lka.org>
 Installed-Size: 20
 Depends: python3, python3-requests
 Section: misc
 Priority: optional
 Multi-Arch: foreign
 Description: tool to easily package any binary to a deb file
  ELF2deb makes it easy to package simple binaries to a deb file
  to help deploy files across debian environments.
```
