"""Open and save MTSV in LibreOffice Calc, through its flat ODF filter.

Classes:
Filter -- the import and export filter of MTSV

Constants:
g_ImplementationHelper -- the implementation and the services it offers
"""

__all__ = ["Filter", "g_ImplementationHelper"]

import io
import logging
from typing import Any

import mtsv
import uno
import unohelper
from com.sun.star.document import XExporter, XFilter, XImporter
from mtsv.integrations import odf_single_xml

from mtsv_office import IDENTIFIER, read

_IMPLEMENTATION = IDENTIFIER + ".Filter"
_SERVICES = (
    "com.sun.star.document.ImportFilter",
    "com.sun.star.document.ExportFilter",
)
# LibreOffice, filters/ODS_FlatXML.xcu: Calc's filter for a single XML
# document.
_FLAT_ODF = "OpenDocument Spreadsheet Flat XML"
# mtsv's README, What is left behind: the logger of the report.
_LOGGER = logging.getLogger("mtsv.integrations")


class Filter(unohelper.Base, XImporter, XExporter, XFilter):
    """The import and export filter of MTSV, for Calc.

    LibreOffice Developer's Guide, Filters: whether setTargetDocument
    or setSourceDocument was called decides what filter does.
    """

    def __init__(self, ctx: Any, *args: Any) -> None:
        """Keep the component context.

        ctx -- the component context
        args -- the filter's configuration, which FilterFactory passes
        """
        self._ctx = ctx
        self._target = None
        self._source = None

    def setTargetDocument(self, document: Any) -> None:
        """Import into a document, XImporter.

        document -- the Calc document to fill
        """
        self._target = document

    def setSourceDocument(self, document: Any) -> None:
        """Export from a document, XExporter.

        document -- the Calc document to write
        """
        self._source = document

    def filter(self, descriptor: Any) -> bool:
        """Import or export, as the document given says, XFilter.

        descriptor -- the MediaDescriptor, a sequence of PropertyValue

        Return whether it succeeded.
        """
        properties = {item.Name: item.Value for item in descriptor}
        if self._target is not None:
            return _import(self._ctx, self._target, properties)
        return _export(self._ctx, self._source, properties)

    def cancel(self) -> None:
        """Cancel the filter, XFilter; filter runs to its end."""


def _import(ctx: Any, document: Any, properties: dict[str, Any]) -> bool:
    """Read MTSV from the descriptor into a Calc document.

    ctx -- the component context
    document -- the Calc document to fill
    properties -- the MediaDescriptor, by name

    Return whether it succeeded: the bytes are MTSV, an ODF single XML
    file holds them, and Calc's flat ODF filter loads it.
    """
    stream = _stream_in(properties)
    if stream is None:
        return False
    data = read(stream)
    odf = io.BytesIO()
    try:
        sheets = mtsv.load(io.BytesIO(data))
        odf_single_xml.dump(sheets, odf)
    except ValueError:
        return False
    flat = _flat_filter(ctx)
    flat.setTargetDocument(document)
    return flat.filter(_descriptor(properties, InputStream=_input(ctx, odf.getvalue())))


def _export(ctx: Any, document: Any, properties: dict[str, Any]) -> bool:
    """Write a Calc document to the descriptor as MTSV.

    ctx -- the component context
    document -- the Calc document to write
    properties -- the MediaDescriptor, by name

    Return whether it succeeded: Calc's flat ODF filter writes the
    document, mtsv reads it, leaving behind what MTSV cannot hold, and
    writes MTSV. What is left behind is shown as status text.
    """
    stream = _stream_out(properties)
    if stream is None:
        return False
    pipe = _pipe(ctx)
    flat = _flat_filter(ctx)
    flat.setSourceDocument(document)
    if not flat.filter(_descriptor(properties, OutputStream=pipe)):
        return False
    pipe.closeOutput()
    data = read(pipe)
    text = io.BytesIO()
    left = _LeftBehind()
    _LOGGER.addHandler(left)
    try:
        sheets = odf_single_xml.load(io.BytesIO(data), errors="ignore")
        mtsv.dump(sheets, text)
    except ValueError:
        return False
    finally:
        _LOGGER.removeHandler(left)
    stream.writeBytes(uno.ByteSequence(text.getvalue()))
    _report(properties.get("StatusIndicator"), left.names)
    return True


