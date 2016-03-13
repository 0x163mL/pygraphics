# Introduction #

The University of Toronto is probably going to only be doing image processing.  The pygame and Tkinter dependencies are proving to be a problem because of the mainloop issue; it would be nice to switch to using only PIL.

Also, it would be nice to switch to using [Guido's style guide](http://www.python.org/dev/peps/pep-0008/).

# Details #

Reformat code to fit [Guido's style guide](http://www.python.org/dev/peps/pep-0008/).  The big changes are:

  * Switch to `pothole_case`.  (As opposed to `camelCase`.)
  * Switch to 0-based indexing.

Rewrite the basic image processing stuff to use only PIL.  This includes pickAFile, makePicture, etc.  The basic idea is that we want something like this to work:

```
f = pick_file()
m = make_picture(f)
for p in get_pixels(m):
    make_darker(p)
```