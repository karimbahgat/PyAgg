"""
Defines the PyAgg Canvas class, where most of the PyAgg functinoality is defined. 
"""

##############################
# Startup and imports

# Import future stuff
from __future__ import division

# Import dependencies
import PIL, PIL.Image, PIL.ImageDraw, PIL.ImageFont
import PIL.ImageOps, PIL.ImageChops, PIL.ImageMath, PIL.ImageEnhance
import aggdraw

# Tkinter related
try:
    # try
    import Tkinter as tk
    import PIL.ImageTk
except:
    # Tkinter not available on this platform
    pass

# Import builtins
import sys, os
import struct
import itertools
import random
import traceback
import warnings
import textwrap
import math
import gc # garbage collection

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

class _Line:
    def __init__(self, x1,y1,x2,y2):
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
        self.xdiff = x2-x1
        self.ydiff = y2-y1
        try:
            self.slope = self.ydiff/float(self.xdiff)
            self.zero_y = self.slope*(0-x1)+y1
        except ZeroDivisionError:
            self.slope = None
            self.zero_y = None
    def __str__(self):
        return str(self.tolist())
    @property
    def start(self):
        return (self.x1,self.y1)
    @property
    def end(self):
        return (self.x2,self.y2)    
    def tolist(self):
        return (self.start,self.end)
    def intersect(self, otherline, infinite=False):
        """
        Input must be another line instance
        Finds real or imaginary intersect assuming lines go forever, regardless of real intersect
        Infinite is based on http://stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
        Real is based on http://stackoverflow.com/questions/18234049/determine-if-two-lines-intersect
        """
        if infinite:
            D  = -self.ydiff * otherline.xdiff - self.xdiff * -otherline.ydiff
            Dx = self._selfprod() * otherline.xdiff - self.xdiff * otherline._selfprod()
            Dy = -self.ydiff * otherline._selfprod() - self._selfprod() * -otherline.ydiff
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return False
        else:
            # MANUAL APPROACH
            # http://stackoverflow.com/questions/18234049/determine-if-two-lines-intersect
            if self.slope == None:
                if otherline.slope == None:
                    return False
                ix = self.x1
                iy = ix*otherline.slope+otherline.zero_y
            elif otherline.slope == None:
                ix = otherline.x1
                iy = ix*self.slope+self.zero_y
            else:
                try:
                    ix = (otherline.zero_y-self.zero_y) / (self.slope-otherline.slope)
                except ZeroDivisionError:
                    #slopes are exactly the same so never intersect
                    return False
                iy = ix*self.slope+self.zero_y

            #check that intsec happens within bbox of both lines
            if ix >= min(self.x1,self.x2) and ix >= min(otherline.x1,otherline.x2)\
            and ix <= max(self.x1,self.x2) and ix <= max(otherline.x1,otherline.x2)\
            and iy >= min(self.y1,self.y2) and iy >= min(otherline.y1,otherline.y2)\
            and iy <= max(self.y1,self.y2) and iy <= max(otherline.y1,otherline.y2):
                return ix,iy
            else:
                return False
    def distance2point(self, point, getpoint=False, relativedist=False):
        """
        - point is a _Point instance with x and y attributes
        - getpoint, when True will not only return the distance but also the point on the line that was closest, in a tuple (dist, _Point instance)
        - relativedist, if comparing many distances is more important than getting the actual distance then this can be set to True which will return the squared distance without the squareroot which makes it faster
        """
        x3,y3 = point.x,point.y
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
        #below is taken directly from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
        px = x2-x1
        py = y2-y1
        something = px*px + py*py
        u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)
        if u > 1:
            u = 1
        elif u < 0:
            u = 0
        x = x1 + u * px
        y = y1 + u * py
        dx = x - x3
        dy = y - y3
        #prepare results
        if relativedist: dist = dx*dx + dy*dy
        else: dist = math.sqrt(dx*dx + dy*dy)
        if getpoint: result = (dist,_Point(x,y))
        else: result = dist
        return result
    def getlength(self):
        return math.hypot(self.xdiff,self.ydiff)
    def getangle(self):
        "hmm, sometimes returns negative angles instead of converting..."
        try:
            angle = math.degrees(math.atan(self.ydiff/float(self.xdiff)))
            if self.xdiff < 0:
                angle = 180 - angle
            else:
                angle *= -1
        except ZeroDivisionError:
            if self.ydiff < 0:
                angle = 90
            elif self.ydiff > 0:
                angle = 270
            else:
                raise TypeError("error: the vector isnt moving anywhere, so has no angle")
        if angle < 0:
            angle = 360+angle
        return angle
    def walkdistance(self, distance):
        angl_rad = math.radians(self.getangle())
        xbuff = distance * math.cos(angl_rad)
        ybuff = distance * math.sin(angl_rad)
        newx = self.x2-xbuff
        newy = self.y2+ybuff
        return (newx,newy)
    def getbuffersides(self, linebuffer):
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
        midline = _Line(x1,y1,x2,y2)
        angl = midline.getangle()
        perpangl_rad = math.radians(angl-90) #perpendicular angle in radians
        xbuff = linebuffer * math.cos(perpangl_rad)
        ybuff = linebuffer * math.sin(perpangl_rad)
        #xs
        leftx1 = (x1-xbuff)
        leftx2 = (x2-xbuff)
        rightx1 = (x1+xbuff)
        rightx2 = (x2+xbuff)
        #ys
        lefty1 = (y1+ybuff)
        lefty2 = (y2+ybuff)
        righty1 = (y1-ybuff)
        righty2 = (y2-ybuff)
        #return lines
        leftline = _Line(leftx1,lefty1,leftx2,lefty2)
        rightline = _Line(rightx1,righty1,rightx2,righty2)
        return leftline,rightline
    def anglediff(self, otherline):
        """
        not complete.
        - is left turn, + is right turn
        """
        angl1 = self.getangle()
        angl2 = otherline.getangle()
        bwangl_rel = angl1-angl2 # - is left turn, + is right turn
        #make into shortest turn direction
        if bwangl_rel < -180:
            bwangl_rel = bwangl_rel+360
        elif bwangl_rel > 180:
            bwangl_rel = bwangl_rel-360
        return bwangl_rel
    def anglebetween_inner(self, otherline):
        "not complete"
        crossvecx = self.ydiff-otherline.ydiff
        crossvecy = otherline.xdiff-self.xdiff
        line = _Line(self.x2,self.y2,self.x2+crossvecx,self.y2+crossvecy)
        bwangl = line.getangle()
        return bwangl
    def anglebetween_outer(self, otherline):
        "not complete"
        bwangl = self.anglebetween_inner(otherline)
        if bwangl > 180:
            normangl = bwangl-180
        else:
            normangl = 180+bwangl
        return normangl
    
    #INTERNAL USE ONLY
    def _selfprod(self):
        """
        Used by the line intersect method
        """
        return -(self.x1*self.y2 - self.x2*self.y1)

