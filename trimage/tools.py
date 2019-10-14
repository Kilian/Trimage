#!/usr/bin/env python3

import sys
import errno
from subprocess import call, PIPE


def check_dependencies():
    """Check if the required command line apps exist."""
    status = True
    dependencies = {
        "jpegoptim": "--version",
        "optipng": "-v",
        "advpng": "--version",
        "pngcrush": "-version"
    }

    for elt in dependencies:
        retcode = safe_call(elt + " " + dependencies[elt])
        if retcode != 0:
            status = False
            print("[error] please install {}".format(elt), file=sys.stderr)

    return status


def safe_call(command):
    """Cross-platform command-line check."""
    while True:
        try:
            return call(command, shell=True, stdout=PIPE)
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise


def human_readable_size(num, suffix="B"):
    """Bytes to a readable size format"""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Y", suffix)
