# mtsv-office

**Open and save MTSV files in your spreadsheet application.**

Multi-Sheet Tab-Separated Values (MTSV) is TSV with one more
dimension: a tab separates fields, a line break separates records, and
a form feed separates sheets. A whole workbook is one plain-text file.
This repository lets office applications open and save it, one sheet
for each MTSV sheet: LibreOffice Calc now, Excel next.

| You are | What changes |
|---|---|
| **Spreadsheet user** | Open a `.mtsv` file in Calc and every sheet comes in as a Calc sheet, every field as text. Save it and it is one text file again. |
| **Developer** | A workbook you keep as MTSV is text: it diffs and merges line by line, and a Python program reads it with the [mtsv](https://github.com/demos-ra/mtsv) library. Calc becomes its editor. |
| **AI model or agent** | A workbook a person keeps as MTSV is text you can read whole, every sheet; [text-spreadsheet](https://github.com/demos-ra/text-spreadsheet) reads the other formats as MTSV too. |

## Quick start

```sh
git clone https://github.com/demos-ra/mtsv-office
cd mtsv-office/libreoffice
make
unopkg add build/mtsv-office.oxt
```

Then open a `.mtsv` file in Calc, and save it as Multi-Sheet
Tab-Separated Values (MTSV). See
[libreoffice/README.md](libreoffice/README.md) for what Calc keeps,
what it leaves behind, and how to test.

## What it is

| Folder         | Contents                                      |
|----------------|-----------------------------------------------|
| `libreoffice/` | The LibreOffice extension, for Calc           |

Each application folder is one extension or add-in, with its own build
and tests. This repository holds no format code: every byte is read and
written by mtsv, and what a spreadsheet holds that MTSV does not is
left behind as mtsv reports it.

## Requirements

- LibreOffice 26.2 or later, with `unopkg`.
- make, and Python 3.11 or later, to build.
- git, for `make check`.

## Versioning

Not yet released. The version is the `version` of
[libreoffice/src/description.xml](libreoffice/src/description.xml), and
versions follow [Semantic Versioning](https://semver.org).

## Author

mtsv-office is created and maintained by Demos Ra. It is built on
[MTSV](https://github.com/demos-ra/mtsv-spec), also created by Demos Ra
and registered as an
[IETF Internet-Draft](https://datatracker.ietf.org/doc/draft-demosra-mtsv/).

## Help

Report a problem or ask a question in the
[issue tracker](https://github.com/demos-ra/mtsv-office/issues). Report
a vulnerability as [SECURITY.md](SECURITY.md) says.

## License

[MIT](LICENSE)
