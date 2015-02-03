# Check dependencies
import PIL, PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageFont
# Import builtins
import sys, os
import Tkinter as tk
import struct
import itertools
import random

# Import submodules
PYAGGFOLDER = os.path.split(__file__)[0]
sys.path.insert(0, PYAGGFOLDER)
from . import affine
from fontTools.ttLib import TTFont
#print TTFont
#print TTFont("C:/Windows/Fonts/Times.ttf").get("name").names

# Define some globals
OSSYSTEM = {"win32":"windows",
             "darwin":"mac",
             "linux":"linux",
             "linux2":"linux"}[sys.platform]

PYVERSION = sys.version[:3]

SYSFONTFOLDERS = dict([("windows","C:/Windows/Fonts/"),
                       ("mac", "/Library/Fonts/"),
                       ("linux", "/usr/share/fonts/truetype/")])

FONTFILENAMES = dict([(filename.lower(), os.path.join(dirpath, filename))
                       for dirpath,dirnames,filenames in os.walk(SYSFONTFOLDERS[OSSYSTEM])
                      for filename in filenames
                      if filename.endswith(".ttf")])

FONTNAMES = dict()
for filename in FONTFILENAMES.keys():
    metadata = TTFont(FONTFILENAMES[filename]).get("name")
    for info in metadata.names:
        if info.nameID == 4: # font family name with optional bold/italics
            if info.string.startswith("\x00"):
                # somehow the font string has weird byte data in first position and between each character
                fontname = info.string[1::2]
            else:
                fontname = info.string
            break
    FONTNAMES.update([(fontname.lower(), filename)])

def GET_FONTPATH(font):
    font = font.lower()
    # first try to get human readable name from custom list
    if FONTNAMES.get(font):
        return os.path.join(SYSFONTFOLDERS[OSSYSTEM], FONTFILENAMES[FONTNAMES[font]])
    # then try to get from custom font filepath
    elif os.path.lexists(font):
        return font
    # or try to get from filename in font folder
    elif FONTFILENAMES.get(font):
        return FONTFILENAMES[font]
    # raise error if hasnt succeeded yet
    raise Exception("Could not find the font specified. Font must be either a human-readable name, a filename with extension in the default font folder, or a full path to the font file location")
        

# Import correct AGG binaries
try:
    if OSSYSTEM == "windows":
        if PYVERSION == "2.6": from .precompiled.win.py26 import aggdraw
        elif PYVERSION == "2.7": from .precompiled.win.py27 import aggdraw
    elif OSSYSTEM == "mac":
        if PYVERSION == "2.6": raise ImportError("Currently no Mac precompilation for Py26")
        elif PYVERSION == "2.7": from .precompiled.mac.py27 import aggdraw
except ImportError:
    import aggdraw # in case user has compiled a working aggdraw version on their own





# Some convenience functions

def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=None, *args)

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def bbox_resize_ratio(bbox, xratio, yratio):
    # remember old
    x1,y1,x2,y2 = bbox
    x2x = (x1,x2)
    y2y = (y1,y2)
    midx = sum(x2x) / 2.0
    midy = sum(y2y) / 2.0
    halfxwidth = (max(x2x)-min(x2x)) / 2.0
    halfyheight = (max(y2y)-min(y2y)) / 2.0
    # expand or shrink bbox
    if x1 < x2:
        x1 = midx - halfxwidth * xratio
        x2 = midx + halfxwidth * xratio
    else:
        x1 = midx + halfxwidth * xratio
        x2 = midx - halfxwidth * xratio
    if y1 < y2:
        y1 = midy - halfyheight * yratio
        y2 = midy + halfyheight * yratio
    else:
        y1 = midy + halfyheight * yratio
        y2 = midy - halfyheight * yratio
    return [x1,y1,x2,y2]

