.PHONY: all
all: elf2deb.pyz
	

elf2deb.pyz: 
	python3 -m zipapp elf2deb --python="/usr/bin/env python3"

.PHONY: test
test: elf2deb.pyz
	./elf2deb.pyz --package_name elf2deb --package_version `./elf2deb.pyz --version | awk '{print $NF}'` --license_file LICENSE ./elf2deb.pyz
