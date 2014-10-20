# Check dependencies
import PIL, PIL.Image, PIL.ImageTk
try: import PIL, PIL.Image, PIL.ImageTk ; hasPIL = True
except ImportError: hasPIL = False

# Import builtins
import Tkinter as tk
import struct
import itertools
import random

# Import submodules
from . import affine

# Define some globals
import sys, os
OSSYSTEM = {"win32":"windows",
             "darwin":"mac",
             "linux":"linux",
             "linux2":"linux"}[sys.platform]
PYVERSION = sys.version[:3]
SYSFONTFOLDERS = dict([("windows","C:/Windows/Fonts/"),
                       ("mac", "/Library/Fonts/"),
                       ("linux", "/usr/share/fonts/truetype/")])
FONTFILENAMES = dict([("default", "TIMES.TTF"),
                        ("times new roman","TIMES.TTF"),
                        ("arial","ARIAL.TTF")])

# Import correct AGG binaries
try:
    if OSSYSTEM == "windows":
        if PYVERSION == "2.6": from .precompiled.win.py26 import aggdraw
        elif PYVERSION == "2.7": from .precompiled.win.py27 import aggdraw
    elif OSSYSTEM == "mac":
        if PYVERSION == "2.6": raise ImportError("Currently no Mac precompilation for Py27")
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

def bbox_offset(bbox, xoff, yoff):
    pass