def bbox_resize_dimensions(bbox, newwidth, newheight):
    xleft,ytop,xright,ybottom = bbox
    x2x = (xleft,xright)
    y2y = (ytop,ybottom)
    xwidth = max(x2x) - min(x2x)
    yheight = max(y2y) - min(y2y)
    xratio = newwidth / float(xwidth)
    yratio = newheight / float(yheight)
    return bbox_resize_ratio(bbox, xratio, yratio)

def bbox_center(bbox, center):
    # remember old
    x1,y1,x2,y2 = bbox
    x2x = (x1,x2)
    y2y = (y1,y2)
    xmin,ymin = min(x2x),min(y2y)
    xmax,ymax = max(x2x),max(y2y)
    halfxwidth = (xmax-xmin) / 2.0
    halfyheight = (ymax-ymin) / 2.0
    centerx, centery = center
    # center it
    xmin = centerx - halfxwidth
    xmax = centerx + halfxwidth
    ymin = centery - halfyheight
    ymax = centery + halfyheight
    # make sure they have same bbox format as when came in
    if x1 < x2: x1,x2 = xmin,xmax
    else: x1,x2 = xmax,xmin
    if y1 < y2: y1,y2 = ymin,ymax
    else: y1,y2 = ymax,ymin
    return [x1,y1,x2,y2]

##def bbox_center(bbox, center):
##    xleft,ytop,xright,ybottom = bbox
##    x2x = (xleft,xright)
##    y2y = (ytop,ybottom)
##    xhalfwidth = (max(x2x) - min(x2x)) / 2.0
##    yhalfheight = (max(y2y) - min(y2y)) / 2.0
##    centerx, centery = center
##    if xleft < xright:
##        xleft = centerx - xhalfwidth
##        xright = centerx + xhalfwidth
##    else:
##        xleft = centerx + xhalfwidth
##        xright = centerx - xhalfwidth
##    if ytop > ybottom:
##        ytop = centery + yhalfheight
##        ybottom = centery - yhalfheight
##    else:
##        ytop = centery - yhalfheight
##        ybottom = centery + yhalfheight
##    return [xleft, ytop, xright, ybottom]

def bbox_offset(bbox, xoffset, yoffset):
    x1,y1,x2,y2 = bbox
    x1,x2 = x1+xoffset,x2+xoffset
    y1,y2 = y1+yoffset,y2+yoffset
    return [x1,y1,x2,y2]
    
##    xleft,ytop,xright,ybottom = bbox
##    x2x = (xleft,xright)
##    y2y = (ytop,ybottom)
##    xhalfwidth = (max(x2x) - min(x2x))
##    yhalfheight = (max(y2y) - min(y2y))
##    centerx, centery = xoffset, yoffset
##    if xleft < xright:
##        xleft = centerx - xhalfwidth
##        xright = centerx + xhalfwidth
##    else:
##        xleft = centerx + xhalfwidth
##        xright = centerx - xhalfwidth
##    if ytop > ybottom:
##        ytop = centery + yhalfheight
##        ybottom = centery - yhalfheight
##    else:
##        ytop = centery - yhalfheight
##        ybottom = centery + yhalfheight
##    return [xleft, ytop, xright, ybottom]





# Main class
def load(filepath):
    canvas = Canvas(100, 100)
    canvas.img = PIL.Image.open(filepath)
    canvas.drawer = aggdraw.Draw(canvas.img)
    canvas.pixel_space()
    return canvas

