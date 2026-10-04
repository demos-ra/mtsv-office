# MTSV for LibreOffice

Open and save Multi-Sheet Tab-Separated Values (MTSV) files in
LibreOffice Calc, one Calc sheet for each MTSV sheet.

The version is the `version` of
[src/description.xml](src/description.xml).

* [Specification](https://github.com/demos-ra/mtsv-spec)
* [mtsv](https://github.com/demos-ra/mtsv), which reads and writes every
  byte

## Install

Build the extension in this folder, then add it to LibreOffice 26.2 or
later:

```
make
unopkg add build/mtsv-office.oxt
```

To remove it:

```
unopkg remove io.github.demos-ra.mtsv-office
```

## Use

Open a `.mtsv` file in Calc, and save it as Multi-Sheet Tab-Separated
Values (MTSV). Every field comes in as text.

Calc's own rules apply to what it holds. A sheet name Calc does not
take, such as an empty one, gets Calc's own name for it, and a sheet
name repeated in another case gets `_2`. A character that XML 1.0 does
not allow cannot reach Calc, so a file holding one does not open.

Saving leaves behind what MTSV does not hold: formatting, formulas,
types and the rest. The status bar names what was left behind only
until the save ends, when Calc hides it.

## Test

In this folder:

```
make check
```

The tests install the extension into a LibreOffice profile of their
own, and open and save mtsv's conforming files through it.

## Layout

Each file hides one decision, named beside it.

```
src/
  META-INF/manifest.xml   what the package holds
  description.xml         who it is, its version, which LibreOffice
  Types.xcu               the MTSV type: .mtsv, text/prs.mtsv
  Filter.xcu              the filter of the MTSV type
  filter.py               how the bytes pass between mtsv and Calc
  extended_type_detection.py   whether a .mtsv file holds MTSV
  pythonpath/mtsv_office.py    what the two components share
tests/                    the filter, run in Calc
Makefile                  all, check and clean
```

Use points one way: the manifest to the two components and the two
configuration files; `Filter.xcu` to `Types.xcu` and `filter.py`;
`Types.xcu` to `extended_type_detection.py`; both components to
`mtsv_office.py` and mtsv. Nothing points back up.

## License

[MIT](../LICENSE)
