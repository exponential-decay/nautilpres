#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Digital preservation helper functions.

    - Ensure Siegfried is installed.
    - Ensure that it has at least one format matcher, e.g. ($ sf -update)
"""

from __future__ import print_function, unicode_literals
import hashlib
import json
import subprocess
import sys


# Populate this with the result of $ which sf.
#
WHICH_SF = "/home/<user>/git/go/bin/sf"


class HashHandler(object):
    """Encapsulate functions associated with returning a checksum for an
    input file."""

    BLOCKSIZE = 65536

    def _get_hash_func(self, hash_type):
        """Return an appropriate hash function if we want to choose something
        different.
        """
        if "md5" in hash_type:
            return hashlib.md5()
        if "sha1" in hash_type:
            return hashlib.sha1()
        if "sha256" in hash_type:
            return hashlib.sha256()
        if "sha512" in hash_type:
            return hashlib.sha512()

    def get_hash(self, file_name, hash_type):
        """Return a checksum for a given file."""
        hash_func = self._get_hash_func(hash_type)
        with open(file_name, "rb") as file:
            buf = file.read(self.BLOCKSIZE)
            while len(buf) > 0:
                hash_func.update(buf)
                buf = file.read(self.BLOCKSIZE)
        return hash_func.hexdigest()


class SiegfriedRunner(object):
    """Encapsulate the functions we're going to use from Siegfried."""

    def get_format_puid_pair(self, file):
        """Return a tuple with some information about our file format."""
        try:
            sf_out = subprocess.check_output([WHICH_SF, "-json", file])
        except OSError:
            print("Siegfried not installed", file=sys.stderr)
            return (None, None)
        except subprocess.CalledProcessError:
            print("Error accessing file object", file=sys.stderr)
            return (None, None)
        try:
            files = json.loads(sf_out)
        except ValueError:
            print("Cannot parse SF data", file=sys.stderr)
            return (None, None)
        try:
            format_name = (
                files.get("files", [])[0].get("matches", [])[0].get("format", "None")
            )
            version = (
                files.get("files", [])[0].get("matches", [])[0].get("version", "None")
            )
            puid = files.get("files", [])[0].get("matches", [])[0].get("id", "None")
        except IndexError:
            print("Cannot access sf data for file:", file, file=sys.stderr)
            return (None, None)
        if version:
            return (puid, "{} {}".format(format_name, version))
        return (puid, format_name)