def _stream_in(properties: dict[str, Any]) -> Any:
    """Return the stream to read, or None.

    properties -- the MediaDescriptor, by name

    LibreOffice Developer's Guide, MediaDescriptor: "first check for a
    "Stream" property"; "if it isn't available, check for an
    "InputStream" property".
    """
    if properties.get("Stream") is not None:
        return properties["Stream"].getInputStream()
    return properties.get("InputStream")


def _flat_filter(ctx: Any) -> Any:
    """Return Calc's flat ODF filter, by its name, from FilterFactory.

    ctx -- the component context

    LibreOffice, FilterFactory.idl: "The factory interface can be used
    to create filter components by its internal filter name only."
    """
    factory = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.document.FilterFactory", ctx
    )
    return factory.createInstanceWithArguments(
        _FLAT_ODF, (_property("FilterName", _FLAT_ODF),)
    )


def _descriptor(properties: dict[str, Any], **streams: Any) -> tuple[Any, ...]:
    """Return the MediaDescriptor passed on to Calc's flat ODF filter.

    properties -- the MediaDescriptor this filter was given, by name
    streams -- the stream Calc's filter reads or writes instead

    LibreOffice Developer's Guide, MediaDescriptor: it "is passed as an
    in/out parameter to some methods of objects that participate in the
    loading or storing process"; "first check for a "Stream"
    property", so the Stream given is not passed on.
    """
    passed = {name: value for name, value in properties.items() if name != "Stream"}
    passed.update(streams, FilterName=_FLAT_ODF)
    return tuple(_property(name, value) for name, value in passed.items())


def _input(ctx: Any, data: bytes) -> Any:
    """Return an input stream over bytes, SequenceInputStream.

    ctx -- the component context
    data -- the bytes
    """
    return ctx.ServiceManager.createInstanceWithArgumentsAndContext(
        "com.sun.star.io.SequenceInputStream", (uno.ByteSequence(data),), ctx
    )


def _stream_out(properties: dict[str, Any]) -> Any:
    """Return the stream to write, or None.

    properties -- the MediaDescriptor, by name

    LibreOffice Developer's Guide, MediaDescriptor: "first check for a
    "Stream" property"; "if it isn't available, check for an
    "OutputStream" property".
    """
    if properties.get("Stream") is not None:
        return properties["Stream"].getOutputStream()
    return properties.get("OutputStream")


def _pipe(ctx: Any) -> Any:
    """Return a pipe, written and then read back, Pipe.

    ctx -- the component context
    """
    return ctx.ServiceManager.createInstanceWithContext("com.sun.star.io.Pipe", ctx)


class _LeftBehind(logging.Handler):
    """Collect the names in mtsv's reports of what was left behind."""

    def __init__(self) -> None:
        """Start with no names."""
        super().__init__()
        self.names: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the names of one report.

        record -- the report; mtsv's README: its left_behind attribute
        """
        self.names.extend(getattr(record, "left_behind", []))


def _report(indicator: Any, names: list[str]) -> None:
    """Show what was left behind as status text, XStatusIndicator.

    indicator -- the MediaDescriptor's StatusIndicator, or None
    names -- the names left behind, as mtsv reports them

    mtsv's README, What is left behind: "left behind: a, b".
    """
    if indicator is None or not names:
        return
    indicator.start("left behind: " + ", ".join(names), 0)
    indicator.end()


def _property(name: str, value: Any) -> Any:
    """Return a PropertyValue.

    name -- its Name
    value -- its Value
    """
    return uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue", Name=name, Value=value
    )


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(Filter, _IMPLEMENTATION, _SERVICES)