class Canvas:
    """
    This class is a painter's canvas on which to draw with aggdraw.
    """
    
    def __init__(self, width, height, background=None, mode="RGBA"):
        self.img = PIL.Image.new(mode, (width, height), background)
        self.drawer = aggdraw.Draw(self.img)
        self.background = background
        self.pixel_space()

    @property
    def width(self):
        return self.drawer.size[0]

    @property
    def height(self):
        return self.drawer.size[1]








    # Image operations

    def resize(self, width, height, lock_ratio=False):
        """
        Resize canvas image to new width and height in pixels,
        and the coordinate system will follow.
        """
        # Resize image
        self.drawer.flush()
        self.img = self.img.resize((width, height), PIL.Image.ANTIALIAS)
        self.update_drawer_img()
        # Then update coordspace to match the new image dimensions
        self.custom_space(*self.coordspace_bbox, lock_ratio=lock_ratio)
        return self

    def rotate(self, degrees):
        """
        Rotate the canvas image in degree angles,
        and the coordinate system will follow.
        """
        # NOTE: Also need to update drawing transform to match the new image dimensions
        self.drawer.flush()
        self.img = self.img.rotate(degrees, PIL.Image.BICUBIC)
        self.update_drawer_img()
        return self

    def skew(self):
        """
        Skew the canvas image in pixels,
        and the coordinate system will follow.
        """
        pass

    def flip(self, xflip=True, yflip=False):
        """
        Flip the canvas image horizontally or vertically (center-anchored),
        and the coordinate system will follow. 
        """
        # NOTE: Also need to update drawing transform to match the new image dimensions
        self.drawer.flush()
        img = self.img
        if xflip: img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        if yflip: img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.img = img
        self.update_drawer_img()
        return self

    def move(self, xmove, ymove):
        """
        Move/offset the canvas image in pixels,
        and the coordinate system will follow.
        """
        self.drawer.flush()
        blank = PIL.Image.new(self.img.mode, self.img.size, None)
        blank.paste(self.img, (xmove, ymove))
        self.img = blank
        # similarly move the drawing transform
        # assuming args were in pixels, convert to coord distances
        xmove,ymove = self.pixel2coord_dist(xmove, ymove)
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
        return self

    def paste(self, image, xy=(0,0)):
        """
        Paste the northwest corner of a PIL image
        onto a given pixel location in the Canvas.
        """
        self.drawer.flush()
        if isinstance(image, Canvas): image = image.img
        self.img.paste(image, xy, image)
        self.update_drawer_img()
        return self

    def crop(self, xmin, ymin, xmax, ymax):
        """
        Crop the canvas image to a bounding box defined in pixel coordinates,
        and the coordinate system will follow.
        """
        ### NEW: JUST DO SAME ROUTINE AS "move" AND "resize"
        # HALFWAY THROUGH USING COORDINATES
        # MAYBE GO BACK TO PIXELS ONLY
        # NOTE: Also need to update drawing transform to match the new image dimensions
        self.drawer.flush()

        # convert bbox to pixel positions
        (xmin, ymin), (xmax, ymax) = [self.coord2pixel(xmin, ymin),
                                      self.coord2pixel(xmax, ymax)]

        # ensure pixels are listed in correct left/right top/bottom order
        xleft, ytop, xright, ybottom = xmin, ymin, xmax, ymax
        if xleft > xright: xleft,xright = xright,xleft
        if ytop > ybottom: ytop,ybottom = ybottom,ytop

        # constrain aspect ratio, maybe by applying a new zoom_transform and reading coordbbox
        # ...

        # do the cropping
        pixel_bbox = map(int, [xleft, ytop, xright, ybottom])
        self.img = self.img.crop(pixel_bbox)
        self.update_drawer_img()
        return self

    def update_drawer_img(self):
        # update changes to the aggdrawer, and remember to reapply transform
        self.drawer = aggdraw.Draw(self.img)
        self.drawer.settransform(self.coordspace_transform)








    # Color quality

    def brightness():
        pass

    def contrast():
        pass

    def transparency(self, alpha):
        self.drawer.flush()
        blank = PIL.Image.new(self.img.mode, self.img.size, None)
        self.img = blank.paste(self.img, (0,0), alpha)
        self.update_drawer_img()
        return self

    def color_tint():
        # add rgb color to each pixel
        pass












    # Layout

    def insert_graph(self, image, bbox, xaxis, yaxis):
        # maybe by creating and drawing on images as subplots,
        # and then passing them in as figures that draw their
        # own coordinate axes if specified and then paste themself.
        # ... 
        pass

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
        if no given center, defaults to middle of previous zoom.
        
        - units: how many coordinate units per screen cm at the new zoom level.
        
        """
        # calculate pixels per unit etc
        unitscm = units
        cmsunit = 1 / float(unitscm)
        pixscm = 28.346457
        pixsunit = pixscm * cmsunit
        unitswidth = self.width / float(pixsunit) # use as the width of the bbox
        unitsheight = self.height / float(pixsunit) # use as the height of the bbox
        # zoom it
        newbbox = bbox_resize_dimensions(self.coordspace_bbox,
                                         newwidth=unitswidth,
                                         newheight=unitsheight)
        # center it
        if center:
            newbbox = bbox_center(newbbox, center)
        self.custom_space(*newbbox, lock_ratio=True)

    def zoom_factor(self, factor, center=None):
        """
        Zooms x times of previous bbox. Positive values > 1 for in-zoom,
        negative < -1 for out-zoom. 
        """
        if -1 < factor < 1:
            raise Exception("Zoom error: Zoom factor must be higher than +1 or lower than -1.")
        # positive zoom means bbox must be shrunk
        if factor > 1: factor = 1 / float(factor)
        # remove minus sign for negative zoom
        elif factor <= -1: factor *= -1
        # zoom it
        newbbox = bbox_resize_ratio(self.coordspace_bbox,
                           xratio=factor,
                           yratio=factor)
        # center it
        if center:
            newbbox = bbox_center(newbbox, center)
        self.custom_space(*newbbox, lock_ratio=False)

    def zoom_bbox(self, xmin, ymin, xmax, ymax):
        """
        Essentially the same as using coord_space, but takes bbox
        in min/max format instead, converting to left/right/etc behind
        the scenes. 
        """
        xleft, ybottom, xright, ytop = xmin, ymin, xmax, ymax
        oldxleft, oldytop, oldxright, oldybottom = self.coordspace_bbox
        # ensure old and zoom axes go in same directions
        if not (xleft < xright) == (oldxleft < oldxright):
            xleft,xright = xright,xleft
        if not (ytop < ybottom) == (oldytop < oldybottom):
            ytop,ybottom = ybottom,ytop
        # zoom it
        self.custom_space(xleft, ytop, xright, ybottom, lock_ratio=True)

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
        so the user can easily draw coordinates as lat/long of world.
        """
        self.custom_space(*[-180,90,180,-90], lock_ratio=True)

    def custom_space(self, xleft, ytop, xright, ybottom,
                         lock_ratio=False):
        """
        Defines which areas of the screen represent which areas in the
        given drawing coordinates. Default is to draw directly with
        screen pixel coordinates. 

        - bbox: Each corner of the coordinate bbox will be mapped to each corner of the screen.
        - lock_ratio: Set to True if wanting to constrain the coordinate space to have the same width/height ratio as the image, in order to avoid distortion. Default is False. 

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
            # make coords same proportions as screen
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
        self.coordspace_bbox = bbox_resize_ratio(bbox,
                                           xratio=xwidth / float(oldxwidth),
                                           yratio=yheight / float(oldyheight) )
        self.coordspace_transform = transcoeffs












    # Drawing

    def draw_circle(self, xy=None, bbox=None, flatratio=1, **options):
        """
        Draw a circle, normal or flattened.
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
            width, height = width / self.width * self.coordspace_width, \
                            height / self.height * self.coordspace_height
            if flatratio: height *= flatratio
            halfwidth, halfheight = width / 2.0, height / 2.0
            bbox = [x-halfwidth, y-halfheight, x+halfwidth, y+halfheight]
        
        elif bbox: pass
        
        else: raise Exception("Either xy or bbox has to be specified")
        
        self.drawer.ellipse(bbox, *args)

    def draw_triangle(self, xy=None, bbox=None, **options):
        """
        Draw a triangle, equiangled or otherwise.
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
        """
        options = self._check_options(options)
        x,y = xy
        fillsize = options["fillsize"]
        bbox = [x-fillsize, y-fillsize, x+fillsize, y+fillsize]
        args = []
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
        self.drawer.pieslice(bbox, startangle, endangle, *args)

    def draw_box(self, xy=None, bbox=None, **options):
        """
        Draw a square, equisized or rectangular.
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
            width, height = width / self.width * self.coordspace_width, \
                            height / self.height * self.coordspace_height
            halfwidth, halfheight = width / 2.0, height / 2.0
            bbox = [x-halfwidth, y-halfheight, x+halfwidth, y+halfheight]
        
        elif bbox: pass
        
        else: raise Exception("Either xy or bbox has to be specified")
        
        self.drawer.rectangle(bbox, *args)

    def draw_line(self, coords, smooth=False, **options):
        """
        Connect a series of flattened coordinate points with one or more lines.
        NOTE: Outline does not work bc uses paths instead of normal line method.

        - coords: A list of coordinates for the linesequence.
        - smooth: If True, smooths the lines by drawing quadratic bezier curves between midpoints of each line segment.
        """
        options = self._check_options(options)
        
        if not hasattr(coords[0], "__iter__"):
            coords = grouper(coords, 2)
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
            
            pathstring = ""
            
            # begin
            coords = pairwise(coords)
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
        Note: holes must be counterclockwise. 
        """
        options = self._check_options(options)
        
        path = aggdraw.Path()
        
        if not hasattr(coords[0], "__iter__"):
            coords = grouper(coords, 2)
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
                hole = grouper(hole, 2)
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

    def draw_text(self, xy, text, **options):
        """
        draws basic text, no effects
        """
        x,y = xy
        options = self._check_text_options(options)

        # process text options
        fontlocation = GET_FONTPATH(options["textfont"])
        PIL_drawer = PIL.ImageDraw.Draw(self.img)

        # PIL doesnt support transforms, so must get the pixel coords of the coordinate
        x,y = self.coord2pixel(x,y)
        
        # get font dimensions
        font = PIL.ImageFont.truetype(fontlocation, size=options["textsize"]) #, opacity=options["textopacity"])
        fontwidth, fontheight = font.getsize(text)
        # anchor
        textanchor = options["textanchor"].lower()
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

        # then draw text
        self.drawer.flush()
        # for text wrapping inside bbox, see: http://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil
        # ...
        PIL_drawer.text((x,y), text, fill=options["textcolor"], font=font)
        
        # update changes to the aggdrawer, and remember to reapply transform
        self.drawer = aggdraw.Draw(self.img)
        self.drawer.settransform(self.coordspace_transform)

    def draw_geojson(self, geojobj, **options):
        """
        Takes any geojson dictionary or object that has the __geo_interface__ attribute
        """
        if isinstance(geojobj, dict): geojson = geojobj
        else: geojson = geojobj.__geo_interface__
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

    def draw_svg(self, svg):
        pass










    # Interactive

    def pixel2coord(self, x, y):
        # partly taken from Sean Gillies "affine.py"
        a,b,c,d,e,f = self.coordspace_transform
        det = a*e - b*d
        idet = 1 / float(det)
        ra = e * idet
        rb = -b * idet
        rd = -d * idet
        re = a * idet
        newx = (x*ra + y*rb + (-c*ra - f*rb) )
        newy = (x*rd + y*re + (-c*rd - f*re) )
        return newx,newy

    def pixel2coord_dist(self, x, y):
        # partly taken from Sean Gillies "affine.py"
        a,b,c,d,e,f = self.coordspace_transform
        det = a*e - b*d
        idet = 1 / float(det)
        ra = e * idet
        rb = -b * idet
        rd = -d * idet
        re = a * idet
        newx = (x*ra)
        newy = (y*re)
        return newx,newy

    def coord2pixel(self, x, y):
        a,b,c,d,e,f = self.coordspace_transform
        newx,newy = (x*a + y*b + c, x*d + y*e + f)
        return newx,newy











    # Viewing and Saving

    def clear(self):
        self.img = PIL.Image.new(self.img.mode, self.img.size, self.background)
        self.drawer = aggdraw.Draw(self.img)
        
    def get_image(self):
        self.drawer.flush()
        return self.img
    
    def get_tkimage(self):
        self.drawer.flush()
        return PIL.ImageTk.PhotoImage(self.img)

    def view(self):
        window = tk.Tk()
        label = tk.Label(window)
        label.pack()
        img = self.get_tkimage()
        label["image"] = label.img = img
        window.mainloop()

    def save(self, filepath):
        self.drawer.flush()
        self.img.save(filepath)












    # Internal only

    def _check_options(self, customoptions):
        #types
        customoptions = customoptions.copy()
        #paramaters
        if customoptions.get("fillcolor", "not specified") == "not specified":
            customoptions["fillcolor"] = [random.randrange(0,255) for _ in xrange(3)]
        if not customoptions.get("fillsize"):
            customoptions["fillsize"] = 0.7
        if not customoptions.get("fillwidth"):
            customoptions["fillwidth"] = customoptions["fillsize"] * 2
        if not customoptions.get("fillheight"):
            customoptions["fillheight"] = customoptions["fillsize"] * 2
        if customoptions.get("outlinecolor", "not specified") == "not specified":
            customoptions["outlinecolor"] = (0,0,0)
        if not customoptions.get("outlinewidth"):
            customoptions["outlinewidth"] = 0.07 #percent of map
        #convert relative sizes to pixels
        customoptions["fillsize"] = self.width * customoptions["fillsize"] / 100.0
        customoptions["fillwidth"] = self.width * customoptions["fillwidth"] / 100.0
        customoptions["fillheight"] = self.width * customoptions["fillheight"] / 100.0
        customoptions["outlinewidth"] = self.width * customoptions["outlinewidth"] / 100.0
        return customoptions

    def _check_text_options(self, customoptions):
        customoptions = customoptions.copy()
        #text and font
        if not customoptions.get("textfont"):
            customoptions["textfont"] = "Arial"
            
        # RIGHT NOW, TEXTSIZE IS PERCENT OF IMAGE SIZE, BUT MAYBE USE NORMAL SIZE INSTEAD
        # see: http://stackoverflow.com/questions/4902198/pil-how-to-scale-text-size-in-relation-to-the-size-of-the-image

        if not customoptions.get("textsize"):
            #customoptions["textsize"] = int(round(self.width*0.0055)) #equivalent to textsize 7
            customoptions["textsize"] = 8
        else:
            customoptions["textsize"] = int(round(customoptions["textsize"]))
            #input is percent textheight of MAPWIDTH
            #percentheight = customoptions["textsize"]
            #so first get pixel height
            #pixelheight = self.width*percentheight
            #to get textsize
            #textsize = int(round(pixelheight*0.86))
            #customoptions["textsize"] = textsize
        if not customoptions.get("textcolor"):
            customoptions["textcolor"] = (0,0,0)
##        if not customoptions.get("textopacity"):
##            customoptions["textopacity"] = 255
##        if not customoptions.get("texteffect"):
##            customoptions["texteffect"] = None
        if not customoptions.get("textanchor"):
            customoptions["textanchor"] = "center"
        #text background box
##        if not customoptions.get("textboxfillcolor"):
##            customoptions["textboxfillcolor"] = None
##        else:
##            if customoptions.get("textboxoutlinecolor","not specified") == "not specified":
##                customoptions["textboxoutlinecolor"] = (0,0,0)
##        if not customoptions.get("textboxfillsize"):
##            customoptions["textboxfillsize"] = 1.1 #proportion size of text bounding box
##        if not customoptions.get("textboxoutlinecolor"):
##            customoptions["textboxoutlinecolor"] = None
##        if not customoptions.get("textboxoutlinewidth"):
##            customoptions["textboxoutlinewidth"] = 1.0 #percent of fill, not of map
##        if not customoptions.get("textboxopacity"):
##            customoptions["textboxopacity"] = 0 #both fill and outline
        return customoptions




