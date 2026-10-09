# -*- coding: utf-8 -*-
"""Images intégrées en data URI (src/images, préparées par outils/preparer-images.sh)."""
import base64
import pathlib
import struct

IMAGES = pathlib.Path(__file__).resolve().parent / "images"


def png(name):
    data = (IMAGES / f"{name}.png").read_bytes()
    w, h = struct.unpack(">II", data[16:24])
    return "data:image/png;base64," + base64.b64encode(data).decode(), w, h


def jpg(name):
    """Photo JPEG ; dimensions lues dans le segment SOF."""
    data = (IMAGES / f"{name}.jpg").read_bytes()
    i = 2
    while i < len(data):
        marker, size = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return "data:image/jpeg;base64," + base64.b64encode(data).decode(), w, h
        i += 2 + size
    raise ValueError(f"{name}.jpg : dimensions introuvables")


def image(name):
    """PNG ou JPEG selon le fichier présent."""
    return (jpg if (IMAGES / f"{name}.jpg").exists() else png)(name)
