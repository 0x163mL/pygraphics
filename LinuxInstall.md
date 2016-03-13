# Linux Installation Instructions #

  * If you do not already have Wing, you may wish to install it. Wing is the Python IDE that has been most thoroughly tested with `PyGraphics`. It is available here: http://wingware.com/downloads/wingide-101/3.2
  * Visit the Downloads page at http://code.google.com/p/pygraphics/downloads/list and download the file named 'PyGraphics-1.5.tar.gz'.
  * Extract the file using Ark (or another archive tool).
  * Open a console window. In the main pygraphics folder, install the setup file: 'python setup.py install'. Use sudo if you are not logged in as root.
  * Download and install `Nose`, `NumPy`, and `PyGame`, if you do not already have those packages. They are available via apt-get under the names python-nose, python-numpy, and python-pygame. In each case, 'apt-get install packagename'. **Note:** Nose is required only if you intend to use the test suite.
  * Download and install Python's Tk imaging package: 'apt-get install python-imaging-tk'.

Now you and `PyGraphics` should be ready to make beautiful music (and pictures!) together.