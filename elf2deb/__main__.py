import os
import shutil
from pathlib import Path
from zipfile import ZipFile

__version__ = "1.0.0"
TEMPLATE_DIR = "templates/"


def get_copyright(args):
    import requests
    from datetime import datetime

    r = requests.get("https://api.github.com/licenses/" + args.license)
    if r.status_code != 200:
        print("Unknown license (or no connection to GitHub Licenses API)")
        exit(1)
    license_txt = r.json()["body"]

    year = args.license_year or datetime.now().year
    fullname = args.license_holder or args.author_name

    # MIT
    license_txt = license_txt.replace("[year]", year)
    license_txt = license_txt.replace("[fullname]", fullname)

    # Apache-2.0
    license_txt = license_txt.replace("[yyyy]", year)
    license_txt = license_txt.replace("[name of copyright owner]", fullname)

    return license_txt


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="ELF2deb")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    package_group = parser.add_argument_group("package info")
    package_group.add_argument(
        "--package_name", required=True, help="The name of the deb package"
    )
    package_group.add_argument(
        "--package_version", required=True, help="The version of the package"
    )
    package_group.add_argument(
        "--homepage", default="https://example.com/", help="The homepage of the package"
    )
    package_group.add_argument(
        "--dependencies", default="", help="Dependencies specified in the deb package"
    )

    license_group = parser.add_argument_group("license info")
    license_group.add_argument(
        "--license", default=None, help="TODO",
        choices=[
            "MIT",
            "LGPL-3.0",
            "MPL-2.0",
            "AGPL-3.0",
            "unlicense",
            "apache-2.0",
            "GPL-3.0",
        ],
    )
    license_group.add_argument("--license_year", default=None, help="TODO")
    license_group.add_argument("--license_holder", default=None, help="TODO")

    parser.add_argument(
        "binary_files", help="The binaries you want to package.", nargs="+"
    )

    args = parser.parse_args()

    args.author_name = os.getenv("DEBFULLNAME")
    args.author_mail = os.getenv("DEBEMAIL")

    # Create app dir:
    package_dir = Path("{package_name}-{package_version}".format(**vars(args)))
    if package_dir.exists():
        if (input("Folder {} already exists.  Delete? (y/n) ".format(package_dir)).lower() == "y"):
            shutil.rmtree(str(package_dir))
    package_dir.mkdir(exist_ok=True)

    print("Copying files... ", end="", flush=True)
    binary_files = []
    for i, binary in enumerate(args.binary_files):
        shutil.copy(binary, str(package_dir / os.path.basename(binary)))
        # TODO: doest exist yet
        # if i > 0:
        #    (package_dir / 'Makefile').write_text("\tcp {} $(DESTDIR)$(PREFIX)/bin/".format(binary))

        binary_files.append(os.path.basename(binary))
    args.binary_files = binary_files
    print("done!")

    # print("Copying templates... ", end='', flush=True)
    me = ZipFile(os.path.dirname(__file__), "r")
    for template in me.filelist:
        if template.filename == os.path.basename(__file__):
            continue  # skip this file

        target_filename = template.filename[len(TEMPLATE_DIR) :]
        if template.is_dir():
            (package_dir / target_filename).mkdir(exist_ok=True)
        else:
            date = me.read(template).decode().format(**vars(args))
            (package_dir / target_filename).write_text(date)

    if args.license is not None:
        copyright_file = package_dir / "debian/copyright"
        copyright_file.write_text(get_copyright(args))
    print("done!")

    print("Run:")
    print("cd {}".format(package_dir))
    print("dch --create --empty --distribution unstable --package {package_name} --newversion {package_version}".format(**vars(args)))
    print("dch --append 'Empty changelog' 2>/dev/null")
    print("vim debian/control  # change description, dont add empty lines")
    print("debuild -us -uc")


if __name__ == "__main__":
    main()
