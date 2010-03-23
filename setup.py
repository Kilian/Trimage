#!/usr/bin/env python

from distutils.core import setup

setup(name = "Trimage",
      version = "1.0.0b",
      description = "Trimage image compressor - A cross-platform tool for optimizing PNG and JPG files",
      author = "Kilian Valkhof, Paul Chaplin",
      author_email = "help@trimage.org",
      url = "http://trimage.org",
      license = "MIT license",
      packages = ["hurry", "hurry/filesize","ui",""],
      data_files = [("pixmaps", ["pixmaps/list-add.png",
                                 "pixmaps/view-refresh.png",
                                 "pixmaps/compressing.gif",
                                 "pixmaps/trimage-icon.png"])],
      scripts = ["trimage"],
      long_description = """Trimage is a cross-platform GUI and command-line interface to optimize image files via optipng, advpng and jpegoptim, depending on the filetype (currently, PNG and JPG files are supported). It was inspired by imageoptim. All image files are losslessy compressed on the highest available compression levels. Trimage gives you various input functions to fit your own workflow: A regular file dialog, dragging and dropping and various command line options.""",
      platforms = ["*nix", "mac", "windows"],
      requires = ["PyQt4 (>4.4)"],
      )
