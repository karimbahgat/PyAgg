"""
Defines the PyAgg Canvas class, where most of the PyAgg functinoality is defined. 
"""

##############################
# Startup and imports

# Import future stuff
from __future__ import division

# Import dependencies
import PIL, PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageFont
import PIL.ImageOps, PIL.ImageChops, PIL.ImageMath, PIL.ImageEnhance

# Import builtins
import sys, os
import Tkinter as tk
import struct
import itertools
import random
import traceback
import warnings
import textwrap
import math

# Import submodules
PYAGGFOLDER = os.path.split(__file__)[0]
from . import affine
from . import units
from . import bboxhelper
from . import fonthelper
from . import gridinterp

##############################
# Determine OS and bitsystem
OSSYSTEM = {"win32":"windows",
             "darwin":"mac",
             "linux":"linux",
             "linux2":"linux"}[sys.platform]
PYVERSION = sys.version[:3]
if sys.maxsize == 9223372036854775807: PYBITS = "64"
else: PYBITS = "32"

##############################     
# Import correct AGG binaries
try:
    if OSSYSTEM == "windows":
        if PYBITS == "32":
            if PYVERSION == "2.6":
                try: from .precompiled.win.bit32.py26 import aggdraw
                except:
                    sys.path.insert(0, PYAGGFOLDER+"/precompiled/win/bit32/py26")
                    import aggdraw
                    sys.path = sys.path[1:] # remove previously added aggdraw path
            elif PYVERSION == "2.7":
                try: from .precompiled.win.bit32.py27 import aggdraw
                except:
                    sys.path.insert(0, PYAGGFOLDER+"/precompiled/win/bit32/py27")
                    import aggdraw
                    sys.path = sys.path[1:] # remove previously added aggdraw path
        elif PYBITS == "64":
            if PYVERSION == "2.6":
                raise ImportError("Currently no Windows precompilation for 64-bit Py26")
            elif PYVERSION == "2.7":
                try: from .precompiled.win.bit64.py27 import aggdraw
                except:
                    sys.path.insert(0, PYAGGFOLDER+"/precompiled/win/bit64/py27")
                    import aggdraw
                    sys.path = sys.path[1:] # remove previously added aggdraw path
    elif OSSYSTEM == "mac":
        if PYBITS == "32":
            raise ImportError("Currently no Mac precompilation for 32-bit Py26 or Py27")
        elif PYBITS == "64":
            if PYVERSION == "2.6":
                raise ImportError("Currently no Mac precompilation for 64-bit Py26")
            elif PYVERSION == "2.7":
                try: from .precompiled.mac.bit64.py27 import aggdraw
                except:
                    sys.path.insert(0, PYAGGFOLDER+"/precompiled/mac/bit64/py27")
                    import aggdraw
                    sys.path = sys.path[1:] # remove previously added aggdraw path
    elif OSSYSTEM == "linux":
        raise ImportError("Currently no Linux precompilation for any version or bit system")
except ImportError:
    import aggdraw # in case user has compiled a working aggdraw version on their own






##############################
# Some convenience functions

def _grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=None, *args)

def _pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def _floatrange(start, end, interval):
    # force interval input to be positive
    if interval < 0:
        interval *= -1
    # count forward
    if start < end:
        cur = start
        while cur < end:
            yield cur
            cur += interval
    # or backwards
    else:
        cur = start
        while cur > end:
            yield cur
            cur -= interval






##############################
# Main class

