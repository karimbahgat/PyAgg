"""
# PyAgg

PyAgg is a precompiled Python library for lightweight, easy, and convenient graphics
rendering based on the aggdraw module.


## Motivation

There are several ways to create high quality 2D drawings and graphics in Python. The widely used
Matplotlib library is a favorite for advanced scientific visualizations, but for
simpler drawing uses, its size, dependencies, and steep learning curve can be a bit
overkill. PyCairo is another library, but unfortunately it suffers some from slow
drawing and a stateful API that leads to longer code. Finally, Aggdraw is simple and
intuitive, but has slightly limited functionality, is no longer maintained, and precompiled
binaries are hard to come by. 

The current library, PyAgg, aims to solve some of these problems. By building on the lightweight
aggdraw module and including the necessary pre-compiled binaries for multiple Python and
architecture versions in the same package, PyAgg is ready to use out of the box, no
installation or compiling required. It is very fast and produces high quality antialiased
drawings. Most importantly, PyAgg wraps around and offers several convenience functions for
easier no-brain drawing and data visualization, including flexible handling of coordinate
systems and length units.

Here is to at least another 5 years of beautiful and lightweight AGG image drawing.
Cheers! After that, Python 2x will no longer be maintained, and while people can
still continue to use it, it is likely that most people will be using Python 3x. At
that point someone will have to update the C++ Aggdraw wrapper so it can be compiled
for Python 3x if Python users are to continue to enjoy the power of the Agg graphics
library.


## Features

The main features of PyAgg include:

- A coordinate aware image. No need for the intricacies of affine matrix transformations, just define the
coordinates that make up each corner of your image once, and watch it follow as you
resize, crop, rotate, move, and paste the image. Zoom in and out of you coordinate system by bounding box, factor,
or units, and lock the aspect ratio to avoid distortions.
- Oneliners to easily draw and style high quality graphical elements including polygons with holes, lines with or
without smooth curves, pie slices, and point symbols like circles, squares, and triangles with an optional flattening factor.
- Style your drawing sizes and distances in several types of units, including pixels, percentagea, cm, mm, inches, and
font points, by specifying the real world size of your image.
- Smart support for text writing, including text anchoring, and automatic detection of available fonts. 
- Instantly view your image in a Tkinter pop up window, or prepare it for use in a Tkinter application. 

There is also support for common domain specific data visualization:

- Partial support for geographical plotting, including a lat-long coordinate system, and automatic drawing of
GeoJSON features. 
- Easily plot statistical data on graphs witn a syntax and functionality that is aimed more for data analysts and laymen than
computer scientists, including linegraph, scatterplot, histogram, etc, although these are still a work in progress. 


## Platforms

Python 2.6 and 2.7

PyAgg relies on the aggdraw Python C++ wrapper, and as a convenience comes with
aggdraw precompiled for the following platforms:

- Python 2.6 (Windows: 32-bit only, Mac and Linux: No support)
- Python 2.7 (Windows: 32 and 64-bit, Mac and Linux: 64-bit only)

Note: Mac and Linux support has not been fully tested, and there are some reports of
problems on Linux. 

You can get around these limitations by compiling aggdraw on your own, in which case
PyAgg should work on any machine that you compile for.


## Dependencies

PIL/Pillow (used for image loading, saving, and manipulation. Also used for text-rendering,
which means if you compile PIL/Pillow on your own make sure FreeType support is enabled)


## Installing it

PyAgg is installed with pip from the commandline:

    pip install pyagg

It also works to just place the "pyagg" package folder in an importable location like 
"site-packages". 


## Example Usage

Begin by importing the pyagg module:

    import pyagg

To begin drawing, create your canvas instance and define its coordinate system, in this
case based on percentages to easily draw using relative positions. In our case
we give our image the size of an A4 paper, and specify that all further drawing in real
world units should use 96 pixels per inch:

    canvas = pyagg.Canvas("210mm", "297mm", background=(222,222,222), ppi=96)
    canvas.percent_space()

Next, draw some graphical elements:

    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize="2cm")

    canvas.draw_triangle((50,50),fillsize="30px", fillcolor=(0,0,0, 111))

And some text:

    canvas.draw_text((50,50),"PyAgg is for drawing!",
                    textanchor="center",
                    textfont="Segoe UI",
                    textsize=42)

Once you are done, view or save your image:

    canvas.save("test.png")
    canvas.view()


## More Information:

The above was just a very small example of what you can do with PyAgg.
But until I get around to making the full tutorial just check out the
API documentation below. 

- [Home Page](http://github.com/karimbahgat/PyAgg)
- [API Documentation](http://pythonhosted.org/PyAgg)


## License:

This code is free to share, use, reuse,
and modify according to the MIT license, see license.txt


## Credits:

Karim Bahgat (2020)
"""

__version__ = "0.3.0"

from .canvas import Canvas, load
from .graph import LineGraph
