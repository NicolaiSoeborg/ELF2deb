.PHONY: all
all: elf2deb.pyz
	

elf2deb.pyz: 
	python3 -m zipapp elf2deb --python="/usr/bin/env python3"

.PHONY: test
test: clean elf2deb.pyz
	./elf2deb.pyz --package_name elf2deb --package_version `./elf2deb.pyz --version | cut -d' ' -f2` --license_file LICENSE --dependencies 'python3' ./elf2deb.pyz
	cd elf2deb-`./elf2deb.pyz --version | cut -d' ' -f2` && debuild -us -uc
	@echo -n "\nDone building. Now testing output deb file:\n"
	dpkg-deb --info elf2deb_*.deb

.PHONY: test2
test2: clean elf2deb.pyz
	curl -Lo ./skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
	./elf2deb.pyz --license apache-2.0 --license_year 2018 --license_holder "The Skaffold Authors" --package_name skaffold --package_version 0.28.0 --homepage "https://skaffold.dev/" ./skaffold
	cd skaffold-0.28.0 && debuild -us -uc
	@echo -n "\nDone building. Now testing output deb file:\n"
	dpkg-deb --info skaffold_0.28.0*.deb
	# rm -rf skaffold*

.PHONY: clean
clean: 
	@rm -f elf2deb.pyz
	@rm -rf elf2deb-*.*
	@rm -rf elf2deb_*.*