# Main class
class Canvas:
    """
    This class is a painter's canvas on which to draw with aggdraw.
    """
    
    def __init__(self, width, height, background=None, mode="RGBA"):
        if hasPIL:
            self.img = PIL.Image.new(mode, (width, height), background)
            self.drawer = aggdraw.Draw(self.img)
        else:
            self.drawer = aggdraw.Draw(mode, (width, height), background)
            self.img = self.drawer
        self.width,self.height = width,height
        self.pixel_space()



    # Image operations

    def resize(self, width, height):
        return self.img.resize((width, height))

    def rotate(self, angle):
        return self.img.rotate(angle)

    def flip(xflip=True, yflip=False):
        img = self.img
        if xflip: img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        if yflip: img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        return img

    def move(self, xmove, ymove):
        return self.img.offset(xmove, ymove)

    def paste(self, image, xy):
        return self.img.paste(image, xy)

    def crop(self, bbox):
        return self.img.crop(bbox)

    def skew():
        # ...
        pass

    def tilt_right(self, angle):
        # use pyeuclid to get the Matrix4 coefficients for the PIL perspective function
        pass

    def tilt_top(self, angle):
        # use pyeuclid to get the Matrix4 coefficients for the PIL perspective function
        pass
    


    # Color quality

    def brightness():
        pass

    def contrast():
        pass

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
        self.coordinate_space(*newbbox, lock_ratio=True)

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
        self.coordinate_space(*newbbox, lock_ratio=False)

    def zoom_bbox(self, xleft, ytop, xright, ybottom):
        """
        Essentially the same as using coord_space, but assumes that
        you only want to stay within the previous coordinate boundaries,
        so checks for this and also does not allow changing axis directions. 
        """
        oldxleft, oldytop, oldxright, oldybottom = self.coordspace_bbox
        # ensure old and zoom axes go in same directions
        if not (xleft < xright) == (oldxleft < oldxright) or not (ytop < ybottom) == (oldytop < oldybottom):
            raise Exception("Zoom error: Zoom bbox must follow the same axis directions as the canvas' coordinate space.")
        # zoom it
        self.coordinate_space(xleft, ytop, xright, ybottom, lock_ratio=True)

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
        self.coordinate_space(*[0,0,1,1])

    def percent_space(self):
        """
        Convenience method for setting the coordinate space to percentages,
        so the user can easily draw coordinates as percentage (0-100) of image.
        """
        self.coordinate_space(*[0,0,100,100])

    def geographic_space(self):
        """
        Convenience method for setting the coordinate space to geographic,
        so the user can easily draw coordinates as lat/long of world.
        """
        self.coordinate_space(*[-180,90,180,-90], lock_ratio=True)

    def coordinate_space(self, xleft, ytop, xright, ybottom,
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

    def draw_geoj(self, geojobj):
        pass
    
    def draw_point(self, xy, symbol="circle", **options):
        """
        Draw a point/spot/marker as one of several symbol types.
        """
        options = self._check_options(options)
        
        args = []
        fillsize = options["fillsize"]
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)
        x,y = xy
        bbox = [x-fillsize, y-fillsize, x+fillsize, y+fillsize]
        if symbol == "circle":
            self.drawer.ellipse(bbox, *args)
        elif symbol == "square":
            self.drawer.rectangle(bbox, *args)

    def draw_line(self, coords, smooth=False, **options):
        """
        Connect a series of flattened coordinate points with one or more lines.

        - coords: A list of coordinates for the linesequence.
        - smooth: If True, smooths the lines by drawing quadratic bezier curves between midpoints of each line segment.
        """
        options = self._check_options(options)
        
        path = aggdraw.Path()

        def traverse_straightlines(coords):
            pathstring = ""
            
            # begin
            coords = grouper(coords, 2)
            startx,starty = next(coords)
            pathstring += " M%s,%s" %(startx, starty)
            
            # connect to each successive point
            for nextx,nexty in coords:
                pathstring += " L%s,%s" %(nextx, nexty)

            # make into symbol object
            symbol = aggdraw.Symbol(pathstring)
            return symbol

        def traverse_curvelines(coords):
            pathstring = ""
            
            # begin
            coords = pairwise(grouper(coords, 2))
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
            return symbol

        if smooth: symbol = traverse_curvelines(coords)
        else: symbol = traverse_straightlines(coords)
        
        # get drawing tools from options
        args = []
        if options["fillcolor"]:
            pen = aggdraw.Pen(options["fillcolor"], options["fillsize"])
            args.append(pen)

        # draw the constructed path
        self.drawer.symbol((0,0), symbol, *args)

    def draw_polygon(self, coords, holes=[], **options):
        """
        Draw polygon and holes with color fill.
        Note: holes must be counterclockwise. 
        """
        options = self._check_options(options)
        
        path = aggdraw.Path()

        def traverse_ring(coords):
            # begin
            coords = grouper(coords, 2)
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
            hole = (xory for point in reversed(tuple(grouper(hole, 2))) for xory in point)
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

    def draw_text(self, x, y, text, **options):
        """
        draws basic text, no effects
        """
        fontlocation = SYSFONTFOLDERS[OSSYSTEM]+FONTFILENAMES[options["textfont"]]
        font = aggdraw.Font(color=options["textcolor"], file=fontlocation, size=options["textsize"], opacity=options["textopacity"])
        fontwidth, fontheight = self.drawer.textsize(text, font)
        textanchor = options.get("textanchor")
        if textanchor:
            textanchor = textanchor.lower()
            if textanchor == "center":
                x = int(x) - int(fontwidth/2.0)
                y = int(y) - int(fontheight/2.0)
            else:
                x = int(x) - int(fontwidth/2.0)
                y = int(y) - int(fontheight/2.0)
                if "n" in textanchor:
                    y = int(y)
                elif "s" in textanchor:
                    y = int(y) - int(fontheight)
                if "e" in textanchor:
                    x = int(x) - int(fontwidth)
                elif "w" in textanchor:
                    x = int(x)
        if options.get("textboxfillcolor") or options.get("textboxoutlinecolor"):
            relfontwidth, relfontheight = (fontwidth/float(MAPWIDTH), fontheight/float(MAPHEIGHT))
            relxmid,relymid = (x/float(MAPWIDTH)+relfontwidth/2.0,y/float(MAPHEIGHT)+relfontheight/2.0)
            relupperleft = (relxmid-relfontwidth*options["textboxfillsize"]/2.0, relymid-relfontheight*options["textboxfillsize"]/2.0)
            relbottomright = (relxmid+relfontwidth*options["textboxfillsize"]/2.0, relymid+relfontheight*options["textboxfillsize"]/2.0)
            options["fillcolor"] = options["textboxfillcolor"]
            options["outlinecolor"] = options["textboxoutlinecolor"]
            options["outlinewidth"] = options["textboxoutlinewidth"]
            self.RenderRectangle(relupperleft, relbottomright, options)
        self.drawer.text((x,y), text, font)





    # Interactive

    def pixel2coord(self, x, y):
        a,b,c,d,e,f = self.coordspace_transform
        newx,newy = (x/a - y/b - c, x/d - y/e - f) # ?
        return newx,newy

    def coord2pixel(self, x, y):
        a,b,c,d,e,f = self.coordspace_transform
        newx,newy = (x*a + y*b + c, x*d + y*e + f)
        return newx,newy
    
    def dist_coord2pixel(self, dist):
        xdist,ydist = self.coord2pixel(dist,dist)
        return xdist

    def dist_pixel2coord(self, dist):
        xdist,ydist = self.pixel2coord(dist,dist)
        return xdist





    # Viewing and Saving

    def get_tkimage(self):
        self.drawer.flush()
        if hasPIL:
            return PIL.ImageTk.PhotoImage(self.img)
        else:
            colorlength = len(self.drawer.mode)
            width,height = self.drawer.size
            imgbytes = self.drawer.tostring()
            imgnrs = struct.unpack("%sB"%(colorlength*width*height), imgbytes)
            rgbs = grouper(imgnrs, colorlength)
            imagegrid = grouper(rgbs, width)
            tkimg = tk.PhotoImage(width=width, height=height)
            imgstring = " ".join(["{"+" ".join(["#"+"%02x"*colorlength %tuple(color) for color in horizline])+"}" for horizline in imagegrid]) # bottleneck 1
            tkimg.put(imgstring) # bottleneck 2
            return tkimg

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
            customoptions["fillsize"] = 0.4
        if not customoptions.get("fillwidth"):
            customoptions["fillwidth"] = 1.2
        if not customoptions.get("fillheight"):
            customoptions["fillheight"] = 0.8
        if customoptions.get("outlinecolor", "not specified") == "not specified":
            customoptions["outlinecolor"] = (0,0,0)
        if not customoptions.get("outlinewidth"):
            customoptions["outlinewidth"] = 0.09 #percent of map
        #convert relative sizes to pixels
        customoptions["fillsize"] = self.width * customoptions["fillsize"] / 100.0
        customoptions["fillwidth"] = self.width * customoptions["fillwidth"] / 100.0
        customoptions["fillheight"] = self.width * customoptions["fillheight"] / 100.0
        customoptions["outlinewidth"] = self.width * customoptions["outlinewidth"] / 100.0
        return customoptions





