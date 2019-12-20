### Made by [@kilianvalkhof](https://twitter.com/kilianvalkhof)

#### Other projects:

- 💻 [Polypane](https://polypane.app) - Develop responsive websites and apps twice as fast on multiple screens at once
- 🖌️ [Superposition](https://superposition.design) - Kickstart your design system by extracting design tokens from your website
- 🗒️ [FromScratch](https://fromscratch.rocks) - A smart but simple autosaving scratchpad

---

# Trimage image compressor

A cross-platform tool for optimizing PNG and JPG files.

Trimage is a cross-platform GUI and command-line interface to optimize image files via [advpng](http://advancemame.sourceforge.net/comp-readme.html), [jpegoptim](http://www.kokkonen.net/tjko/projects.html), [optipng](http://optipng.sourceforge.net) and [pngcrush](https://pmt.sourceforge.io/pngcrush) depending on the
filetype (currently, PNG and JPG files are supported).
It was inspired by
[imageoptim](http://imageoptim.pornel.net).

All image files are losslessly
compressed on the highest available compression levels. Trimage gives you
various input functions to fit your own workflow: a regular file dialog,
dragging and dropping and various command line options.

## Installation instructions

Visit [Trimage.org](http://trimage.org) to install Trimage as a package.

## Building instructions

### Prerequisites

- PyQt5
- advpng
- jpegoptim
- optipng
- pngcrush

### Build from source

Build and install by running:

    python setup.py build
    sudo python setup.py install
