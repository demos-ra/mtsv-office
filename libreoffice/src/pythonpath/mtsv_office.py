"""What the extension's two components share.

Functions:
read -- return every byte left in an input stream

Constants:
IDENTIFIER -- the extension identifier, the prefix of its unique names
"""

__all__ = ["read", "IDENTIFIER"]

import io
from typing import Any

# LibreOffice Developer's Guide, Extension Identifiers: the same prefix
# applies to "all unique names in configuration files of extensions".
IDENTIFIER = "io.github.demos-ra.mtsv-office"


def read(stream: Any) -> bytes:
    """Return every byte left in an XInputStream, by readBytes.

    stream -- the input stream
    """
    chunks = []
    while True:
        count, data = stream.readBytes(None, io.DEFAULT_BUFFER_SIZE)
        if not count:
            return b"".join(chunks)
        chunks.append(data.value)
