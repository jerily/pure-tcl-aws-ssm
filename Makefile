PREFIX ?= /usr/local
DESTDIR ?=
TCLSH ?= tclsh9.1
PACKAGE = pure-tcl-aws-ssm
VERSION = 1.0.0
.PHONY: all install test
all:
	@echo "Tcl package; no compilation required."
install:
	install -d "$(DESTDIR)$(PREFIX)/lib/$(PACKAGE)$(VERSION)/library"
	install -m 644 pkgIndex.tcl "$(DESTDIR)$(PREFIX)/lib/$(PACKAGE)$(VERSION)/"
	install -m 644 library/*.tcl "$(DESTDIR)$(PREFIX)/lib/$(PACKAGE)$(VERSION)/library/"
	install -d "$(DESTDIR)$(PREFIX)/share/doc/$(PACKAGE)"
	install -m 644 README.md LICENSE "$(DESTDIR)$(PREFIX)/share/doc/$(PACKAGE)/"
test:
	$(TCLSH) tests/all.tcl