class Gradient:
    def __init__(self, colorstops):
        self.colorstops = colorstops

    def interp(self, steps=100):
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
                for j in range(len(self.colorstops[0]))
                ]
                # Add it to our list of output colors
                RGB_list.append(curr_vector)
            return RGB_list

        def polylinear_gradient(colors, n):
            ''' returns a list of colors forming linear gradients between
              all sequential pairs of colors. "n" specifies the total
              number of desired output colors '''
            # The number of colors per individual linear gradient
            n_out = int(round(float(n) / (len(colors) - 1)))
            final_gradient = []
            # returns dictionary defined by color_dict()
            prevcolor = colors[0]
            for nextcolor in colors[1:]:
                subgrad = linear_gradient(prevcolor, nextcolor, n_out)
                final_gradient.extend(subgrad[:-1])
                prevcolor = nextcolor
            final_gradient.append(nextcolor)
            return final_gradient

        colors = polylinear_gradient(self.colorstops, steps)
        while len(colors) < steps:
            # hack to just duplicate the last color in case of indivisible step number
            colors.append(colors[-1])

        return colors




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
    def __init__(self, width=None, height=None, background=None, mode="RGBA", ppi=300, preset=None):
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
        - *preset* (optional):
            Automatically sets the width and height options based on a template.
            Valid values are: "A4"
        """
        # maybe use image size preset
        if not (width and height):
            if preset:
                if preset == "A4":
                    width,height = "210mm","297mm"
            else:
                raise Exception("Canvas must be initiated with a width and height, or using the preset option")

        # unless specified, interpret width and height as pixels
        width = units.parse_dist(width, default_unit="px", ppi=ppi)
        height = units.parse_dist(height, default_unit="px", ppi=ppi)
        width,height = int(round(width)),int(round(height))

        # "none" as background opens up for random noise and contamination from previous images still in memory
        # so override with default backgrounds
        if not background:
            if mode == "RGBA":
                background = (255,255,255,0)
            elif mode == "RGB":
                background = (255,255,255)

        # create image
        gc.collect()  # free up memory and avoid noise from previous images
        self.img = PIL.Image.new(mode, (width, height), background)

        # create drawer
        self.drawer = aggdraw.Draw(self.img)

        # remember info
        self.background = background
        self.ppi = ppi

        # set canvas-wide parent options...
        self.textoptions = {"font":"DejaVu Sans",
                            "textcolor":(0,0,0),
                            "textsize":"5%min", # 5% of minimum side
                            "anchor":"center", "justify":"left"}


        # customize misc default options...

        # by default, interpret all sizes in % of width
        self.default_unit = "%w"

        # maybe also have default general drawingoptions
        # ...

        # maybe also have default colorcycle
        # ...

        # by default, interpret all coordinates in pixel space
        self.pixel_space()

    def __del__(self):
        del self.img
        del self.drawer
        del self
        gc.collect()

    def copy(self):
        newcanvas = Canvas(100, 100)
        newcanvas.img = self.img.copy()
        newcanvas.background = self.background
        newcanvas.ppi = self.ppi
        newcanvas.default_unit = self.default_unit
        newcanvas.textoptions = self.textoptions
        newcanvas.coordspace_transform = self.coordspace_transform
        newcanvas.coordspace_bbox = self.coordspace_bbox
        newcanvas.update_drawer_img()
        return newcanvas

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
            # FINAL TODO: newbbox coords not correct yet...
            if fit:
                # fits entire image inside the width and height
                
##                img = self.img.copy()
##                img.thumbnail((width,height), PIL.Image.ANTIALIAS)
##                oldwidth,oldheight = img.size
##                thumb = img.crop( (0, 0, width, height) )
##                offset_x = max([ (width - oldwidth) / 2.0, 0 ])
##                offset_y = max([ (height - oldheight) / 2.0, 0 ])
##                self.img = PIL.ImageChops.offset(thumb, int(offset_x), int(offset_y))
                
                wratio = width / float(self.width)
                hratio = height / float(self.height)
                scale = min((wratio,hratio))

                newwidth = int(self.width * scale)
                newheight = int(self.height * scale)
                topaste = self.img.resize((newwidth, newheight), PIL.Image.ANTIALIAS)

                self.img = PIL.Image.new(self.img.mode, (width, height))
                midx = int(width / 2.0)
                midy = int(height / 2.0)
                self.paste(topaste, (midx,midy), anchor="center")

                newbbox = self.coordspace_bbox
                newbbox = bboxhelper.conform_aspect(newbbox, width, height, fit=True)
                
            else:
                # fills entire width and height while cropping any excess
                # Note: PIL "fit" is actually filling, just difference uses of terminology
                self.img = PIL.ImageOps.fit(self.img, (width,height), PIL.Image.ANTIALIAS, (0.5, 0.5))
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

    def rotate(self, degrees, expand=True):
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
        self.img = self.img.rotate(degrees, PIL.Image.BICUBIC, expand=expand)
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

    def paste(self, image, xy=(0,0), bbox=None, lock_ratio=True, fit=True, anchor="nw", outlinewidth=None, outlinecolor="black"):
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

            # NOTE: potential bug here if opposite axis directions
            # which happes when drawing the outline below
            # ...

        ###
        if image.mode == "RGBA":
            pasted = PIL.Image.new("RGBA", self.img.size)
            pasted.paste(image, xy) # reframes the image so has the same size as the background image
            self.img = PIL.Image.alpha_composite(self.img, pasted) # possibly slower but correctly blends the transparencies of both imgs
            #self.img.paste(image, xy, image) # paste using self as transparency mask (PROBLEM: forces transparency of pasted image, so cuts through solid colors in the background image)
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
        Similar to zoom_bbox(), except the size of the returned image will match the pixel
        dimensions of the given bounding box. Meaning that cropping to a sub-region of the
        current view extent will return a smaller image, while cropping to a larger region
        will return an enlarged image that includes the cropped area at original size. 
        Also, lock_ratio is set to False by default.

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
        ##self.drawer.flush()
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
        oldmode = self.img.mode
        if not self.img.mode == "RGB":
            self.img = self.img.convert("RGB")
        self.img = PIL.ImageOps.equalize(self.img)
        self.update_drawer_img()
        if oldmode != self.img.mode:
            self.img = self.img.convert(oldmode)
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
            red_mask = r.point(lambda px: 255 if px == color[0] else 0, "L")
            green_mask = g.point(lambda px: 255 if px == color[1] else 0, "L")
            blue_mask = b.point(lambda px: 255 if px == color[2] else 0, "L")
            all_mask = PIL.ImageMath.eval("convert(r & g & b, 'L')", r=red_mask, g=green_mask, b=blue_mask)
            #image.putalpha(all_mask)
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
            all_mask = avg_diff.point(lambda px: 255 if px <= tolerance else 0)
            #image.putalpha(all_mask)

        newimg = image #PIL.Image.new("RGB", image.size, newcolor)
        newimg.paste(newcolor, (0,0), all_mask)

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
        colors = Gradient(gradient).interp(256)

        # put into palette
        mode = self.img.mode
        rgbs = ((rgb[0],rgb[1],rgb[2]) for rgb in colors)
        plt = [spec for rgb in rgbs for spec in rgb]
        if mode == "RGBA":
            r,g,b,a = self.img.split()
        self.img = self.img.convert("L")
        self.img.putpalette(plt)
        self.img = self.img.convert("RGBA")
        # put alpha into the palette
        if mode == "RGBA" and len(colors[0]) == 4:
            alphas = [rgb[3] for rgb in colors]
            gradalpha = self.img.convert("L").point(lut=alphas)
            # gradient alpha can only lessen the original alpha
            a = PIL.ImageMath.eval('min(a1,a2)', a1=a, a2=gradalpha).convert('L')
        # apply gradient transparancy to the paletted img
        if mode == "RGBA":
            self.img.putalpha(a)
        self.update_drawer_img()

##        self.percent_space()
##        x = 0
##        for c in colors:
##            c = tuple(c)
##            self.draw_box(xy=(x,20), anchor="w", fillsize=1, fillcolor=c)
##            x += 1
            
        return self

    def draw_gradient(self, line, gradient, width, steps=100):

        #width,unit = units.split_unit(width)
        width = self.parse_relative_dist(width)
        
        halfwidth = width/2.0
        p1,p2 = line
        dirvec = p2[0]-p1[0], p2[1]-p1[1]
        magni = math.hypot(*dirvec)
        relmagni = halfwidth / float(magni)
        perpvec = dirvec[1]*relmagni, -dirvec[0]*relmagni

        colors = (col for col in Gradient(gradient).interp(steps))
        xincr = dirvec[0]/float(steps)
        yincr = dirvec[1]/float(steps)
        incrlength = math.hypot(xincr,yincr)
        incrlength = str(incrlength + 2) + "px" # NOTE: Adds 2 extra pixels to avoid tiny gaps bw lines

        cur = p1[0]+xincr/2.0, p1[1]+yincr/2.0
        for step in range(steps):
            left = cur[0]-perpvec[0], cur[1]-perpvec[1]
            right = cur[0]+perpvec[0], cur[1]+perpvec[1]
            col = tuple(next(colors))
            
            self.draw_line([left,right], fillcolor=col, fillsize=incrlength, outlinecolor=None)
            cur = cur[0]+xincr, cur[1]+yincr
            
        









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
        if "fillcolor" not in kwargs:
            kwargs["fillcolor"] = "1px"

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
                    if img:
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
                    if img:
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
                  tickpos=None,
                  tickinterval=None, ticknum=5,
                  ticktype="tick", tickoptions={},
                  ticklabelformat=None, ticklabeloptions={},
                  noticks=False, noticklabels=False,
                  **kwargs):
        """
        Draws an axis line with tickmarks and labels marking positions along
        the canvas coordinate system. 

        Parameters:

        - *axis*: Which axis of the coordinate system to draw, either 'x' or 'y' (str)
        - *minval*: At which coordinate along the selected axis the axis line should start.
        - *maxval*: At which coordinate along the selected axis the axis line should end.
        - *intercept*: If drawing a y-axis, where along the opposite x-axis that the line should be
            positioned (the x-coordinate where the two axes intercept). Opposite if drawing an x-axis.
        - *tickpos* (optional): A list of positions where tick marks should be drawn.
        - *tickinterval* (optional): The coordinate interval between tick marks.
        - *ticknum* (optional): The number of ticks to draw between the minimum and maximum values.
        - *ticktype* (optional): What type of tick to draw, either 'tick' for a small line, or any of the
            canvas primitive drawing types, eg 'circle', etc. Alternatively a function that takes an xy arg
            and kwargs to be called for every tick. 
        - *tickoptions* (optional): Dictionary of options to be passed to the ticktype drawing method.
        - *ticklabelformat* (optional): Python formatting string or function for converting coordinate values
            to tick labels. By default auto detects an appropriate formatting based on the axis value range. 
        - *ticklabeloptions* (optional): Dictionary of options to be passed to the draw_text() tick labeling method.
        - *noticks* (optional): Disables drawing any tick marks.
        - *noticklabels* (optional): Disables drawing any tick mark labels.
        - *kwargs* (optional): Any additional keyword args are passed on as options to the draw_line() method
            that renders the axis line. 
        """

        if not tickoptions: tickoptions = dict()
        if not ticklabeloptions: ticklabeloptions = dict()
        
        xleft,ytop,xright,ybottom = self.coordspace_bbox
        xs = (xleft,xright)
        ys = (ytop,ybottom)
        xmin,xmax = min(xs),max(xs)
        ymin,ymax = min(ys),max(ys)

        if ticktype == "tick":
            ticktype = "box"

        if axis == "x":
            tickoptions["fillwidth"] = tickoptions.get("fillwidth","0.5px")
            tickoptions["fillheight"] = tickoptions.get("fillheight","4px")
        else:
            w,h = tickoptions.get("fillwidth","0.5px"),tickoptions.get("fillheight","4px")
            # switch them since width intuitively means thickness of the tick
            tickoptions["fillwidth"] = h
            tickoptions["fillheight"] = w
        
        if ticktype in ("box","circle","triangle"):
            tickfunc = getattr(self, "draw_%s"%ticktype)
        elif hasattr(ticktype,"__call__"):
            tickfunc = ticktype
        else:
            raise Exception("Invalid ticktype")
            
        if "fillsize" not in kwargs:
            kwargs["fillsize"] = "0.7%min"
        if "fillcolor" not in kwargs:
            kwargs["fillcolor"] = "black"
        if "fillsize" not in tickoptions:
            tickoptions["fillsize"] = "0.7%min"
        if "fillcolor" not in tickoptions:
            tickoptions["fillcolor"] = "black"
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
            if tickpos:
                xpos = tickpos
            else:
                xpos = _floatrange(minval, maxval+tickinterval, tickinterval)
            for x in xpos:
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
            if tickpos:
                ypos = tickpos
            else:
                ypos = _floatrange(minval, maxval+tickinterval, tickinterval)
            for y in ypos:
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

    def set_default_unit(self, unit):
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

    def draw_line(self, coords, smooth=False, volume=None, start="flat", end="flat", **options):
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

        # convert coords to pixels and temp disable transform bc all buffers etc have already been converted to pixels
        coords = (self.coord2pixel(*xy) for xy in coords)
        self.drawer.settransform() 

        if volume or (options.get("outlinecolor") and options.get("outlinewidth")):
            # enables outline and varying line volume thickness

            def convertvolume(val):
                return units.parse_dist(val,
                                         ppi=self.ppi,
                                         default_unit=self.default_unit,
                                         canvassize=[self.width,self.height],
                                         coordsize=[self.coordspace_width,self.coordspace_height])

            coords = list(coords)

            if not volume:
                fillsize = options["fillsize"] / 2.0 # no need to convert unit since fillsize has already been through that
                getbuffer = lambda p,x,y: fillsize

            elif hasattr(volume, "__call__"):
                def getbuffer(prog, x, y):
                    return convertvolume(volume(prog, x, y)) / 2.0

            elif hasattr(volume, "__iter__"):
                _buffers = (buff for buff in volume)
                def getbuffer(prog, x, y):
                    return convertvolume(next(_buffers)) / 2.0

            else:
                raise Exception("The volume parameter must be a function or an iterable (of the same length as the line minus 1) that hold the fillsize for each node")

            def threewise(iterable):
                a,_ = itertools.tee(iterable)
                b,c = itertools.tee(_)
                next(b, None)
                next(c, None)
                next(c, None)
                return itertools.izip(a,b,c)

            def bufferedlinesegments():
                if len(coords) == 2:
                    (x1,y1),(x2,y2) = coords
                    lastline = _Line(x1,y1,x2,y2)
                    prog = 1
                    buffersize = getbuffer(prog, x2, y2)
                    leftline,rightline = lastline.getbuffersides(linebuffer=buffersize)
                    yield leftline.tolist(), rightline.tolist()

                else:
                    #the first line
                    (x1,y1),(x2,y2),(x3,y3) = coords[:3]
                    line1 = _Line(x1,y1,x2,y2)
                    line2 = _Line(x2,y2,x3,y3)
                    prog = 0
                    buffersize = getbuffer(prog, x1, y1)
                    leftline,rightline = line1.getbuffersides(linebuffer=buffersize)
                    leftlinestart = leftline.tolist()[0]
                    rightlinestart = rightline.tolist()[0]
                    prevleft = leftlinestart
                    prevright = rightlinestart
                    #then all mid areas
                    #sharp join style
                    for i,(start,mid,end) in enumerate(threewise(coords)):
                        i += 1
                        (x1,y1),(x2,y2),(x3,y3) = start,mid,end
                        line1 = _Line(x1,y1,x2,y2)
                        line2 = _Line(x2,y2,x3,y3)
                        prog = i / float(len(coords))
                        buffersize = getbuffer(prog, x2, y2)
                        
                        line1_left,line1_right = line1.getbuffersides(linebuffer=buffersize)
                        line2_left,line2_right = line2.getbuffersides(linebuffer=buffersize)
                        midleft = line1_left.intersect(line2_left, infinite=True)
                        midright = line1_right.intersect(line2_right, infinite=True)
                        if not midleft or not midright:
                            #PROB FLOAT ERROR,SO NO INTERSECTION FOUND
                            #CURRENTLY JUST SKIP DRAWING,BUT NEED BETTER HANDLING
                            raise Exception("Unexpected error")

                        # yield each line segment one at a time, so they are drawn in correct order if overlap
                        leftside = [prevleft,midleft]
                        rightside = [prevright,midright]
                        yield leftside, rightside

                        # remember coords
                        prevleft = midleft
                        prevright = midright
                        
                    #finally add last line coords
                    (x1,y1),(x2,y2) = coords[-2:]
                    lastline = _Line(x1,y1,x2,y2)
                    prog = 1
                    buffersize = getbuffer(prog, x2, y2)
                    leftline,rightline = lastline.getbuffersides(linebuffer=buffersize)
                    leftlineend = leftline.tolist()[1]
                    rightlineend = rightline.tolist()[1]

                    leftside = [prevleft,leftlineend]
                    rightside = [prevright,rightlineend]
                    yield leftside, rightside

            if smooth:
                # TODO: add support for simple 2point line
                
                pen,brush = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"]), aggdraw.Brush(options["fillcolor"])

                segments = bufferedlinesegments()
                def midpoint(line):
                    (startx,starty),(endx,endy) = line
                    midx,midy = (endx + startx) / 2.0, (endy + starty) / 2.0
                    return midx,midy

                # draw straight line to first line midpoint
                left,right = next(bufferedlinesegments()) # without iterating segments
                
                firstleft,firstright = left,right
                firstline = coords[:2]
                
                # first fill
                midleft = midpoint(left)
                midright = midpoint(right)
                linepolygon = [left[0], midleft, midright, right[0]]
                pathstring = " M%s,%s" %linepolygon[0]
                for p in linepolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, None, brush)

                # then outline
                # left
                pathstring = " M%s,%s" %left[0]
                pathstring += " L%s,%s" %midleft
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)
                # right
                pathstring = " M%s,%s" %right[0]
                pathstring += " L%s,%s" %midright
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)

                left1,right1 = left,right
                midleft1,midright1 = midleft,midright
                
                # for each line
                for left2,right2 in segments:
                    # curve from midpoint of first to midpoint of second
                    midleft2 = midpoint(left2)
                    midright2 = midpoint(right2)

                    # first fill
                    pathstring = " M%s,%s" %midleft1 + " Q%s,%s"%left2[0] + ",%s,%s"%midleft2
                    pathstring += " L%s,%s" %midright2 + " Q%s,%s"%right2[0] + ",%s,%s"%midright1
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, None, brush)

                    # then outline
                    # left
                    pathstring = " M%s,%s"%midleft1
                    pathstring += " Q%s,%s"%left2[0] + ",%s,%s"%midleft2
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, pen, None)
                    # right
                    pathstring = " M%s,%s"%midright1
                    pathstring += " Q%s,%s"%right2[0] + ",%s,%s"%midright2
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, pen, None)

                    left1,right1 = left2,right2
                    midleft1,midright1 = midleft2,midright2
                                        
                # draw straight line to endpoint of last line
                # first fill
                linepolygon = [midleft2, left2[1], right2[1], midright2]
                pathstring = " M%s,%s" %linepolygon[0]
                for p in linepolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, None, brush)

                # then outline
                # left
                pathstring = " M%s,%s" %midleft2
                pathstring += " L%s,%s" %left2[1]
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)
                # right
                pathstring = " M%s,%s" %midright2
                pathstring += " L%s,%s" %right2[1]
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)

                lastline = coords[-2:]
                lastleft = left2[1]
                lastright = right2[1]

            else:
                # not smooth
                pen,brush = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"]), aggdraw.Brush(options["fillcolor"])

                firstleft,firstright = next(bufferedlinesegments()) # separate iter
                firstline = coords[:2]
        
                for left,right in bufferedlinesegments():
                    # first fill
                    linepolygon = list(left) + list(reversed(right))
                    pathstring = " M%s,%s" %linepolygon[0]
                    for p in linepolygon[1:]:
                        pathstring += " L%s,%s"%p
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, None, brush)

                    # then outline
                    # left
                    pathstring = " M%s,%s"%left[0] + " L%s,%s"%left[1]
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, pen, None)
                    # right
                    pathstring = " M%s,%s"%right[0] + " L%s,%s"%right[1]
                    symbol = aggdraw.Symbol(pathstring)
                    self.drawer.symbol((0,0), symbol, pen)

                lastline = coords[-2:]
                lastleft = left
                lastright = right

            # optional startpoint
            if start:
                if start == "flat":
                    def start(line,left,right):
                        return left,right
                        
                startpolygon = start(firstline, firstleft[0], firstright[0]) # takes last two poins ie last line and left and right endpoints as input arg

                # first fill
                pathstring = " M%s,%s" %startpolygon[0]
                for p in startpolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, None, brush)

                # then outline
                # left
                pathstring = " M%s,%s"%startpolygon[0]
                for p in startpolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)
                # right
                pathstring = " M%s,%s"%startpolygon[-1]
                for p in reversed(startpolygon[:-1]):
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen)

            # optional endpoint
            if end:
                if end == "arrow":
                    def end(line,left,right):
                        helpline = _Line(line[0][0],line[0][1],line[1][0],line[1][1])
                        width = abs(math.hypot(left[0]-right[0], left[1]-right[1]))
                        tip = helpline.walkdistance(-width)
                        leftbuf,rightbuf = helpline.getbuffersides(width)
                        return left,leftbuf.end,tip,rightbuf.end,right
                elif end == "flat":
                    def end(line,left,right):
                        return left,right
                        
                endpolygon = end(lastline, lastleft[1], lastright[1]) # takes last two poins ie last line and left and right endpoints as input arg

                # first fill
                pathstring = " M%s,%s" %endpolygon[0]
                for p in endpolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, None, brush)

                # then outline
                # left
                pathstring = " M%s,%s"%endpolygon[0]
                for p in endpolygon[1:]:
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen, None)
                # right
                pathstring = " M%s,%s"%endpolygon[-1]
                for p in reversed(endpolygon[:-1]):
                    pathstring += " L%s,%s"%p
                symbol = aggdraw.Symbol(pathstring)
                self.drawer.symbol((0,0), symbol, pen)

        else:
            # no volume and no outline, simple and fast
            # TODO: add support for 2point line
        
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
                # not smooth
                # begin
                path = aggdraw.Path()
                startx,starty = next(coords)
                path.moveto(startx, starty)
                
                # connect to each successive point
                for nextx,nexty in coords:
                    path.lineto(nextx, nexty)

                # draw the constructed path
                self.drawer.path(path, *args)

        # reinstate the drawtransform
        self.drawer.settransform(self.coordspace_transform)

    def draw_polygon(self, coords, holes=[], **options):
        """
        Draw polygon and holes with color fill.
        Holes must be counterclockwise.

        Parameters:
        
        - *coords*: A list of coordinates for the polygon exterior.
        - *holes* (optional): A list of one or more polygon hole coordinates, one for each hole. Defaults to no holes.
        - *options* (optional): Keyword args dictionary of draw styling options.
                                Fillcolor can also be a function taking a width and height, returning a canvas of same size.
                                Fillmask is an optional function taking a width and height, returning a canvas of same size that defines which areas will be filled.
        """
        options = self._check_options(options)
        
        path = aggdraw.Path()
        
        if not hasattr(coords[0], "__iter__"):
            coords = list(_grouper(coords, 2))
        else: coords = list(coords)

        def traverse_ring(coords):
            # begin
            coords = (point for point in coords)
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

        # fillmask or picture
        if "fillmask" in options or hasattr(options["fillcolor"], "__call__"): 
            xs,ys = zip(*coords)
            xmin,ymin,xmax,ymax = min(xs),min(ys),max(xs),max(ys)
            w,h = xmax-xmin, ymax-ymin
            pw,ph = self.parse_relative_dist(str(w)+"x"), self.parse_relative_dist(str(h)+"y")
            pw,ph = int(pw),int(ph)

            # use insides of the polygon as mask
            mask = Canvas(width=pw, height=ph, background="black", mode="RGB")
            mask.custom_space(*[xmin,ymin,xmax,ymax])
            mask.drawer.path(path, aggdraw.Brush("white"))
            mask.drawer.flush()
            mask = mask.img.convert("L")

            # add additional mask from user
            if "fillmask" in options:
                maskfunc = options["fillmask"] 
                custommask = maskfunc(pw,ph)
                custommask.drawer.flush()
                custommask = custommask.img.convert("L")
                mask = PIL.ImageMath.eval("a & b", a=mask, b=custommask).convert("L")

            # paste color or image
            final = PIL.Image.new("RGBA", (pw,ph))
            fill = options["fillcolor"]
            
            # picture/texture fill
            if hasattr(fill, "__call__"):
                fill = fill(pw,ph).img
            final.paste(fill,
                        mask=mask)
            self.paste(final, bbox=[xmin,ymin,xmax,ymax])

            # draw outline on top
            if options["outlinecolor"]:
                outlinepen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
                self.drawer.path(path, None, outlinepen)

        else:
            # normal fast drawing
            args = []
            if options["fillcolor"]:
                fillbrush = aggdraw.Brush(options["fillcolor"])
                args.append(fillbrush)
            if options["outlinecolor"]:
                outlinepen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
                args.append(outlinepen)
            self.drawer.path(path, *args)

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
        # TODO:
        # add parsing of latex formatted math (between $$ or \begin{equation}), via pylatexenc
        # with replacing all alphanumeric characters with their math alphanumeric unicodes (https://www.fileformat.info/info/unicode/block/mathematical_alphanumeric_symbols/list.htm)
        # + https://www.charbase.com has all unicode python representations
        # and custom handling of sub/superscripts by writing extra text of half size towards top or bottom half
        # + special handling of \sum \int etc by writing it as one char then placing sub/superscripts centered fully above or below
        # + maybe special handling of fractions, by writing unicode horizline then half offsetting below or above
        # maybe just do all this as contributions to pylatexenc...
        # see maybe also:
        # https://github.com/JelteF/PyLaTeX
        # https://github.com/plastex/plastex
        # http://milde.users.sourceforge.net/LUCR/Math/
        
        if not text:
            return False

        if not isinstance(text, (unicode,str)):
            text = str(text)
        
        options = self._check_text_options(options)

        def draw_textlines(img, textlines, pos, size, **options):
            PIL_drawer = PIL.ImageDraw.Draw(img)

            # PIL doesnt support transforms, so must get the pixel coords of the coordinate
            # here only for y, because x is handled for each line depending on justify option below
            x,y = xleft,ytop = pos
            xwidth,yheight = size
            
            # wrap text into lines, and write each line
            horizjustify = options["justify"].lower()
            for textline in textlines:
                # horizontally justify the text relative to the bbox edges
                fontwidth, fontheight = font.getsize(textline)
                if horizjustify == "center":
                    x = int(xleft + xwidth/2.0 - fontwidth/2.0)
                elif horizjustify == "right":
                    x = xleft + xwidth - fontwidth
                elif horizjustify == "left":
                    x = xleft
                # draw and increment downwards
                PIL_drawer.text((x,y), textline, fill=options["textcolor"], font=font)
                y += fontheight

        if xy:
            x,y = xy

            # process text options
            fontlocation = fonthelper.get_fontpath(options["font"])

            # PIL doesnt support transforms, so must get the pixel coords of the coordinate
            x,y = xorig,yorig = self.coord2pixel(x,y)

            # offset
            xoffset,yoffset = options.get("xoffset"),options.get("yoffset")
            if xoffset or yoffset:
                x,y = xorig,yorig = self._offset_xy((x,y), xoffset, yoffset)
            
            # get font dimensions
            textlines = text.split("\n")
            font = PIL.ImageFont.truetype(fontlocation, size=options["textsize"]) #, opacity=options["textopacity"])
            widths,heights = zip(*[font.getsize(line) for line in textlines])
            maxwidth, maxheight = max(widths),sum(heights)
            
            # anchor
            def anchor_offset(x, y, anchor, size):
                # update to post-rotate anchor
                itemwidth,itemheight = size
                if anchor == "center":
                    x = int(x - itemwidth/2.0)
                    y = int(y - itemheight/2.0)
                else:
                    x = int(x - itemwidth/2.0)
                    y = int(y - itemheight/2.0)
                    if "n" in anchor:
                        y = int(y + itemheight/2.0)
                    elif "s" in anchor:
                        y = int(y - itemheight/2.0)
                    if "e" in anchor:
                        x = int(x - itemwidth/2.0)
                    elif "w" in anchor:
                        x = int(x + itemwidth/2.0)
                return x,y
            
            textanchor = options["anchor"].lower()
            x,y = anchor_offset(x, y, textanchor, (maxwidth,maxheight))

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
                x2,y2 = self.pixel2coord(x+maxwidth, y+maxheight)
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

            if rotate:
                # write and rotate separate img
                txt_img = PIL.Image.new('RGBA', (maxwidth,maxheight))
                draw_textlines(txt_img, textlines, (0,0), (maxwidth,maxheight), **options)
                txt_img = txt_img.rotate(rotate, PIL.Image.BILINEAR, expand=1)
                pastex,pastey = anchor_offset(xorig, yorig, textanchor, txt_img.size)
                # paste into main
                self.drawer.flush()
                self.img.paste(txt_img, (pastex,pastey), txt_img)

            else:
                self.drawer.flush()
                draw_textlines(self.img, textlines, (x,y), (maxwidth,maxheight), **options)

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
            if boxwidth < 5 or boxheight < 5:
                # box to write text is so small that it doesnt fit in five pixel, dont draw
                return None

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

            self.drawer.flush()
            draw_textlines(self.img, textlines, (xmin,ymin), (boxwidth,boxheight), **options)

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
            
        if "shape" in options:
            draw_point = getattr(self, "draw_%s" % options["shape"])
        else:
            draw_point = self.draw_circle

        geotype = geojson["type"]
        coords = geojson["coordinates"]
        if geotype == "Point":
            draw_point(xy=coords, **options)
        elif geotype == "MultiPoint":
            for point in coords:
                draw_point(xy=point, **options)
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

    def parse_relative_dist(self, dist):
       return units.parse_dist(dist,
                                 ppi=self.ppi,
                                 default_unit=self.default_unit,
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])

    def parse_relative_units(self, coordinates):
        return [(units.parse_dist(point[0],
                                 ppi=self.ppi,
                                 default_unit=self.default_unit,
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height]),
                 units.parse_dist(point[1],
                                 ppi=self.ppi,
                                 default_unit=self.default_unit,
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height]) )
                for point in coordinates]











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
        if "fillsize" in customoptions:
            customoptions["fillsize"] = units.parse_dist(customoptions["fillsize"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillsize"] = units.parse_diststring("0.7%min", ppi=self.ppi, canvassize=[self.width,self.height])
        if "fillwidth" in customoptions:
            customoptions["fillwidth"] = units.parse_dist(customoptions["fillwidth"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillwidth"] = customoptions["fillsize"] * 2
        if "fillheight" in customoptions:
            customoptions["fillheight"] = units.parse_dist(customoptions["fillheight"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["fillheight"] = customoptions["fillsize"] * 2
        # outlinewidth
        if "outlinewidth" in customoptions:
            customoptions["outlinewidth"] = units.parse_dist(customoptions["outlinewidth"],
                                                         ppi=self.ppi,
                                                         default_unit=self.default_unit,
                                                         canvassize=[self.width,self.height],
                                                         coordsize=[self.coordspace_width,self.coordspace_height])
        else:
            customoptions["outlinewidth"] = units.parse_diststring("0.07%min", ppi=self.ppi, canvassize=[self.width,self.height])
        
        # colors
        if "fillcolor" not in customoptions:
            customoptions["fillcolor"] = tuple([random.randrange(0,255) for _ in xrange(3)])
        if "outlinecolor" not in customoptions:
            customoptions["outlinecolor"] = (0,0,0)

        # force to tuple of ints so user doesnt have to
        if isinstance(customoptions["fillcolor"], (tuple,list)):
            customoptions["fillcolor"] = tuple(map(int,customoptions["fillcolor"]))
        if isinstance(customoptions["outlinecolor"], (tuple,list)):
            customoptions["outlinecolor"] = tuple(map(int,customoptions["outlinecolor"]))
            
        # finish  
        return customoptions

    def _check_text_options(self, customoptions):
        customoptions = customoptions.copy()

        def calc_fontsize(width=None, height=None, font=None):
            #### process text options
            fontlocation = fonthelper.get_fontpath(font)

            #### incrementally cut size in half or double it until within 20 percent of desired height
            infiloop = False
            prevsize = None
            cursize = 12
            nextsize = None
            
            while True: 
                # calculate size metrics for current
                font = PIL.ImageFont.truetype(fontlocation, size=cursize) 
                fontwidth, fontheight = font.getsize("H") # arbitrary big character, we are only interested in height

                refsize = width if width else height
                refratio = fontheight / float(refsize)

                # exit if size is within threshold of target size
                ## print fontheight,refsize,refratio
                if 0.9 <= refratio <= 1.1:
                    break 

                # break out of infinite loop between two almost same sizes
                if infiloop:
                    ## print("infinite loop, break!")
                    break

                # check if too big or small
                toobig = False
                toosmall = False
                if refratio < 1:
                    toosmall = True
                else:
                    toobig = True

                # mark as infinite loop once increments get smaller than 1
                if prevsize and cursize-prevsize in (-1,0,1):
                    infiloop = True
                    # prefer to choose the smaller of the two repeating sizes
                    if toobig:
                        nextsize = cursize-1

                # or if prev change went too far, try in between prev and cur size
                elif prevsize and ((toosmall and prevsize > cursize) or (toobig and prevsize < cursize)):
                    ## print("too far, flip!")
                    nextsize = int(round((prevsize + cursize) / 2.0))

                # otherwise double or halve size based on fit
                else:
                    if toobig:
                        nextsize = int(round(cursize / 2.0))
                        ## print("too big!")
                    elif toosmall:
                        nextsize = cursize * 2
                        ## print("too small!")

                # update vars for next iteration
                ## print(prevsize, cursize, nextsize)
                prevsize = cursize
                cursize = nextsize

            return cursize

        def parse_textsize(size, font):
            # determine target pixel size
            if isinstance(size, str):
                if size.endswith("%"):
                    defsize = parse_textsize(self.textoptions["textsize"], font=font)
                    size = defsize * float(size[:-1]) / 100.0
                    return size
                else:
                    if size.endswith("%min"):
                        if self.width <= self.height:
                            size = size.replace("%min","%w")
                        elif self.height < self.width:
                            size = size.replace("%min","%h")
                    elif size.endswith("%max"):
                        if self.width >= self.height:
                            size = size.replace("%max","%w")
                        elif self.height > self.width:
                            size = size.replace("%max","%h")
                            
                    if size.endswith("%w"):
                        percnum = float(size[:-2])
                        percpix = self.width / 100.0 * percnum
                        return calc_fontsize(width=percpix, font=font)
                    elif size.endswith("%h"):
                        percnum = float(size[:-2])
                        percpix = self.height / 100.0 * percnum
                        return calc_fontsize(height=percpix, font=font)

            else:
                if self.ppi != 97:
                    size *= self.ppi / 97.0 # textsize pixel resolution assumes 97 ppi, so must be adjusted for desired ppi
                return size

        finaloptions = self.textoptions.copy()
        finaloptions.update(customoptions)

        textsize = parse_textsize(finaloptions["textsize"], font=finaloptions["font"])
        finaloptions["textsize"] = int(round(textsize))
        
        return finaloptions

    def _offset_xy(self, xy, xoffset=None, yoffset=None):
        x,y = xy
        if xoffset:
            x += units.parse_dist(xoffset,
                                 ppi=self.ppi,
                                 default_unit=self.default_unit,
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        if yoffset:
            y += units.parse_dist(yoffset,
                                 ppi=self.ppi,
                                 default_unit=self.default_unit,
                                 canvassize=[self.width,self.height],
                                 coordsize=[self.coordspace_width,self.coordspace_height])
        return (x,y)





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





