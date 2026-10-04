"""Test the MTSV filter in LibreOffice Calc, run headless.

Each test class installs the built extension into a profile of its own,
and each file is opened and saved through the filter by soffice
--convert-to. What should come back is what mtsv's ODF single XML file
holds, named as Calc names sheets.
"""

__all__ = []

import io
import json
import pathlib
import subprocess
import tempfile
import unittest

import mtsv
from mtsv.integrations import odf_single_xml

BUILD = pathlib.Path(__file__).resolve().parents[1] / "build"
OXT = BUILD / "mtsv-office.oxt"
CONFORMING = BUILD / "mtsv" / "conformance" / "conforming"
FILTER = "io.github.demos-ra.mtsv-office.MTSV Spreadsheet"
# sc/source/core/data/document.cxx, ValidTabName: the characters a sheet
# name cannot hold.
NOT_IN_NAME = ":\\/?*[]"
# sc/source/core/tool/defaultsoptions.cxx, ScDefaultsOptions: the
# default prefix of a sheet name, STR_TABLE_DEF; sc/inc/globstr.hrc:
# "Sheet".
PREFIX = "Sheet"


class _Installed(unittest.TestCase):
    """Tests run with the extension installed in their own profile."""

    @classmethod
    def setUpClass(cls):
        """Install the built extension into a profile of its own."""
        directory = cls.enterClassContext(tempfile.TemporaryDirectory())
        cls.profile = "-env:UserInstallation=" + pathlib.Path(directory).as_uri()
        subprocess.run(["unopkg", "add", cls.profile, str(OXT)], check=True)


class TestHandOff(_Installed):
    """The hand-off to Calc's flat ODF filter, both ways."""

    def test_round_trip(self):
        """A file of named sheets comes back byte for byte."""
        source = CONFORMING / "multiple-sheets.mtsv"
        with tempfile.TemporaryDirectory() as directory:
            saved = convert(self.profile, source, directory)
        self.assertEqual(saved, source.read_bytes())


class TestConformance(_Installed):
    """mtsv's conforming files, opened and saved in Calc."""

    def test_conforming(self):
        """Each comes back as Calc holds it."""
        for path in sorted(CONFORMING.glob("*.mtsv")):
            with self.subTest(path.name):
                result = json.loads(path.with_suffix(".json").read_text("utf-8"))
                want = expected(result)
                with tempfile.TemporaryDirectory() as directory:
                    saved = convert(self.profile, path, directory)
                if want is None:
                    self.assertIsNone(saved)
                else:
                    self.assertIsNotNone(saved)
                    self.assertEqual(mtsv.loads(saved.decode("utf-8")), want)


def convert(profile, path, directory):
    """Open a file, save it through the filter, return what was saved.

    profile -- the -env:UserInstallation option of the profile to use
    path -- the MTSV file to open
    directory -- the folder to save into

    Return the bytes saved, or None where nothing was saved.
    """
    subprocess.run(
        [
            "soffice",
            profile,
            "--headless",
            "--convert-to",
            "mtsv:" + FILTER,
            "--outdir",
            directory,
            str(path),
        ],
        capture_output=True,
    )
    saved = pathlib.Path(directory, path.name)
    return saved.read_bytes() if saved.exists() else None


def expected(sheets):
    """Return the sheets that should come back, or None for none.

    sheets -- the sheets of the file opened

    What mtsv's ODF single XML file holds, with the names Calc gives;
    a file of no sheets comes back as the one sheet a new document
    holds.
    """
    odf = io.BytesIO()
    try:
        odf_single_xml.dump(sheets, odf)
    except ValueError:
        return None
    odf.seek(0)
    held = odf_single_xml.load(odf)
    if not held:
        return [{"sheet name": PREFIX + "1", "header": None, "records": []}]
    names = calc_names([sheet["sheet name"] for sheet in held])
    return [dict(sheet, **{"sheet name": name}) for sheet, name in zip(held, names)]


def calc_names(names):
    """Return the sheet names Calc gives sheets loaded with these names.

    names -- the sheet names, in order

    ScMyTables::NewSheet: the first sheet keeps the name the new
    document gave it when the name is not valid; every later sheet
    takes ScDocument::CreateValidTabName.
    """
    given = []
    for index, name in enumerate(names):
        if index == 0:
            given.append(name if valid(name) else PREFIX + "1")
            continue
        taken = {other.upper() for other in given}
        if not valid(name):
            number = len(given) + 1
            while (PREFIX + str(number)).upper() in taken:
                number += 1
            given.append(PREFIX + str(number))
        elif name.upper() in taken:
            number = 2
            while (name + "_" + str(number)).upper() in taken:
                number += 1
            given.append(name + "_" + str(number))
        else:
            given.append(name)
    return given


def valid(name):
    """Return whether Calc takes a sheet name, ScDocument::ValidTabName.

    name -- the sheet name
    """
    return (
        bool(name)
        and not any(char in NOT_IN_NAME for char in name)
        and not name.startswith("'")
        and not name.endswith("'")
    )
