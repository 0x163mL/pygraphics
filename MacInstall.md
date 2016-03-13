# Why Doesn't `PyGraphics` Work on OS X? #

Although a Mac version of `PyGraphics` exists, support is not currently available for Snow Leopard. If you are using an earlier version of OS X, `PyGraphics` should work for you; the Downloads page contains the appropriate installer.

The incompatibility with Snow Leopard is due to a change in the OS X `TkAqua` package which was released with it. The first call to `TkAqua` from within a threaded Python program must be made from the main thread, which is problematic when that program is itself being run by IDLE or Wing; in such cases, the IDE is controlling the main thread, and the program calling `TkAqua` does not have access to it. `PyGraphics` cannot call Tk from within the programs which run it, and because it relies on Tk to handle its imaging output, its picture-, color-, and pixel-manipulation methods result in errors.

`PyGraphics` will be made available for Snow Leopard once a suitable solution is found.

For a detailed description of the attempts which have been made to fix this problem to date, visit http://fourninetyfour.wordpress.com/2010/03/31/pygraphics-on-snow-leopard-fear-loathing-and-tk-x-11/. If you are a developer who has successfully dealt with similar Tk threading issues in OS X, please contact Sarah Nason at sarah.nason @ utoronto.ca.