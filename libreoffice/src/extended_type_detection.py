"""Confirm that a file of the MTSV type holds MTSV, for LibreOffice.

Classes:
ExtendedTypeDetection -- the DetectService of the MTSV type

Constants:
g_ImplementationHelper -- the implementation and the service it offers
"""

__all__ = ["ExtendedTypeDetection", "g_ImplementationHelper"]

import io
from typing import Any

import mtsv
import unohelper
from com.sun.star.document import XExtendedFilterDetection

from mtsv_office import IDENTIFIER, read

_IMPLEMENTATION = IDENTIFIER + ".ExtendedTypeDetection"
_SERVICES = ("com.sun.star.document.ExtendedTypeDetection",)
_TYPE = IDENTIFIER + ".MTSV"


class ExtendedTypeDetection(unohelper.Base, XExtendedFilterDetection):
    """The DetectService of the MTSV type.

    LibreOffice Developer's Guide, TypeDetection: a DetectService gets
    "a MediaDescriptor containing the name of the type to confirm and it
    will return this name in case it matches the content". It guesses
    nothing. draft-demosra-mtsv-01, Relationship to TSV: "A TSV file
    that contains no FF, and no CR other than in CRLF line breaks, is
    an MTSV file".
    """

    def __init__(self, ctx: Any, *args: Any) -> None:
        """Take the component context, which detection does not use.

        ctx -- the component context
        args -- the arguments of creation
        """

    def detect(self, descriptor: Any) -> tuple[str, Any]:
        """Confirm the MTSV type, XExtendedFilterDetection.

        descriptor -- the MediaDescriptor, a sequence of PropertyValue

        Return the MTSV type where it is the TypeName to confirm and
        mtsv reads the InputStream, else "", with the descriptor, which
        the [inout] parameter passes back.
        """
        properties = {item.Name: item.Value for item in descriptor}
        stream = properties.get("InputStream")
        if properties.get("TypeName") != _TYPE or stream is None:
            return "", descriptor
        data = read(stream)
        try:
            mtsv.load(io.BytesIO(data))
        except ValueError:
            return "", descriptor
        return _TYPE, descriptor


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ExtendedTypeDetection, _IMPLEMENTATION, _SERVICES
)