class Canvas:
    """
    An image that knows how to draw on itself and keep track of its
    coordinate system.

    Attributes:

    - *width*:
        Pixel width of canvas image
    - *height*:
        Pixel height of canvas image
    - *ppi*:
        Pixels per inch. Used to calculate pixels needed for real world sizes. 
    - *default_unit*:
        How to interpret sizes given as just a number.
    - *coordspace_bbox*:
        Bounding box of the canvas coordinate system as a list 
        containing 4 floats [xmin, ymin, xmax, ymax].
    - *coordspace_width*:
        Width of the canvas coordinate system, as the difference
        between xmin and xmax. 
    - *coordspace_height*:
        Height of the canvas coordinate system, as the difference
        between ymin and ymax. 
    - *coordspace_units*:
        The number of coordinate space units per 1 cm screen width. 
    - *coordspace_transform*:
        A list of 6 floats representing the affine transform
        coefficients used to transform input coordinates to the drawing coordinate system. 
    """
    def __init__(self, width, height, background=None, mode="RGBA", ppi=300):
        """
        Creates a new blank canvas image. 

        Parameters:
        
        - *width*:
            Width of the canvas image. Value can be an integer for number of
            pixels. Value can also be any valid string size: in, cm, or mm. In the latter
            case uses the ppi setting (pixels per inch) to calculate the
            pixel width/height equivalent, because pixels are distance agnostic.
        - *height*:
            Height of the canvas image. Same values as width. 
        - *background* (optional):
            The color of the background image.
            Value should be an RGB or RGB tuple, or an aggdraw color name that matches the
            image mode. Defaults to None (transparent). 
        - *mode* (optional):
            any of PIL's image modes, typically 'RGBA' (default) or 'RGB'. 
        - *ppi* (optional):
            Pixels per inch. Defaults to publication quality of 300. Its only effect
            is that it calculates the correct pixels whenever you use a real world
            size such as cm, mm, in, or pt. When you use pixel units directly or %, the ppi has
            no effect. This means that if ppi matters to you, you should initiate
            the canvas width and height using real world sizes, and draw all sizes using
            real world sizes as well. Ppi should only be set at initiation time.
        """
        # unless specified, interpret width and height as pixels
        width = units.parse_dist(width, default_unit="px", ppi=ppi)
        height = units.parse_dist(height, default_unit="px", ppi=ppi)
        width,height = int(round(width)),int(round(height))
        # create image
        self.img = PIL.Image.new(mode, (width, height), background)
        # create drawer
        self.drawer = aggdraw.Draw(self.img)
        # remember info
        self.background = background
        self.ppi = ppi
        # by default, interpret all sizes in % of width
        self.default_unit = "%w"
        # and baseline textsize as 8 for every 97 inch of ppi
        self.default_textoptions = {"font":"Calibri",
                                    "textcolor":(0,0,0),
                                    "textsize":int(round(8 * (self.ppi / 97.0))),
                                    "anchor":"center", "justify":"center"}
        # maybe also have default general drawingoptions
        # ...
        # maybe also have default colorcycle
        # ...
        # by default, interpret all coordinates in pixel space
        self.pixel_space()

    @property
    def width(self):
        return self.drawer.size[0]

    @property
    def height(self):
        return self.drawer.size[1]








    # Image operations

    def resize(self, width, height, lock_ratio=False, fit=True):
        """
        Resize canvas image to new width and height in pixels or other units,
        and the coordinate system will follow, so that each corner
        in the old image is equivalent to each corner in the new image.

        Parameters:

        - *width*:
            Width of the new image. Can be specified with any unit with a string representation. Otherwise defaults to pixels. 
        - *height*:
            Height of the new image. Can be specified with any unit with a string representation. Otherwise defaults to pixels. 
        - *lock_ratio* (optional):
            Whether to modify the given sizes to preserve the
            width/height ratio of the original image. Default is False. 

        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls. 
        """
        # Resize image
        self.drawer.flush()
        width = units.parse_dist(width,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        height = units.parse_dist(height,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        if lock_ratio:
            # see: http://stackoverflow.com/questions/9103257/resize-image-maintaining-aspect-ratio-and-making-portrait-and-landscape-images-e
            img = self.img.copy()
            img.thumbnail((width,height), PIL.Image.ANTIALIAS)
            oldwidth,oldheight = img.size

            # FINAL TODO: newbbox coords not correct yet...
            if fit:
                thumb = img.crop( (0, 0, width, height) )

                offset_x = max([ (width - oldwidth) / 2.0, 0 ])
                offset_y = max([ (height - oldheight) / 2.0, 0 ])

                self.img = PIL.ImageChops.offset(thumb, int(offset_x), int(offset_y))
                newbbox = self.coordspace_bbox
                newbbox = bboxhelper.conform_aspect(newbbox, width, height, fit=True)

            else:
                self.img = PIL.ImageOps.fit(img, (width,height), PIL.Image.ANTIALIAS, (0.5, 0.5))
                newbbox = self.coordspace_bbox
                newbbox = bboxhelper.conform_aspect(newbbox, width, height, fit=False)
        
        else:
            self.img = self.img.resize((width, height), PIL.Image.ANTIALIAS)
            newbbox = self.coordspace_bbox
        # apply
        self.update_drawer_img()
        # Then update coordspace to match the new image dimensions
        self.custom_space(*newbbox, lock_ratio=False)
        return self

    def rotate(self, degrees):
        """
        Rotate the canvas image in degree angles,
        and the coordinate system will follow.

        Parameters:

        - *degrees*: Degree angles to rotate. 0 degrees faces upwards and increases
            clockwise.
            
        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls. 
        """
        self.drawer.flush()
        self.img = self.img.rotate(degrees, PIL.Image.BICUBIC, expand=0)
        self.update_drawer_img()
        # Somehow update the drawtransform/coordspace to follow the image change operation
        # Rotate around the midpoint
        # Useful: http://www.euclideanspace.com/maths/geometry/affine/aroundPoint/
        # To do: Allow expand option to include all the rotated image and coordspace...
        # To fix: Some shearing effects of drawing objects vs the rotated background color image
        midx = self.coordspace_bbox[0] + self.coordspace_width/2.0
        midy = self.coordspace_bbox[1] + self.coordspace_height/2.0
        orig = affine.Affine(*self.coordspace_transform)
        rotated = orig * (affine.Affine.translate(midx,midy) * affine.Affine.rotate(degrees) * affine.Affine.translate(-midx,-midy))
        # remember the new coordinate extents and affine matrix
        self.coordspace_transform = rotated.coefficients
        # offset bbox
        x1,y1,x2,y2 = 0,0,self.width,self.height
        x1,y1 = self.pixel2coord(x1, y1)
        x2,y2 = self.pixel2coord(x2, y2)
        self.coordspace_bbox = [x1,y1,x2,y2]
        # apply
        self.update_drawer_img()
        return self

##    def skew(self):
##        """
##        Skew the canvas image in pixels,
##        and the coordinate system will follow.
##        """
##        pass

    def flip(self, xflip=True, yflip=False):
        """
        Flip the canvas image horizontally or vertically (center-anchored),
        and the coordinate system will follow.

        Parameters:

        - *xflip* (optional): Flips the image horizontally if set to True. Default is True. 
        - *yflip* (optional): Flips the image vertically if set to True. Default is False. 

        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls. 
        """
        self.drawer.flush()
        img = self.img
        if xflip: img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        if yflip: img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.img = img
        self.update_drawer_img()
        # Somehow update the drawtransform/coordspace to follow the image change operation
        orig = affine.Affine(*self.coordspace_transform)
        if xflip and yflip: flipfactor = affine.Affine.translate(self.coordspace_width,self.coordspace_height) * affine.Affine.flip(xflip, yflip)
        elif xflip: flipfactor = affine.Affine.translate(self.coordspace_width,0) * affine.Affine.flip(xflip, yflip)
        elif yflip: flipfactor = affine.Affine.translate(0,self.coordspace_height) * affine.Affine.flip(xflip, yflip)
        flipped = orig * flipfactor
        print flipped
        # remember the new coordinate extents and affine matrix
        self.coordspace_transform = flipped.coefficients
        # offset bbox
        x1,y1,x2,y2 = 0,0,self.width,self.height
        x1,y1 = self.pixel2coord(x1, y1)
        x2,y2 = self.pixel2coord(x2, y2)
        self.coordspace_bbox = [x1,y1,x2,y2]
        # apply
        self.update_drawer_img()
        return self

    def move(self, xmove, ymove):
        """
        Move/offset the canvas image in pixels or other units,
        and the coordinate system will follow.

        Parameters:

        - *xmove*: Moves/offsets the image horizontally.
            Can be specified with any unit with a string representation. Otherwise defaults to pixels. 
        - *ymove*: Moves/offsets the image vertically.
            Can be specified with any unit with a string representation. Otherwise defaults to pixels. 

        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls.
        """
        # convert units to pixels
        xmove = units.parse_dist(xmove,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        ymove = units.parse_dist(ymove,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        # paste self on blank at offset pixel coords
        self.drawer.flush()
        blank = PIL.Image.new(self.img.mode, self.img.size, None)
        blank.paste(self.img, (int(xmove), int(ymove)))
        self.img = blank
        # similarly move the drawing transform
        # by converting pixels to coord distances
        def pixel2coord_dist(x, y):
            # SHOULD BE REMOVED, NEED INSTEAD A PIXEL TO COORDINATE UNIT CONVERTER (units.py is only coords 2 pixel)?
            # Added units.px_to_coord() so maybe try that...
            # partly taken from Sean Gillies "affine.py"
            a,b,c,d,e,f = self.coordspace_transform
            det = a*e - b*d
            idet = 1 / float(det)
            ra = e * idet
            rb = -b * idet
            rd = -d * idet
            re = a * idet
            newx = (x*ra) # only considers xoffset
            newy = (y*re) # only considers yoffset
            return newx,newy
        xmove,ymove = pixel2coord_dist(xmove, ymove)   # REDO LATER
        orig = affine.Affine(*self.coordspace_transform)
        moved = orig * affine.Affine.translate(xmove,ymove)
        self.drawer = aggdraw.Draw(self.img)
        self.drawer.settransform(moved.coefficients)
        # remember the new coordinate extents and affine matrix
        self.coordspace_transform = moved.coefficients
        # offset bbox
        x1,y1,x2,y2 = 0,0,self.width,self.height
        x1,y1 = self.pixel2coord(x1, y1)
        x2,y2 = self.pixel2coord(x2, y2)
        self.coordspace_bbox = [x1,y1,x2,y2]
        # apply
        self.update_drawer_img()
        return self

    def paste(self, image, xy=(0,0), bbox=None, lock_ratio=True, fit=True, anchor="nw", outlinewidth="1px", outlinecolor="black"):
        """
        Paste a PIL image or PyAgg canvas
        onto a given location in the Canvas.

        Parameters:

        - *image*: PIL image or PyAgg canvas to paste.
        - *xy*: An xy point tuple of the location to paste the northwest corner of the image.
            Can be specified with any unit with a string representation. Otherwise defaults to pixels.
        - *bbox*: ...
        - *lock_ratio*: ...
        - *fit*: ...
        - *anchor*: What part of the image to anchor at the xy point. Can be any compass direction
            n,ne,e,se,s,sw,w,nw, or center.
        - *outlinewidth*: ...
        - *outlinecolor*: ...

        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls.
        """
        self.drawer.flush()
        if isinstance(image, Canvas): image = image.img
        
        if bbox:
            x1,y1,x2,y2 = bbox
            x1,y1 = self.coord2pixel(x1,y1)
            x2,y2 = self.coord2pixel(x2,y2)
            xs,ys = (x1,x2),(y1,y2)
            bbwidth = max(xs) - min(xs)
            bbheight = max(ys) - min(ys)
            image = from_image(image).resize(bbwidth,bbheight,lock_ratio=lock_ratio,fit=fit).img

            # ensure old and zoom axes go in same directions
            xleft, ybottom, xright, ytop = x1,y1,x2,y2
            oldxleft, oldytop, oldxright, oldybottom = self.coordspace_bbox
            if not (xleft < xright) == (oldxleft < oldxright):
                xleft,xright = xright,xleft
            if not (ytop < ybottom) == (oldytop < oldybottom):
                ytop,ybottom = ybottom,ytop            
            xy = xleft,ytop
            
        elif xy:
            # Parse xy location from any type of unit to pixels
            x,y = xy
            x = units.parse_dist(x,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
            y = units.parse_dist(y,
                                 ppi=self.ppi,
                                 default_unit="px",
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
            
            # Anchor
            width,height = image.size
            anchor = anchor.lower()
            if anchor == "center":
                x = int(x - width/2.0)
                y = int(y - height/2.0)
            else:
                x = int(x - width/2.0)
                y = int(y - height/2.0)
                if "n" in anchor:
                    y = int(y + height/2.0)
                elif "s" in anchor:
                    y = int(y - height/2.0)
                if "e" in anchor:
                    x = int(x - width/2.0)
                elif "w" in anchor:
                    x = int(x + width/2.0)
            xy = (x,y)
            bbox = [x,y,x+width,y+height]

        ###
        if image.mode == "RGBA":
            self.img.paste(image, xy, image) # paste using self as transparency mask
        else: self.img.paste(image, xy)
            
        # apply
        self.update_drawer_img()
      
        # outline
        if outlinewidth and outlinecolor:
            self.draw_box(bbox=bbox, fillcolor=None, outlinewidth=outlinewidth, outlinecolor=outlinecolor)
        
        return self

    def crop(self, xmin, ymin, xmax, ymax):
        """
        Crop the canvas image to a bounding box defined in pixel coordinates,
        and the coordinate system will follow.
        Essentially just an alias for zoom_bbox(), except lock_ratio
        is set to False by default.

        Parameters:

        - *xmin*: The lower bound of the x-axis after the zoom.
        - *ymin*: The lower bound of the y-axis after the zoom.
        - *xmax*: The higher bound of the x-axis after the zoom.
        - *ymax*: The higher bound of the y-axis after the zoom.

        Returns:
        
        - In addition to changing the original instance, this method returns
            the new instance to allow for linked method calls.
        """
        self.drawer.flush()

        # ensure old and zoom axes go in same directions
        xleft, ybottom, xright, ytop = xmin,ymin,xmax,ymax
        oldxleft, oldytop, oldxright, oldybottom = self.coordspace_bbox
        if not (xleft < xright) == (oldxleft < oldxright):
            xleft,xright = xright,xleft
        if not (ytop < ybottom) == (oldytop < oldybottom):
            ytop,ybottom = ybottom,ytop            

        pxleft,pytop = self.coord2pixel(xleft,ytop)
        pxright,pybottom = self.coord2pixel(xright,ybottom)

        self.img = self.img.crop((pxleft,pytop,pxright,pybottom))
        self.update_drawer_img()
        
        self.custom_space(xleft,ytop,xright,ybottom, lock_ratio=False)

        return self        

    def update_drawer_img(self):
        """
        Updates any image changes to the drawer, and reapplies the transform to the new
        image size. Mostly used internally, but can be useful if you apply any PIL operations
        directly to the canvas image (the .img attribute). 
        """
        self.drawer = aggdraw.Draw(self.img)
        self.drawer.settransform(self.coordspace_transform)








    # Color quality

    def brightness(self, factor):
        self.drawer.flush()
        self.img = PIL.ImageEnhance.Brightness(self.img).enhance(factor)
        self.update_drawer_img()
        return self

    def contrast(self, factor):
        self.drawer.flush()
        self.img = PIL.ImageEnhance.Contrast(self.img).enhance(factor)
        self.update_drawer_img()
        return self

    def blur(self, factor):
        self.drawer.flush()
        factor = 1 - factor # input is 0-1, PIL expects 0-1.
        self.img = PIL.ImageEnhance.Sharpness(self.img).enhance(factor)
        self.update_drawer_img()
        return self

    def sharpen(self, factor):
        self.drawer.flush()
        factor += 1 # input is 0-1, PIL expects 1-2.
        self.img = PIL.ImageEnhance.Sharpness(self.img).enhance(factor)
        self.update_drawer_img()
        return self

    def equalize(self):
        self.drawer.flush()
        self.img = PIL.ImageOps.equalize(self.img)
        self.update_drawer_img()
        return self

    def invert(self):
        self.drawer.flush()
        self.img = PIL.ImageOps.invert(self.img)
        self.update_drawer_img()
        return self
        
    def transparency(self, alpha):
        self.drawer.flush()
##        blank = PIL.Image.new(self.img.mode, self.img.size, None)
##        self.img = blank.paste(self.img, (0,0), alpha)
        self.img.putalpha(alpha)
        self.update_drawer_img()
        return self

    def transparent_color(self, color, alpha=0, tolerance=0):
        # make all specified color values transparent (alpha)
        # ...alternatively with a tolerance for almost matching colors
        self.drawer.flush()
        
        if tolerance == 0:
            image = self.img.convert("RGBA")
            r,g,b,a = image.split()
            red_mask = r.point(lambda px: alpha if px == color[0] else 255, "L")
            green_mask = g.point(lambda px: alpha if px == color[1] else 255, "L")
            blue_mask = b.point(lambda px: alpha if px == color[2] else 255, "L")
            all_mask = PIL.ImageMath.eval("convert(r | g | b, 'L')", r=red_mask, g=green_mask, b=blue_mask)
            image.putalpha(all_mask)
        else:
            image = self.img.convert("RGBA")
            r,g,b,a = image.split()
            tolerance = 255 * tolerance
            def diff(a, b):
                # absolute positive diff
                if a >= b:
                    _diff = a - b
                else:
                    _diff = b - a
                return _diff 
            red_diff = r.point(lambda px: diff(px,color[0]), "L")
            green_diff = g.point(lambda px: diff(px,color[1]), "L")
            blue_diff = b.point(lambda px: diff(px,color[2]), "L")
            avg_diff = PIL.ImageMath.eval("convert((r+g+b) / 3.0, 'L')",
                                          r=red_diff, g=green_diff, b=blue_diff)
            all_mask = avg_diff.point(lambda px: alpha if px <= tolerance else 255)
            image.putalpha(all_mask)

            # from: http://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent
##            def distance(a, b):
##                return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])
##            image = self.img.convert("RGBA")
##            red, green, blue, alpha = image.split()
##            image.putalpha(PIL.ImageMath.eval("""convert(((((t - d(c, (r, g, b))) >> 31) + 1) ^ 1) * a, 'L')""",
##                t=tolerance, d=distance, c=color, r=red, g=green, b=blue, a=alpha))
            
        self.img = image
        self.update_drawer_img()
        return self

    def replace_color(self, color, newcolor, tolerance=0):
        # replace all specified color values with another color
        # ...alternatively with a tolerance for almost matching colors
        self.drawer.flush()
        
        if tolerance == 0:
            image = self.img.convert("RGBA")
            r,g,b,a = image.split()
            red_mask = r.point(lambda px: 0 if px == color[0] else 255, "L")
            green_mask = g.point(lambda px: 0 if px == color[1] else 255, "L")
            blue_mask = b.point(lambda px: 0 if px == color[2] else 255, "L")
            all_mask = PIL.ImageMath.eval("convert(r | g | b, 'L')", r=red_mask, g=green_mask, b=blue_mask)
            image.putalpha(all_mask)
        else:
            image = self.img.convert("RGBA")
            r,g,b,a = image.split()
            tolerance = 255 * tolerance # tolerance is 0-1
            def diff(a, b):
                # absolute positive diff
                if a >= b:
                    _diff = a - b
                else:
                    _diff = b - a
                return _diff 
            red_diff = r.point(lambda px: diff(px,color[0]), "L")
            green_diff = g.point(lambda px: diff(px,color[1]), "L")
            blue_diff = b.point(lambda px: diff(px,color[2]), "L")
            avg_diff = PIL.ImageMath.eval("convert((r+g+b) / 3.0, 'L')",
                                          r=red_diff, g=green_diff, b=blue_diff)
            all_mask = avg_diff.point(lambda px: 0 if px <= tolerance else 255)
            image.putalpha(all_mask)

        newimg = PIL.Image.new("RGB", image.size, newcolor)
        newimg.paste(image, (0,0), image)

        self.img = newimg
        self.update_drawer_img()
        return self

    def color_tint(self, color):
        # add rgb color to each pixel
        # from: http://stackoverflow.com/questions/12251896/colorize-image-while-preserving-transparency-with-pil
        self.drawer.flush()
        r, g, b, alpha = self.img.split()
        gray = PIL.ImageOps.grayscale(self.img)
        result = PIL.ImageOps.colorize(gray, (0, 0, 0, 0), color) 
        result.putalpha(alpha)
        self.img = result
        self.update_drawer_img()
        return self

    def color_remap(self, gradient):
        # convert to grayscale and recolor based on input gradient
        # experimental...
        self.drawer.flush()

        # interpolate gradient
        # http://bsou.io/posts/color-gradients-with-python
        
        def linear_gradient(fromrgb, torgb, n=10):
            ''' returns a gradient list of (n) colors between
            two hex colors. start_hex and finish_hex
            should be the full six-digit color string,
            inlcuding the number sign ("#FFFFFF") '''
            # Starting and ending colors in RGB form
            s = fromrgb
            f = torgb
            # Initilize a list of the output colors with the starting color
            RGB_list = [s]
            # Calcuate a color at each evenly spaced value of t from 1 to n
            for t in range(1, n):
            # Interpolate RGB vector for color at the current value of t
                curr_vector = [
                int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
                for j in range(3)
                ]
                # Add it to our list of output colors
                RGB_list.append(curr_vector)
            return RGB_list

        def polylinear_gradient(colors, n):
            ''' returns a list of colors forming linear gradients between
              all sequential pairs of colors. "n" specifies the total
              number of desired output colors '''
            # The number of colors per individual linear gradient
            n_out = int(float(n) / (len(colors) - 1))
            final_gradient = []
            # returns dictionary defined by color_dict()
            prevcolor = colors[0]
            for nextcolor in colors[1:]:
                subgrad = linear_gradient(prevcolor, nextcolor, n_out)
                final_gradient.extend(subgrad[:-1])
                prevcolor = nextcolor
            final_gradient.append(nextcolor)
            return final_gradient

        colors = polylinear_gradient(gradient, 256)
        # put into palette
        plt = [spec for rgb in colors for spec in rgb]
        r,g,b,a = self.img.split()
        self.img = self.img.convert("L")
        self.img.putpalette(plt)
        self.img.putalpha(a)
        self.img = self.img.convert("RGBA")
        self.update_drawer_img()

##        self.percent_space()
##        x = 0
##        for c in colors:
##            c = tuple(c)
##            self.draw_box(xy=(x,20), anchor="w", fillsize=1, fillcolor=c)
##            x += 1
            
        return self










    # Layout

    def draw_grid(self, xinterval, yinterval, **kwargs):
        # ONLY BASIC SO FAR...
        xleft,ytop,xright,ybottom = self.coordspace_bbox
        xs = (xleft,xright)
        ys = (ytop,ybottom)
        xmin,xmax = min(xs),max(xs)
        ymin,ymax = min(ys),max(ys)
        
        if "fillsize" not in kwargs:
            kwargs["fillsize"] = "1px"

        xorigin, yorigin = 0,0
        
        # x
        for x in _floatrange(xorigin, xmin, -xinterval):
            self.draw_line([(x,ymax),(x,ymin)], **kwargs)
        for x in _floatrange(xorigin, xmax, xinterval):
            self.draw_line([(x,ymax),(x,ymin)], **kwargs)

        # y
        for y in _floatrange(yorigin, ymin, -yinterval):
            self.draw_line([(xmin,y),(xmax,y)], **kwargs)
        for y in _floatrange(yorigin, ymax, yinterval):
            self.draw_line([(xmin,y),(xmax,y)], **kwargs)

    def grid_paste(self, imgs, columns=None, rows=None, colfirst=True, lock_ratio=True, fit=True):
        # canvas size
        width,height = self.width,self.height
        # in case imgs is a generator
        imggen,imgcounter = itertools.tee((img for img in imgs))
        img_len = sum((1 for _ in imgcounter))

        # auto find best grid size
        if not columns and not rows:
            # see: http://stackoverflow.com/questions/3513081/create-an-optimal-grid-based-on-n-items-total-area-and-hw-ratio
            aspect_ratio = height/float(width) # * (tilewidth/tileheight)
            #rows = math.sqrt(len(imgs) * aspect_ratio)
            columns = math.sqrt(img_len/float(aspect_ratio))
            #if not rows.is_integer():
            #    rows += 1
            if not columns.is_integer():
                columns += 1
        if columns and not rows:
            columns = round(columns)
            rows = img_len/float(columns)
            if not rows.is_integer():
                rows += 1
        elif rows and not columns:
            rows = round(rows)
            columns = img_len/float(rows)
            if not columns.is_integer():
                columns += 1
        columns,rows = map(int,(columns,rows))

        # insert
        pastewidth = int(width/columns)
        pasteheight = int(height/rows)

        if colfirst:
            y = 0
            for row in range(rows):
                x = 0
                for col in range(columns):
                    img = next(imggen, None)
                    # get canvas if needed
                    if isinstance(img, Canvas): canvas = img
                    elif isinstance(img, PIL.Image.Image): canvas = from_image(img)
                    elif isinstance(img, str): canvas = load(img)
                    if canvas:
                        # resize subimg
                        canvas.resize(pastewidth, pasteheight, lock_ratio=lock_ratio, fit=fit)
                        # paste
                        self.paste(canvas, (x,y))
                    x += pastewidth
                    
                y += pasteheight

        else:
            x = 0
            for col in range(columns):
                y = 0
                for row in range(rows):
                    img = next(imggen, None)
                    # get canvas if needed
                    if isinstance(img, Canvas): canvas = img
                    elif isinstance(img, PIL.Image.Image): canvas = from_image(img)
                    elif isinstance(img, str): canvas = load(img)
                    if canvas:
                        # resize subimg
                        canvas.resize(pastewidth, pasteheight, lock_ratio=lock_ratio, fit=fit)
                        # paste
                        self.paste(canvas, (x,y))
                    y += pasteheight
                    
                x += pastewidth

        return self

##    def warp(self, coordconvert, method="near"):
##        # not sure if python has any functions for this
##        # so probably resort to my pure python scripts
##        # with a choice between nearest neighbour, bilinear, and idw algorithms
##        self.drawer.flush()
##
##        # create old vs new warped coords
##        # NOTE: assumes and requires coordsys to be rectilinear,
##        # ie same xs at all ys and same ys at all xs, ie no rotation or skew
##        # ie only converts top row of xs and first column on ys
##        # maybe add a check?
##        # ...
##        oldxs = [self.pixel2coord(x,0)[0] for x in range(self.width)]
##        oldys = [self.pixel2coord(0,y)[1] for y in range(self.height)]
####        newxs = [coordconvert(x,0)[0] for x in oldxs]
####        newys = [coordconvert(0,y)[1] for y in oldys]
##        newxs = []
##        newys = []
##        for y in oldys:
##            for x in oldxs:
##                newx,newy = coordconvert(x,y)
##                newys.append(newy)
##                newxs.append(newx)
##
##        # interpolate each band
##        bands = []
##        for band in self.img.split():
##            # get grid
##            grid = []
##            flat = list(band.getdata())
##            for i in range(0, len(flat), self.width):
##                grid.append( flat[i:i+self.width] )
##            # interp
##            if method == "near":
##                grid = gridinterp.gridinterp_near(grid, oldxs, oldys, newxs, newys)
##            elif method == "bilinear":
##                grid = gridinterp.gridinterp_bilin(grid, oldxs, oldys, newxs, newys)
##            # flatten and put into new img
##            flat = [val for row in grid for val in row]
##            band.putdata(flat)
##            bands.append(band)
##
##        # merge bands back together
##        self.img = PIL.Image.merge(self.img.mode, bands)
##        self.update_drawer_img()

    def draw_axis(self, axis, minval, maxval, intercept,
                  tickinterval=None, ticknum=5,
                  tickfunc=None, tickoptions={"fillsize":"0.4%min"},
                  ticklabelformat=None, ticklabeloptions={},
                  noticks=False, noticklabels=False,
                  **kwargs):
        # ONLY BASIC SO FAR...
        xleft,ytop,xright,ybottom = self.coordspace_bbox
        xs = (xleft,xright)
        ys = (ytop,ybottom)
        xmin,xmax = min(xs),max(xs)
        ymin,ymax = min(ys),max(ys)
        
        if "fillsize" not in kwargs:
            kwargs["fillsize"] = "1px"
        if not tickfunc:
            tickfunc = self.draw_box
        if not ticklabelformat:
            if axis == "x":
                valrange = xmax - xmin
            elif axis == "y":
                valrange = ymax - ymin
            if valrange < 1:
                ticklabelformat = ".6f"
            elif valrange < 10:
                ticklabelformat = ".1f"
            else:
                ticklabelformat = ".0f"
        if isinstance(ticklabelformat, str):
            _frmt = ticklabelformat
            ticklabelformat = lambda s: format(s, _frmt)
        if not tickinterval:
            if ticknum:
                if axis == "x": valuerange = xmax-xmin
                elif axis == "y": valuerange = ymax-ymin
                tickinterval = valuerange / float(ticknum)
            else:
                raise Exception("either tickinterval or ticknum must be specified")
            
        if axis == "x":
            _ticklabeloptions = {"anchor":"n"}
            _ticklabeloptions.update(ticklabeloptions)
            self.draw_line([(minval,intercept),(maxval,intercept)], **kwargs)
            for x in _floatrange(minval, maxval+tickinterval, tickinterval):
                if x > maxval:
                    x = maxval
                if not noticks:
                    tickfunc((x,intercept), **tickoptions)
                if not noticklabels:
                    lbl = ticklabelformat(x)
                    self.draw_text(lbl, (x,intercept), **_ticklabeloptions)
        elif axis == "y":
            _ticklabeloptions = {"anchor":"e"}
            _ticklabeloptions.update(ticklabeloptions)
            self.draw_line([(intercept,minval),(intercept,maxval)], **kwargs)
            for y in _floatrange(minval, maxval+tickinterval, tickinterval):
                if y > maxval:
                    y = maxval
                if not noticks:
                    tickfunc((intercept,y), **tickoptions)
                if not noticklabels:
                    lbl = ticklabelformat(y)
                    self.draw_text(lbl, (intercept,y), **_ticklabeloptions)

##    def insert_graph(self, image, bbox, xaxis, yaxis):
##        # maybe by creating and drawing on images as subplots,
##        # and then passing them in as figures that draw their
##        # own coordinate axes if specified and then paste themself.
##        # ... 
##        pass

    ###############################
    

    @property
    def coordspace_width(self):
        xleft,ytop,xright,ybottom = self.coordspace_bbox
        x2x = (xleft,xright)
        xwidth = max(x2x)-min(x2x)
        return xwidth

    @property
    def coordspace_height(self):
        xleft,ytop,xright,ybottom = self.coordspace_bbox
        y2y = (ybottom,ytop)
        yheight = max(y2y)-min(y2y)
        return yheight

    @property
    def coordspace_units(self):
        # calculate pixels per unit etc
        pixscm = 28.346457
        widthcm = self.width / float(pixscm)
        units = self.coordspace_width / float(widthcm)
        return units

    def zoom_units(self, units, center=None):
        """
        Zoom in or out based on how many units per cm to have at the new zoom level.

        Parameters:
        
        - *units*: how many coordinate units per screen cm at the new zoom level.
        - *center* (optional): xy coordinate tuple to center/offset the zoom. Defauls to middle of the bbox. 
        """
        self.drawer.flush()
        
        # calculate pixels per unit etc
        unitscm = units
        cmsunit = 1 / float(unitscm)
        pixscm = 28.346457
        pixsunit = pixscm * cmsunit
        unitswidth = self.width / float(pixsunit) # use as the width of the bbox
        unitsheight = self.height / float(pixsunit) # use as the height of the bbox
        # zoom it
        newbbox = bboxhelper.resize_dimensions(self.coordspace_bbox,
                                         newwidth=unitswidth,
                                         newheight=unitsheight)
        # center it
        if center:
            newbbox = bboxhelper.center(newbbox, center)
        self.zoom_bbox(*newbbox, lock_ratio=True, fit=False)
        # NOTE: Not sure if this fit=False will always keep the correct side width or height
        # ...

        self.update_drawer_img()

    def zoom_factor(self, factor, center=None):
        """
        Zooms in or out n times of previous bbox. Useful when the zoom is called programmatically and it is
        not certain which way the zoom will go. 

        Parameters:

        - *factor*: Positive values > 1 for in-zoom, negative < -1 for out-zoom.
        - *center* (optional): xy coordinate tuple to center/offset the zoom. Defauls to middle of the bbox. 
        """
        self.drawer.flush()
        
        if -1 < factor < 1:
            raise Exception("Zoom error: Zoom factor must be higher than +1 or lower than -1.")
        # positive zoom means bbox must be shrunk
        if factor > 1: factor = 1 / float(factor)
        # remove minus sign for negative zoom
        elif factor <= -1: factor *= -1
        # zoom it
        newbbox = bboxhelper.resize_ratio(self.coordspace_bbox,
                           xratio=factor,
                           yratio=factor)
        # center it
        if center:
            newbbox = bboxhelper.center(newbbox, center)
        self.zoom_bbox(*newbbox, lock_ratio=False)
        
        self.update_drawer_img()

    def zoom_in(self, factor, center=None):
        """
        Zooms inwards n times of previous bbox. Same as zoom_factor() with a positive value. 

        Parameters:

        - *factor*: Zoom in factor, 1 or higher. 
        - *center* (optional): xy coordinate tuple to center/offset the zoom. Defauls to middle of the bbox. 
        """
        self.zoom_factor(factor, center)

    def zoom_out(self, factor, center=None):
        """
        Zooms outwards n times of previous bbox. Same as zoom_factor() with a negative value. 

        Parameters:

        - *factor*: Zoom out factor, 1 or higher. 
        - *center* (optional): xy coordinate tuple to center/offset the zoom. Defauls to middle of the bbox. 
        """
        self.zoom_factor(-1 * factor, center)        

    def zoom_bbox(self, xmin, ymin, xmax, ymax, lock_ratio=True, fit=True):
        """
        Essentially the same as using coord_space(), but takes a bbox
        in min/max format instead, converting to left/right/etc behind
        the scenes so that axis directions are preserved.
        Moreover, the existing image is zoomed as well. 

        Parameters:

        - *xmin*: The lower bound of the x-axis after the zoom.
        - *ymin*: The lower bound of the y-axis after the zoom.
        - *xmax*: The higher bound of the x-axis after the zoom.
        - *ymax*: The higher bound of the y-axis after the zoom.
        - *lock_ratio*: Preserve the aspect ratio of the original image/coordsys. 
        """
        self.drawer.flush()
        
        xleft, ybottom, xright, ytop = xmin, ymin, xmax, ymax
        oldxleft, oldytop, oldxright, oldybottom = self.coordspace_bbox
        
        # ensure old and zoom axes go in same directions
        if not (xleft < xright) == (oldxleft < oldxright):
            xleft,xright = xright,xleft
        if not (ytop < ybottom) == (oldytop < oldybottom):
            ytop,ybottom = ybottom,ytop
            
        # constrain the coordinate view ratio to the screen ratio, shrinking the coordinate space to ensure that it is fully contained inside the image
        # NOTE: figure out why we use coordspace dimensions here
        # ...and image pixel dimensions in custom_coordspace().
        if lock_ratio:
            bbox = [xleft,ytop,xright,ybottom]
            xleft,ytop,xright,ybottom = bboxhelper.conform_aspect(bbox,
                                                                  self.coordspace_width,
                                                                  self.coordspace_height,
                                                                  fit=fit)
            
        # zoom the image
        pxleft,pytop = self.coord2pixel(xleft,ytop)
        pxright,pybottom = self.coord2pixel(xright,ybottom)
        self.img = self.img.transform((self.width,self.height),
                                      PIL.Image.EXTENT,
                                      (pxleft,pytop,pxright,pybottom),
                                      PIL.Image.BILINEAR)
        
        # zoom the coord space
        # NOTE: disabling aspect ratio because already calculated the bbox correctly
        self.custom_space(xleft, ytop, xright, ybottom, lock_ratio=False) 
        
        self.update_drawer_img()

    def pixel_space(self):
        """
        Convenience method for setting the coordinate space to pixels,
        so the user can easily draw directly to image pixel positions.
        """
        self.drawer.settransform()
        self.coordspace_bbox = [0, 0, self.width, self.height]
        self.coordspace_transform = (1, 0, 0,
                                     0, 1, 0)

    def fraction_space(self):
        """
        Convenience method for setting the coordinate space to fractions,
        so the user can easily draw using relative fractions (0-1) of image.
        """
        self.custom_space(*[0,0,1,1])

    def percent_space(self):
        """
        Convenience method for setting the coordinate space to percentages,
        so the user can easily draw coordinates as percentage (0-100) of image.
        """
        self.custom_space(*[0,0,100,100])

    def geographic_space(self):
        """
        Convenience method for setting the coordinate space to geographic,
        so the user can easily draw coordinates as lat/long of world,
        from -180 to 180 x coordinates, and -90 to 90 y coordinates.
        Also locks the aspect ratio to fit the entire coordinate space
        inside the image without geographic distortion.
        """
        self.custom_space(*[-180,90,180,-90], lock_ratio=True)

    def custom_space(self, xleft, ytop, xright, ybottom,
                         lock_ratio=False):
        """
        Defines which areas of the screen represent which areas in the
        given drawing coordinates. Default is to draw directly with
        screen pixel coordinates. 

        Parameters:
        
        - *xleft*: The x-coordinate to be mapped to the left side of the screen.
        - *ytop*: The y-coordinate to be mapped to the top side of the screen.
        - *xright*: The x-coordinate to be mapped to the right side of the screen.
        - *ybottom*: The y-coordinate to be mapped to the bottom side of the screen.
        - *lock_ratio* (optional): Set to True if wanting to constrain the coordinate space to have the same width/height ratio as the image, in order to avoid distortion. Default is False. 

        """

        # basic info
        bbox = xleft,ytop,xright,ybottom
        x2x = (xleft,xright)
        y2y = (ybottom,ytop)
        xwidth = max(x2x)-min(x2x)
        yheight = max(y2y)-min(y2y)
        oldxwidth,oldyheight = xwidth,yheight

        # constrain the coordinate view ratio to the screen ratio, shrinking the coordinate space to ensure that it is fully contained inside the image
        centered = affine.Affine.identity()
        if lock_ratio:
            # make coords same proportions as canvas image
            screenxratio = self.width / float(self.height)
            yheight = yheight
            xwidth = yheight * screenxratio
            # ensure that altered coords do not shrink the original coords
            diffratio = 1.0
            if xwidth < oldxwidth: diffratio = oldxwidth / float(xwidth)
            elif yheight < oldyheight: diffratio = oldyheight / float(yheight)
            xwidth *= diffratio
            yheight *= diffratio
            # move the center of focus to middle of coordinate space if view ratio has been constrained
            xoff = (xwidth - oldxwidth) / 2.0
            yoff = (yheight - oldyheight) / 2.0
            centered *= affine.Affine.translate(xoff, yoff)
            
        # Note: The sequence of matrix multiplication is important and sensitive.
        # ...see eg http://negativeprobability.blogspot.no/2011/11/affine-transformations-and-their.html

        # scale ie resize world to screen coords
        scalex = self.width / float(xwidth)
        scaley = self.height / float(yheight)
        scaled = affine.Affine.scale(scalex,scaley)
        if xleft < xright: xoff = -min(x2x)
        else: xoff = min(x2x)
        if ytop < ybottom: yoff = -min(y2y)
        else: yoff = min(y2y)
        scaled *= affine.Affine.translate(xoff,yoff) # to force anchor upperleft world coords to upper left screen coords

        # flip world coords if axes run in different direction than screen axes
        xflip = xright < xleft
        yflip = ybottom < ytop
        if xflip: xflipoff = xwidth
        else: xflipoff = 0
        if yflip: yflipoff = yheight
        else: yflipoff = 0
        flipped = affine.Affine.translate(xflipoff,yflipoff) # to make the flipping stay in same place
        flipped *= affine.Affine.flip(xflip,yflip)

        # calculate the final coefficients and set as the drawtransform
        transcoeffs = (scaled * flipped * centered).coefficients
        self.drawer.settransform(transcoeffs)

        # finally remember the new coordinate extents and affine matrix
        self.coordspace_bbox = bboxhelper.resize_ratio(bbox,
                                           xratio=xwidth / float(oldxwidth),
                                           yratio=yheight / float(oldyheight) )
        self.coordspace_transform = transcoeffs

    def set_default_unit(unit):
        """
        Sets the default unit for drawing sizes etc.

        Parameters:

        - *unit*:
            Can be real world units (cm, mm, in, pt), percent of width or height
            (%w or %h), or percent of minimum or maximum side (%min or %max). 
            Default is percent of width. 
        """
        self.default_unit = unit













    # Drawing

    def draw_circle(self, xy=None, bbox=None, flatratio=1, **options):
        """
        Draw a circle, normal or flattened. Either specified with xy and flatratio,
        or with a bbox. 

        Parameters:

        - *xy* (optional): Xy center coordinate to place the circle. 
        - *bbox* (optional): Bounding box of the flattened circle instead of xy coordinate. 
        - *flatratio* (optional): The ratio of the circle height to width. A normal circle is given with 1.0 (default) and a half-flat circle with 0.5. 
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        #TEMPORARY DISABLING TRANSFORM TO AVOID DEFORMED CIRCLE
        options = self._check_options(options)
        args = []
        
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
            
        if xy:
            x,y = xy
            x,y = self.coord2pixel(x,y)
            fillsize = options["fillsize"]
            width = options["fillwidth"]
            height = options["fillheight"]
##            width, height = width / self.width * self.coordspace_width, \
##                            height / self.height * self.coordspace_height
            if flatratio: height *= flatratio
            halfwidth, halfheight = width / 2.0, height / 2.0
            bbox = [x-halfwidth, y-halfheight, x+halfwidth, y+halfheight]
        
        elif bbox: pass
        
        else: raise Exception("Either xy or bbox has to be specified")
        
        self.drawer.settransform()
        self.drawer.ellipse(bbox, *args)
        self.drawer.settransform(self.coordspace_transform)

    def draw_triangle(self, xy=None, bbox=None, flatratio=1.0, **options):
        """
        Draw a triangle, equiangled or otherwise. Either specified with xy and flatratio,
        or with a bbox. 

        Parameters:

        - *xy* (optional): Xy center coordinate to place the triangle. 
        - *bbox* (optional): Bounding box of the flattened triangle instead of xy coordinate. 
        - *flatratio* (optional): The ratio of the triangle height to width. A normal triangle is given with 1.0 (default) and a half-flat triangle with 0.5. 
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        options = self._check_options(options)
        args = []
        
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
            
        if xy:
            x,y = xy
            fillsize = options["fillsize"]
            width = options["fillwidth"]
            height = options["fillheight"]
            if flatratio: height *= flatratio
        
        elif bbox:
            xmin,ymin,xmax,ymax = bbox
            width, height = xmax - xmin, ymax - ymin
            x, y = xmin + width / 2.0, ymin + height / 2.0
        
        else: raise Exception("Either xy or bbox has to be specified")

        width, height = width / self.width * self.coordspace_width, \
                        height / self.height * self.coordspace_height
        halfwidth, halfheight = width / 2.0, height / 2.0
        coords = [x-halfwidth,y-halfheight, x+halfwidth,y-halfheight, x,y+halfheight]
        self.drawer.polygon(coords, *args)

    def draw_pie(self, xy, startangle, endangle, **options):
        """
        Draw a piece of pie.

        Parameters:

        - *xy*: Xy center coordinate to place the pie origin. 
        - *startangle*: Degree angle to start the pie.
        - *endangle*: Degree angle to end the pie.
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        #TEMPORARY DISABLING TRANSFORM TO AVOID DEFORMED PIE
        options = self._check_options(options)
        x,y = xy
        x,y = self.coord2pixel(x,y)
        fillsize = options["fillsize"]
        bbox = [x-fillsize, y-fillsize, x+fillsize, y+fillsize]
        args = []
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
        self.drawer.settransform()
        self.drawer.pieslice(bbox, startangle, endangle, *args)
        self.drawer.settransform(self.coordspace_transform)

    def draw_box(self, xy=None, bbox=None, flatratio=1.0, **options):
        """
        Draw a square, equisized or rectangular. Either specified with xy and flatratio,
        or with a bbox. 

        Parameters:

        - *xy* (optional): Xy center coordinate to place the square. 
        - *bbox* (optional): Bounding box of the flattened rectangle instead of xy coordinate. 
        - *flatratio* (optional): The ratio of the rectangle height to width. A normal square is given with 1.0 (default) and a half-flat rectangle with 0.5. 
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        options = self._check_options(options)
        args = []
        
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
            
        if xy:
            x,y = xy
            width = options["fillwidth"]
            height = options["fillheight"]
            if flatratio: height *= flatratio
            width, height = width / self.width * self.coordspace_width, \
                            height / self.height * self.coordspace_height
            halfwidth, halfheight = width / 2.0, height / 2.0
            bbox = [x-halfwidth, y-halfheight, x+halfwidth, y+halfheight]
        
        elif bbox: pass
        
        else: raise Exception("Either xy or bbox has to be specified")
        
        self.drawer.rectangle(bbox, *args)

    def draw_line(self, coords, smooth=False, **options):
        """
        Connect a series of coordinate points with one or more lines.
        Outline does not work with this method.

        Parameters:

        - *coords*: A list of coordinates for the linesequence.
        - *smooth* (optional): If True, smooths the lines by drawing quadratic bezier curves between midpoints of each line segment. Default is False.
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        # NOTE: Outline does not work because uses paths instead of normal line method.
        # TODO: Add volume param, containing a list of linewidths same length as line
        # or as a function that calculates the width at each node
        # Result is a flow line with varying thickness at each node
        # Have to calculate left/right xy at each node, and use symbol curveto()
        # Easy and really cool...DO IT!
        options = self._check_options(options)
        
        if not hasattr(coords[0], "__iter__"):
            coords = _grouper(coords, 2)
        else: coords = (point for point in coords)
        
        # get drawing tools from options
        args = []
        if options["fillcolor"]:
            pen = aggdraw.Pen(options["fillcolor"], options["fillsize"])
            args.append(pen)

        if smooth:

            # Note: Creation of the aggdraw.Symbol object here can be
            # very slow for long lines; Path is much faster but due
            # to a bug it does not correctly render curves, hence the use
            # of Symbol

            # Todo: Maybe use smooth bezier instead which passes through
            # the full start and end points and still connects them smoothly.
##            pathstring = ""
##            coords = (c for c in coords)
##            pathstring += " M%s,%s" %next(coords)
##            pathstring += " L%s,%s" %next(coords)
##            # for each line
##            for nextx,nexty in coords:
##                pathstring += " T%s,%s" %(nextx,nexty)
            
            pathstring = ""
            
            # begin
            coords = _pairwise(coords)
            (startx,starty),(endx,endy) = next(coords)
            pathstring += " M%s,%s" %(startx, starty)
            
            # draw straight line to first line midpoint
            midx,midy = (endx + startx) / 2.0, (endy + starty) / 2.0
            pathstring += " L%s,%s" %(midx, midy)
            oldmidx,oldmidy = midx,midy
            
            # for each line
            for line in coords:
                # curve from midpoint of first to midpoint of second
                (startx,starty),(endx,endy) = line
                midx,midy = (endx + startx) / 2.0, (endy + starty) / 2.0
                pathstring += " Q%s,%s,%s,%s" %(startx, starty, midx, midy)
                oldmidx,oldmidy = midx,midy
                
            # draw straight line to endpoint of last line
            pathstring += " L%s,%s" %(endx, endy)

            # make into symbol object
            symbol = aggdraw.Symbol(pathstring)

            # draw the constructed symbol
            self.drawer.symbol((0,0), symbol, *args)

        else:

            path = aggdraw.Path()
            
            # begin
            startx,starty = next(coords)
            path.moveto(startx, starty)
            
            # connect to each successive point
            for nextx,nexty in coords:
                path.lineto(nextx, nexty)

            # draw the constructed path
            self.drawer.path((0,0), path, *args)

    def draw_polygon(self, coords, holes=[], **options):
        """
        Draw polygon and holes with color fill.
        Holes must be counterclockwise.

        Parameters:
        
        - *coords*: A list of coordinates for the polygon exterior.
        - *holes* (optional): A list of one or more polygon hole coordinates, one for each hole. Defaults to no holes.
        - *options* (optional): Keyword args dictionary of draw styling options. 
        """
        options = self._check_options(options)
        
        path = aggdraw.Path()
        
        if not hasattr(coords[0], "__iter__"):
            coords = _grouper(coords, 2)
        else: coords = (point for point in coords)

        def traverse_ring(coords):
            # begin
            startx,starty = next(coords)
            path.moveto(startx, starty)
            
            # connect to each successive point
            for nextx,nexty in coords:
                path.lineto(nextx, nexty)
            path.close()

        # first exterior
        traverse_ring(coords)

        # then holes
        for hole in holes:
            # !!! need to test for ring direction !!!
            if not hasattr(hole[0], "__iter__"):
                hole = _grouper(hole, 2)
            else: hole = (point for point in hole)
            traverse_ring(hole)

        # options        
        args = []
        if options["fillcolor"]:
            fillbrush = aggdraw.Brush(options["fillcolor"])
            args.append(fillbrush)
        if options["outlinecolor"]:
            outlinepen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(outlinepen)
            
        self.drawer.path((0,0), path, *args)

    def draw_text(self, text, xy=None, bbox=None, rotate=None, **options):
        """
        Draws basic text.

        Parameters:

        - *text*: The text string to write.
        - *xy* (optional): The xy location to write the text.
        - *bbox* (optional): The bounding box into which the text should fit instead of xy location.
            If specified, wraps text where necessary and calculates optimal font size to
            fit inside the box, ignoring any user specified font size. 
        - *options* (optional): Keyword args dictionary of text styling options.
            This includes the usual fillcolor/size and outlinecolor/width and some
            additional ones.
            Font is used with the xy argument and can be the name, filename, or filepath of a font. 
            Anchor is used with the xy argument and can be any compass direction n,ne,e,se,s,sw,w,nw, or center.
            Justify is used with the bbox argument and can be any left,right,center direction.
            Padx is used with the bbox argument or when using xy with fillcolor or outlinecolor and specifies the percent x padding between the text and the box.
            Pady is used with the bbox argument or when using xy with fillcolor or outlinecolor and specifies the percent y padding between the text and the box.
        """
        options = self._check_text_options(options)

        if xy:
            x,y = xy

            # process text options
            fontlocation = fonthelper.get_fontpath(options["font"])

            # PIL doesnt support transforms, so must get the pixel coords of the coordinate
            x,y = xorig,yorig = self.coord2pixel(x,y)
            
            # get font dimensions
            font = PIL.ImageFont.truetype(fontlocation, size=options["textsize"]) #, opacity=options["textopacity"])
            fontwidth, fontheight = font.getsize(text)
            
            # anchor
            textanchor = options["anchor"].lower()
            if textanchor == "center":
                x = int(x - fontwidth/2.0)
                y = int(y - fontheight/2.0)
            else:
                x = int(x - fontwidth/2.0)
                y = int(y - fontheight/2.0)
                if "n" in textanchor:
                    y = int(y + fontheight/2.0)
                elif "s" in textanchor:
                    y = int(y - fontheight/2.0)
                if "e" in textanchor:
                    x = int(x - fontwidth/2.0)
                elif "w" in textanchor:
                    x = int(x + fontwidth/2.0)

            # load or set default background box options
            bboxoptions = dict()
            bboxoptions["fillcolor"] = options.get("fillcolor", None)
            bboxoptions["outlinecolor"] = options.get("outlinecolor", None)
            bboxoptions["outlinewidth"] = options.get("outlinewidth", "2px")
            bboxoptions["fillopacity"] = options.get("fillopacity", 0)
            bboxoptions["outlineopacity"] = options.get("outlineopacity", 0)
            
            #### draw background box and or outline
            if bboxoptions["fillcolor"] or bboxoptions["outlinecolor"]:
                x1,y1 = self.pixel2coord(x, y)
                x2,y2 = self.pixel2coord(x+fontwidth, y+fontheight)
                xmin,ymin = min((x1,x2)),min((y1,y2))
                xmax,ymax = max((x1,x2)),max((y1,y2))
                bbox = [xmin,ymin,xmax,ymax]
                boxwidth, boxheight = xmax-xmin, ymax-ymin

                #### use pad args to determine new bigger bbox
                # padx
                if "padx" in options:
                    padx = options["padx"]
                else:
                    padx = "10%w"
                padx = units.parse_dist(padx,
                                         ppi=self.ppi,
                                         default_unit=self.default_unit,
                                         canvassize=[boxwidth, boxheight])
                halfpadx = padx / 2.0
                xmin = xmin - halfpadx
                xmax = xmax + halfpadx
                # pady
                if "pady" in options:
                    pady = options["pady"]
                else:
                    pady = "10%h"
                pady = units.parse_dist(pady,
                                         ppi=self.ppi,
                                         default_unit=self.default_unit,
                                         canvassize=[boxwidth, boxheight])
                halfpady = pady / 2.0
                ymin = ymin - halfpady
                ymax = ymax + halfpady
                # update bbox
                bbox = [xmin,ymin,xmax,ymax]

                self.draw_box(bbox=bbox, **bboxoptions)

            # then draw text
            if rotate:
                # write and rotate separate img
                txt_img = PIL.Image.new('RGBA', font.getsize(text))
                PIL_drawer = PIL.ImageDraw.Draw(txt_img)
                PIL_drawer.text((0,0), text, fill=options["textcolor"], font=font)
                txt_img = txt_img.rotate(rotate, PIL.Image.BILINEAR, expand=1)
                # update to post-rotate anchor
                fontwidth,fontheight = txt_img.size
                x,y = xorig,yorig
                if textanchor == "center":
                    x = int(x - fontwidth/2.0)
                    y = int(y - fontheight/2.0)
                else:
                    x = int(x - fontwidth/2.0)
                    y = int(y - fontheight/2.0)
                    if "n" in textanchor:
                        y = int(y + fontheight/2.0)
                    elif "s" in textanchor:
                        y = int(y - fontheight/2.0)
                    if "e" in textanchor:
                        x = int(x - fontwidth/2.0)
                    elif "w" in textanchor:
                        x = int(x + fontwidth/2.0)
                # paste into main
                self.drawer.flush()
                self.img.paste(txt_img, (x,y), txt_img)
            else:
                PIL_drawer = PIL.ImageDraw.Draw(self.img)
                self.drawer.flush()
                PIL_drawer.text((x,y), text, fill=options["textcolor"], font=font)

        elif bbox:
            # dynamically decides optimal font size and wrap length
            # TODO: currently only respects pady, not padx

            # load or set default background box options
            bboxoptions = dict()
            bboxoptions["fillcolor"] = options.get("fillcolor", None)
            bboxoptions["outlinecolor"] = options.get("outlinecolor", None)
            bboxoptions["outlinewidth"] = options.get("outlinewidth", "2px")
            bboxoptions["fillopacity"] = options.get("fillopacity", 0)
            bboxoptions["outlineopacity"] = options.get("outlineopacity", 0)
            
            #### draw background box and or outline
            if bboxoptions["fillcolor"] or bboxoptions["outlinecolor"]:
                self.draw_box(bbox=bbox, **bboxoptions)

            #### get bbox with and height in pixels
            xmin,ymin,xmax,ymax = bbox
            x1,y1 = self.coord2pixel(xmin,ymin)
            x2,y2 = self.coord2pixel(xmax,ymax)
            xmin,ymin = min((x1,x2)),min((y1,y2))
            xmax,ymax = max((x1,x2)),max((y1,y2))
            boxwidth = xmax - xmin
            boxheight = ymax - ymin

            #### use pad args to determine new smaller bbox
            # padx
            if "padx" in options:
                padx = options["padx"]
            else:
                padx = "10%w"
            padx = units.parse_dist(padx,
                                     ppi=self.ppi,
                                     default_unit=self.default_unit,
                                     canvassize=[boxwidth, boxheight])
            halfpadx = padx / 2.0
            xmin = xmin + halfpadx
            xmax = xmax - halfpadx
            #pady
            if "pady" in options:
                pady = options["pady"]
            else:
                pady = "10%h"
            pady = units.parse_dist(pady,
                                     ppi=self.ppi,
                                     default_unit=self.default_unit,
                                     canvassize=[boxwidth, boxheight])
            halfpady = pady / 2.0
            ymin = ymin + halfpady
            ymax = ymax - halfpady
            #update bbox
            boxwidth = xmax - xmin
            boxheight = ymax - ymin
            bbox = [xmin,ymin,xmax,ymax]
            
            #### process text options
            fontlocation = fonthelper.get_fontpath(options["font"])
            PIL_drawer = PIL.ImageDraw.Draw(self.img)

            #### incrementally cut size in half or double it until within 20 percent of desired height
            infiloop = False
            prevsize = None
            cursize = options["textsize"]
            nextsize = None
            while True:                
                # calculate size metrics for current
                font = PIL.ImageFont.truetype(fontlocation, size=cursize) #, opacity=options["textopacity"])
                fontwidth, fontheight = font.getsize(text)
                widthratio = fontwidth / float(boxwidth)
                wraplength = int( len(text) / widthratio )
                if wraplength < 1:
                    # minimum wrap length is wrapping a text at every 1 char
                    # ...any lower than that means font size is too big to be
                    # ...wrapped, so halve the size and continue.
                    ### print("size too big to be tested, halve it!")
                    nextsize = int(round(cursize/2.0))
                    prevsize = cursize
                    cursize = nextsize
                    continue
                textlines = textwrap.wrap(text, width=wraplength)
                wrapped_fontheight = fontheight * len(textlines) # + pady * len(textlines)
                wrapped_fontheight_ratio = wrapped_fontheight / float(boxheight)

                # exit if size is within the box and almost fills it
                if 0.8 <= wrapped_fontheight_ratio <= 1:
                    break

                # break out of infinite loop between two almost same sizes
                if infiloop:
                    ### print("infinite loop, break!")
                    break

                # check if too big or small
                toobig = False
                toosmall = False
                if wrapped_fontheight_ratio < 1:
                    toosmall = True
                else:
                    toobig = True

                # mark as infinite loop once increments get smaller than 1
                if prevsize and cursize-prevsize in (-1,0,1):
                    infiloop = True
                    # make sure to choose the smaller of the two repeating sizes, so fits inside box
                    if toobig:
                        nextsize = cursize-1

                # or if prev change went too far, try in between prev and cur size
                elif prevsize and ((toosmall and prevsize > cursize) or (toobig and prevsize < cursize)):
                    ### print("too far, flip!")
                    nextsize = int(round((prevsize + cursize) / 2.0))

                # otherwise double or halve size based on fit
                else:
                    if toobig:
                        nextsize = int(round(cursize / 2.0))
                        ### print("too big!")
                    elif toosmall:
                        nextsize = cursize * 2
                        ### print("too small!")

                # update vars for next iteration
                ### print(prevsize, cursize, nextsize)
                prevsize = cursize
                cursize = nextsize

            # PIL doesnt support transforms, so must get the pixel coords of the coordinate
            # here only for y, because x is handled for each line depending on justify option below
            y = ymin # already converted earlier

            # wrap text into lines, and write each line
            self.drawer.flush()
            horizjustify = options["justify"].lower()
            for textline in textlines:
                # horizontally justify the text relative to the bbox edges
                fontwidth, fontheight = font.getsize(textline)
                if horizjustify == "center":
                    x = int(xmin + boxwidth/2.0 - fontwidth/2.0)
                elif horizjustify == "right":
                    x = xmax - fontwidth
                elif horizjustify == "left":
                    x = xmin
                # draw and increment downwards
                PIL_drawer.text((x,y), textline, fill=options["textcolor"], font=font)
                y += fontheight

        # update changes to the aggdrawer, and remember to reapply transform
        self.drawer = aggdraw.Draw(self.img)
        self.drawer.settransform(self.coordspace_transform)

    def draw_geojson(self, geojobj, **options):
        """
        Draws a shape based on the GeoJSON format. 

        Parameters: 

        - *geojobj*: Takes a GeoJSON dictionary or object that has the \_\_geo_interface__ attribute. Must be a geometry type, or a feature type with a geometry attribute. 
        - *options*: Keyword args dictionary of draw styling options.
        """
        if isinstance(geojobj, dict): geojson = geojobj
        else: geojson = geojobj.__geo_interface__

        if geojson["type"] == "Feature":
            geojson = geojson["geometry"]
            
        geotype = geojson["type"]
        coords = geojson["coordinates"]
        if geotype == "Point":
            self.draw_circle(xy=coords, **options)
        elif geotype == "MultiPoint":
            for point in coords:
                self.draw_circle(xy=point, **options)
        elif geotype == "LineString":
            self.draw_line(coords=coords, **options)
        elif geotype == "MultiLineString":
            for line in coords:
                self.draw_line(coords=line, **options)
        elif geotype == "Polygon":
            exterior = coords[0]
            interiors = []
            if len(coords) > 1:
                interiors.extend(coords[1:])
            self.draw_polygon(exterior, holes=interiors, **options)
        elif geotype == "MultiPolygon":
            for poly in coords:
                exterior = poly[0]
                interiors = []
                if len(poly) > 1:
                    interiors.extend(poly[1:])
                self.draw_polygon(exterior, holes=interiors, **options)

##    def draw_svg(self, svg):
##        pass










    # Interactive

    @property
    def coordspace_invtransform(self):
        # the inverse coefficients to go from pixel space to coordinates
        # taken from Sean Gillies' "affine.py"
        a,b,c,d,e,f = self.coordspace_transform
        det = a*e - b*d
        if det != 0:
            idet = 1 / float(det)
            ra = e * idet
            rb = -b * idet
            rd = -d * idet
            re = a * idet
            a,b,c,d,e,f = (ra, rb, -c*ra - f*rb,
                           rd, re, -c*rd - f*re)
            return a,b,c,d,e,f
        else:
            raise Exception("Cannot invert degenerate matrix")

    def pixel2coord(self, x, y):
        """
        Transforms a pixel location on the image to its position in the canvas coordinate system.

        Parameters:

        - *x*: X image pixel coordinate.
        - *y*: Y image pixel coordinate. 
        """
        a,b,c,d,e,f = self.coordspace_invtransform
        newx,newy = (x*a + y*b + c, x*d + y*e + f)
        return newx,newy

    def coord2pixel(self, x, y):
        """
        Transforms a data coordinate to its canvas image pixel position.

        Parameters:

        - *x*: X data coordinate.
        - *y*: Y data coordinate.
        """
        a,b,c,d,e,f = self.coordspace_transform
        newx,newy = (x*a + y*b + c, x*d + y*e + f)
        return int(newx),int(newy)

    def measure_dist(self, fromxy, toxy):
        """
        Returns euclidean distance between two xy point tuples, assuming they are linear cartesian coordinates.

        Parameters:

        - *fromxy*: Data coordinate point to measure from.
        - *toxy*: Data coordinate point to measure to. 
        """
        fromx,fromy = fromxy
        tox,toy = toxy
        # dist = math.sqrt( (fromx-tox)**2 + (fromy-toy)**2 )
        xdiff,ydiff = (fromx-tox),(fromy-toy)
        dist = math.hypot(xdiff,ydiff) 
        return dist











    # Viewing and Saving

    def clear(self):
        """
        Clears any drawing done on the canvas, and resets it to its
        original mode, size, and background. 
        """
        self.img = PIL.Image.new(self.img.mode, self.img.size, self.background)
        self.drawer = aggdraw.Draw(self.img)
        
    def get_image(self):
        """
        Retrieves the canvas image along with any drawing updates.

        Returns:

        - A PIL image. 
        """
        self.drawer.flush()
        return self.img
    
    def get_tkimage(self):
        """
        Retrieves a Tkinter compatible image along with any drawing updates.

        Returns:

        - A Tkinter PhotoImage image.
        """
        self.drawer.flush()
        return PIL.ImageTk.PhotoImage(self.img)

    def view(self):
        """
        Creates a Tkinter application that packs the canvas image in order to view
        what the canvas image looks like. 
        """
        window = tk.Tk()
        label = tk.Label(window)
        label.pack()
        img = self.get_tkimage()
        label["image"] = label.img = img
        window.mainloop()

    def save(self, filepath):
        """
        Saves the canvas image to a file.

        Parameters:

        - *filepath*: The filepath to save the image, including the file type extension.
            Can be saved to any image type supported by PIL. 
        """
        self.drawer.flush()
        self.img.save(filepath)












    # Internal only

    def _check_options(self, customoptions):
        # types
        customoptions = customoptions.copy()
        
        # fillsize
        # NOTE: if circle is specified with an area, get radius by:
        #    math.sqrt(area_squared/math.pi)
        if customoptions.get("fillsize"):
            customoptions["fillsize"] = units.parse_dist(customoptions["fillsize"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillsize"] = units.parse_diststring("0.7%w", ppi=self.ppi, canvassize=[self.width,self.height])
        if customoptions.get("fillwidth"):
            customoptions["fillwidth"] = units.parse_dist(customoptions["fillwidth"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillwidth"] = customoptions["fillsize"] * 2
        if customoptions.get("fillheight"):
            customoptions["fillheight"] = units.parse_dist(customoptions["fillheight"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillheight"] = customoptions["fillsize"] * 2
        # outlinewidth
        if customoptions.get("outlinewidth"):
            customoptions["outlinewidth"] = units.parse_dist(customoptions["outlinewidth"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else: customoptions["outlinewidth"] = units.parse_diststring("0.07%w", ppi=self.ppi, canvassize=[self.width,self.height])
        
        # colors
        if customoptions.get("fillcolor", "not specified") == "not specified":
            customoptions["fillcolor"] = [random.randrange(0,255) for _ in xrange(3)]
        if customoptions.get("outlinecolor", "not specified") == "not specified":
            customoptions["outlinecolor"] = (0,0,0)
            
        # finish  
        return customoptions

    def _check_text_options(self, customoptions):       
        customoptions = customoptions.copy()
        
        if "textsize" in customoptions:
            textsize = customoptions["textsize"]
            if isinstance(textsize, str) and textsize.endswith("%"):
                textsize = self.default_textoptions["textsize"] * float(textsize[:-1]) / 100.0
            customoptions["textsize"] = int(round(textsize))

        finaloptions = self.default_textoptions.copy()
        finaloptions.update(customoptions)
        return finaloptions





##############################
# User functions

def from_image(img):
    """
    Loads a Canvas instance preloaded with the size and pixels of an
    existing PIL image, from memory.

    Parameters:

    - *img*: A PIL image instance.

    Returns:

    - A Canvas instance. 
    """
    canvas = Canvas(100, 100)
    canvas.img = img
    if not canvas.img.mode in ("RGB","RGBA"):
        canvas.img = canvas.img.convert("RGBA")
    canvas.drawer = aggdraw.Draw(canvas.img)
    canvas.pixel_space()
    return canvas

def load(filepath):
    """
    Loads a Canvas instance preloaded with the size and pixels of an
    existing image from a file.

    Parameters:

    - *filepath*: The filepath of the image file to load.

    Returns:

    - A Canvas instance.
    """
    canvas = Canvas(100, 100)
    canvas.img = PIL.Image.open(filepath)
    if not canvas.img.mode in ("RGB","RGBA"):
        canvas.img = canvas.img.convert("RGBA")
    canvas.drawer = aggdraw.Draw(canvas.img)
    canvas.pixel_space()
    return canvas





