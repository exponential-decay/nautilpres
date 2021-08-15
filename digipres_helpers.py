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
        if "md5" in hash_type.lower():
            return hashlib.md5()
        if "sha1" in hash_type.lower():
            return hashlib.sha1()
        if "sha256" in hash_type.lower():
            return hashlib.sha256()
        if "sha512" in hash_type.lower():
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
        """Return a boolean letting the caller know that the command
        was successful or unsuccessful.
        """
        try:
            sf_out = subprocess.check_output([WHICH_SF, "-json", file])
        except OSError:
            print("Siegfried not installed", file=sys.stderr)
            return False
        except subprocess.CalledProcessError:
            print("Error accessing file object", file=sys.stderr)
            return False
        try:
            files = json.loads(sf_out)
        except ValueError:
            print("Cannot parse SF data", file=sys.stderr)
            return False
        try:
            self.format_name = (
                files.get("files", [])[0].get("matches", [])[0].get("format", None)
            )
            version = (
                files.get("files", [])[0].get("matches", [])[0].get("version", None)
            )
            self.puid = files.get("files", [])[0].get("matches", [])[0].get("id", None)
            self.URI = files.get("files", [])[0].get("matches", [])[0].get("URI", None)
        except IndexError:
            print("Cannot access sf data for file:", file, file=sys.stderr)
            return False
        if version:
            self.format_name = "{} {}".format(self.format_name, version)
        if self.puid:
            if "fmt/" in self.puid:
                # PRNOM identifier, create a URI here.
                self.URI = "http://www.nationalarchives.gov.uk/PRONOM/{}".format(
                    self.puid
                )
            elif "fdd" in self.puid:
                # LoC identifier, create a URI here.
                self.URI = "https://www.loc.gov/preservation/digital/formats/fdd/{}.shtml".format(
                    self.puid
                )
        return True
