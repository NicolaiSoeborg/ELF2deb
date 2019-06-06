import argparse
import os
import shutil
from subprocess import run, DEVNULL
from pathlib import Path
from zipfile import ZipFile

__version__ = "1.2.0"
TEMPLATE_DIR = "templates/"

def main():
    args = get_args()

    # Create app dir:
    package_dir = Path("{package_name}-{package_version}".format(**vars(args)))
    if package_dir.exists():
        if (input("Folder {} already exists.  Delete? (y/n) ".format(package_dir)).lower() == "y"):
            shutil.rmtree(str(package_dir))
    package_dir.mkdir(exist_ok=True)

    print("Copying templates... ", end='', flush=True)
    try:
        # If running from a .pyz file:
        me = ZipFile(os.path.dirname(__file__), "r")
    except:
        # If running from pip:
        me = ZipFile(os.path.dirname(__file__) + '/elf2deb.pyz' , "r")
    for template in me.filelist:
        if template.filename.startswith("__"):
            continue  # skip dunder files

        target_filename = template.filename[len(TEMPLATE_DIR):]
        if template.filename.endswith('/'):
            (package_dir / target_filename).mkdir(exist_ok=True)
        else:
            data = me.read(template).decode().format(**vars(args))
            (package_dir / target_filename).write_text(data)

    if args.license is not None:
        copyright_file = package_dir / 'debian/copyright'
        copyright_file.write_text(get_copyright(args))
    elif args.license_file is not None:
        copyright_file = package_dir / 'debian/copyright'
        copyright_file.write_text(args.license_file.read())

    # Make debian/rules executable:
    mode = os.stat(str(package_dir / 'debian/rules')).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(str(package_dir / 'debian/rules'), mode)
    print("done!")

    print("Copying files... ", end='', flush=True)
    makefile = open(str(package_dir / 'Makefile'), 'at')
    for i, binary in enumerate(args.binary_files):
        # Copy binary to package base dir:
        shutil.copy(binary, str(package_dir / os.path.basename(binary)))
        if i > 0:
            # Update makefile (TODO: update template to support a list of binaries)
            makefile.write('\tcp {} $(DESTDIR)$(PREFIX)/bin/\n'.format(binary))
    makefile.close()
    print("done!")

    run(['dch', '--create', '--empty', '--distribution', 'unstable', '--package', args.package_name, '--newversion', args.package_version], cwd=str(package_dir))
    run(['dch', '--append', 'Packaged using ELF2deb v{}'.format(__version__)], stderr=DEVNULL, cwd=str(package_dir))

    print("Run:")
    print(" * cd {}".format(package_dir))
    print(" * vim debian/control  # change description, dont add empty lines")
    print(" * debuild -us -uc  # remove -us -uc if you want to sign the deb file")


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

    # GNU
    license_txt = license_txt.replace("<year>", year)
    license_txt = license_txt.replace("<name of author>", fullname)
    license_txt = license_txt.replace("<program>", args.package_name)

    return license_txt


def auto_config():
    config = {}

    # Check if a "LICENSE" file is in cwd:
    for f in filter(lambda x: x.is_file(), Path.cwd().iterdir()):
        if "LICENSE" in f.name.upper():
            config['license_file'] = f

    args_required = not ('license_file' in config)
    return args_required, config


def verify_auto_config(args):
    while True:
        items = sorted(vars(args).items())
        print("Package info:")
        for k, v in items:
            print('{}: {}'.format(k, v))
        ans = input("==> Does this look correct? (y/n/q) ").lower()
        if ans == 'y':
            return args
        elif ans == 'n':
            print("\nProperties:")
            for i, (k, _) in enumerate(items):
                print('[{}] {}'.format(i+1, k))
            while True:
                change_idx = int(input("\n==> Which property to change? ({}..{}) ".format(1, len(items)))) - 1
                if 0 <= change_idx < len(items):
                    break
            prop = items[change_idx][0]
            new_value = input("==> Which value should {} be changed to? ".format(prop))
            args.__dict__[prop] = new_value  # change args
        elif ans == 'q':
            exit(1)


def get_args():
    args_required, config = auto_config()

    parser = argparse.ArgumentParser(prog="ELF2deb")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    package_group = parser.add_argument_group("package info")
    package_group.add_argument(
        "--package_name", required=args_required, help="The name of the deb package"
    )
    package_group.add_argument(
        "--package_version", required=args_required, help="The version of the package"
    )
    package_group.add_argument(
        "--homepage", "--webpage", help="The webpage of the package"
    )
    package_group.add_argument(
        "--dependencies", default="", help="Dependencies specified in the deb package (comma seperated)"
    )

    license_group = parser.add_argument_group("license info")
    license_txt = license_group.add_mutually_exclusive_group()
    license_txt.add_argument(
        "--license", default=None, help="Select a standard license.",
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
    license_txt.add_argument('--license_file', type=argparse.FileType('r'), help="... or use a LICENSE text file."),
    license_group.add_argument("--license_year", default=None, help="If using a standard license: year")
    license_group.add_argument("--license_holder", default=None, help="If using a standard license: owner")

    parser.add_argument(
        "binary_files", help="The binaries you want to package.", nargs="+"
    )

    # Parse arguments:
    args = parser.parse_args()
    args.author_name = os.getenv("DEBFULLNAME", os.getlogin())
    args.author_mail = os.getenv("DEBEMAIL", "email@example.org")

    if not args_required:
        args_before = frozenset([args.license_file, args.package_name, args.package_version])
        args.license_file = args.license_file or config['license_file'].open()
        args.package_name = args.package_name or Path.cwd().name
        args.package_version = args.package_version or "0.0.1"
        if args_before != frozenset([args.license_file, args.package_name, args.package_version]):
            args = verify_auto_config(args)

    # Fix homepage (TODO: figure out how to include this in the template file)
    args.homepage = 'Homepage: {}'.format(args.homepage) if args.homepage else ''

    # Make sure package name is lowercase:
    args.package_name = args.package_name.lower()

    return args


if __name__ == "__main__":
    main()
