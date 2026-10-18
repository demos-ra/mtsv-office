mtsv-office
===========

Open and save spreadsheets as plain text in your office apps: a LibreOffice
Calc extension now, Excel next. Each file is Multi-Sheet Tab-Separated
Values (MTSV), TSV with sheets, one Calc sheet for each MTSV sheet, so a
whole workbook is one plain-text file.

Why It Is Useful
----------------

A workbook kept as MTSV is plain text: it diffs and merges line by line, AI
agents read it whole, and LibreOffice Calc becomes its spreadsheet editor.
This repository holds no format code: every byte is read and written by the
[mtsv](https://github.com/demos-ra/mtsv) library.

Get Started
-----------

* Build the extension: `git clone https://github.com/demos-ra/mtsv-office`, then `cd mtsv-office/libreoffice` and `make`
* Install it in LibreOffice: `unopkg add build/mtsv-office.oxt`
* Use it: open a .mtsv file in Calc, and save it as Multi-Sheet Tab-Separated Values (MTSV)
* What Calc keeps, what it leaves behind, and how to test: [libreoffice/README.md](libreoffice/README.md)

Details
-------

* Specification: [MTSV, an IETF Internet-Draft](https://github.com/demos-ra/mtsv-spec)
* Requirements: LibreOffice 26.2 or later, with unopkg; make, and Python 3.11 or later, to build; git, for `make check`; [mtsv](https://github.com/demos-ra/mtsv), at the version [libreoffice/Makefile](libreoffice/Makefile) pins, bundled by the build
* Version: not yet released; the version of [libreoffice/src/description.xml](libreoffice/src/description.xml); versions follow [Semantic Versioning](https://semver.org)
* Layout: [libreoffice/](libreoffice/README.md), the LibreOffice extension for Calc
* License: [MIT](LICENSE)

Get Help
--------

* Issues: [mtsv-office issue tracker](https://github.com/demos-ra/mtsv-office/issues)
* Security: [SECURITY.md](SECURITY.md)
* Maintainer: Demos Ra
* More: [all MTSV tools by Demos Ra](https://github.com/demos-ra)
