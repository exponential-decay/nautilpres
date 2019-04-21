#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Nautilus column extension to return digital preservation info.

1. Install: $ sudo apt-get install nautilus-python.
2. Then place this file in: ~/.local/share/nautilus-python/extensions
3. Copy digipres_helpers.py to the same folder as well.

When you use the list view in Nautilus you will be presented with some
information about you files that will be useful for digital preservation. Some
information will be useful and appraisal and selection as well.

Resources:
    - Extension docs: https://projects-old.gnome.org/nautilus-python/documentation/html/index.html
    - Media example: https://github.com/atareao/nautilus-columns
    - Nautilus examples: https://github.com/GNOME/nautilus-python/tree/13d40c16dbf2df4dd007ae7961aa86aa235c8020/examples
"""

from __future__ import print_function, unicode_literals

try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

from digipres_helpers import HashHandler, SiegfriedRunner

from gi.repository import GObject, Nautilus


class ColumnExtension(GObject.GObject, Nautilus.ColumnProvider, Nautilus.InfoProvider):
    """Column extension subclass for Nautilus."""

    def __init__(self):
        """Class constructor."""
        pass

    def get_columns(self):
        """Return the customized columns to nautilus."""
        return (
            Nautilus.Column(
                name="NautilusPython::puid_column",
                attribute="puid",
                label="Format ID",
                description="Format identifier according to PRONOM",
                xalign=1,
                default_sort_order=0,
            ),
            Nautilus.Column(
                name="NautilusPython::format_name_column",
                attribute="format_name",
                label="Format Name",
                description="Format name according to PRONOM",
                xalign=0,
                default_sort_order=0,
            ),
            Nautilus.Column(
                name="NautilusPython::checksum_column",
                attribute="checksum",
                label="Checksum",
                description="Checksum value",
                xalign=1,
                default_sort_order=0,
            ),
        )

    def update_file_info(self, file):
        """Update information about the file to be displayed by nautilus."""
        if file.get_uri_scheme() != "file":
            return
        if file.is_directory():
            return
        file_name = unquote(file.get_uri()[7:])
        puid, format_name = SiegfriedRunner().get_format_puid_pair(file_name)
        # If we haven't returned something sensible from Siegfried still print
        # something useful to nautilus. Debug may be necessary if we keep
        # seeing None.
        if puid is None:
            puid = "None"
            format_name = "None"
        file.add_string_attribute("puid", puid)
        file.add_string_attribute("format_name", format_name)
        file.add_string_attribute("checksum", HashHandler().get_hash(file_name, "md5"))
        return self.get_columns()
