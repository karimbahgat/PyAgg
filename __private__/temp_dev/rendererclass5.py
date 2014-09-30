
# Check dependencies
import PIL, PIL.Image, PIL.ImageTk
import aggdraw
import affine



# Define some globals
import sys, os
platforms = {"win32":"windows",
             "darwin":"apple",
             "linux":"linux",
             "linux2":"linux"}
OSSYSTEM = platforms[sys.platform]



# Some convenience functions
import itertools
def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=None, *args)



# Main class
class AggRenderer:
    """
    This class is used to draw each feature with aggdraw as long as 
    it is given instructions via a color/size/options dictionary.
    """
    
    def __init__(self):
        self.sysfontfolders = dict([("windows","C:/Windows/Fonts/")])
        self.fontfilenames = dict([("default", "TIMES.TTF"),
                                   ("times new roman","TIMES.TTF"),
                                   ("arial","ARIAL.TTF")])
        
    def new_image(self, width, height, background=None, mode="RGBA"):
        """
        This must be called before doing any rendering.
        Note: this replaces any previous image drawn on so be sure to
        retrieve the old image before calling it again to avoid losing work
        """
        self.img = PIL.Image.new(mode, (width, height), background)
        self.width,self.height = width,height
        self.drawer = aggdraw.Draw(self.img)



    # Image operations

    def resize(self, width, height):
        return self.resize((width, height))

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

    def draw_figureplot(self, image, bbox, xaxis, yaxis):
        # maybe by creating and drawing on images as subplots,
        # and then passing them in as figures that draw their
        # own coordinate axes if specified and then paste themself. 
        pass

    def zoom_units(self, per_cm, center=None):
        """
        if no given center, defaults to middle of previous zoom.
        
        - level: how many coordinate units per screen cm at the new zoom level.
        
        """
        # calculate pixels per unit etc
        unitscm = per_cm
        cmsunit = 1 / float(unitscm)
        pixscm = 28.346457
        pixsunit = pixscm * cmsunit
        unitswidth = self.width / float(pixsunit) # use as the width of the bbox
        unitsheight = self.height / float(pixsunit) # use as the height of the bbox
        print "just testing, not done: %s unitscm -> %s coorddims" %(unitscm, (unitswidth,unitsheight))
        
        #if center:
        #    midx,midy = center
        #    halfwidth = width / 2.0
        #    halfheight = height / 2.0
        #    bbox = [midx - halfwidth, midy - halfheight,
        #            midx + halfwidth, midy + halfheight]
        #else:
        #    # expand/shrink the bbox from previous zoom level by the level factor
        #    pass
        # ...
        pass

    def zoom_factor(self, bbox):
        """
        Zooms x times of previous bbox.
        """
        pass

    def zoom_bbox(self, bbox):
        """
        Essentially the same as using coord_space, but assumes that
        you only want to stay within the previous coordinate boundaries,
        so checks for this and also does not allow changing axis directions. 
        """
        pass

    def pixel_space(self):
        """
        Convenience method for setting the coordinate space to pixels,
        so the user can easily draw directly to image pixel positions.
        """
        self.drawer.settransform()

    def fraction_space(self):
        """
        Convenience method for setting the coordinate space to fractions,
        so the user can easily draw using relative fractions (0-1) of image.
        """
        self.coordinate_space([0,0,1,1])

    def percent_space(self):
        """
        Convenience method for setting the coordinate space to percentages,
        so the user can easily draw coordinates as percentage (0-100) of image.
        """
        self.coordinate_space([0,0,100,100])

    def geographic_space(self):
        """
        Convenience method for setting the coordinate space to geographic,
        so the user can easily draw coordinates as lat/long of world.
        """
        self.coordinate_space([-180,90,180,-90], lock_ratio=True)

    def coordinate_space(self, bbox, lock_ratio=False):
        """
        Defines which areas of the screen represent which areas in the
        given drawing coordinates. Default is to draw directly with
        screen pixel coordinates. 

        - bbox: Each corner of the coordinate bbox will be mapped to each corner of the screen.
        - lock_ratio: Set to True if wanting to constrain the coordinate space to have the same width/height ratio as the image, in order to avoid distortion. Default is False. 

        """

        # basic info
        xleft,ytop,xright,ybottom = bbox
        x2x = (xleft,xright)
        y2y = (ybottom,ytop)
        xwidth = max(x2x)-min(x2x)
        yheight = max(y2y)-min(y2y)

        # constrain the coordinate view ratio to the screen ratio, shrinking the coordinate space to ensure that it is fully contained inside the image
        if lock_ratio:
            coordxratio = xwidth/float(yheight)
            screenxratio = self.width/float(self.height)
            if coordxratio > 1:
                if screenxratio > coordxratio:
                    xwidth = yheight * screenxratio
                else:
                    yheight = xwidth / float(screenxratio)
                print xwidth,yheight
            elif coordxratio < 1:
                if screenxratio > coordxratio:
                    if screenxratio > 1:
                        xwidth = yheight * screenxratio
                    else:
                        xwidth,yheight = yheight,xwidth
                        yheight = xwidth / float(screenxratio)
                else:
                    xwidth,yheight = yheight,xwidth
                    yheight = xwidth / float(screenxratio)
            
            # maybe move the center of focus to middle of coordinate space if view ratio has been constrained
            # ...
            
        # Note: The sequence of matrix multiplication is important and sensitive.

        # scale ie resize world to screen coords
        scalex = self.width / float(xwidth)
        scaley = self.height / float(yheight)
        scaled = affine.Affine.scale(scalex,scaley)
        scaled *= affine.Affine.translate(-xleft,-ytop) # to force anchor upperleft world coords to upper left screen coords

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
        transcoeffs = (scaled * flipped).coefficients
        self.transcoeffs = transcoeffs
        a,b,c,d,e,f = transcoeffs
        for x,y in grouper([100,100, 900,100, 900,500, 100,500, 100,100], 2):
            print (x,y),"=",(x*a + y*b + c, x*d + y*e + f)
        self.drawer.settransform((a,b,c,d,e,f))

        # finally remember the new coordinate extents and affine matrix
        # ...




    # Drawing
    
    def draw_point(self, xy, symbol="circle", **options):
        """
        Draw a point/spot/marker as one of several symbol types.
        """
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

    def draw_lines(self, coords, smooth=False, **options):
        """
        Connect a series of flattened coordinate points with one or more lines.

        - coords: A list of coordinates for the linesequence.
        - smooth: If True, smooths the lines by drawing quadratic bezier curves between midpoints of each line segment.
        """
        path = aggdraw.Path()

        def traverse_linestring(coords):
            # begin
            coords = grouper(coords, 2)
            startx,starty = next(coords)
            path.moveto(startx, starty)
            
            # connect to each successive point
            for nextx,nexty in coords:
                path.lineto(nextx, nexty)

        def traverse_curvelines(coords):
            # draw straight line to first line midpoint
            # for each linepair
            #    curve from midpoint of first to midpoint of second
            # draw straight line to endpoint of last line
            pass

        if smooth: traverse_curvelines(coords)
        else: traverse_linestring(coords)
        
        # get drawing tools from options
        args = []
        if options["outlinecolor"]:
            pen = aggdraw.Pen(options["outlinecolor"], options["outlinewidth"])
            args.append(pen)
        if options["fillcolor"]:
            brush = aggdraw.Brush(options["fillcolor"])
            args.append(brush)

        # draw the constructed path
        self.drawer.path((0,0), path, *args)

    def draw_polygon(self, coords, holes=[], **options):
        """
        Draw polygon and holes with color fill.
        Note: holes must be counterclockwise. 
        """
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
        fontlocation = self.sysfontfolders[OSSYSTEM]+self.fontfilenames[options["textfont"]]
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

    def pixelcoord(px, py):
        pass

    def coordpixel(cx, cy):
        pass




    # Viewing and Saving

    def get_tkimage(self):
        self.drawer.flush()
        return PIL.ImageTk.PhotoImage(self.img)

    def view(self):
        # ...
        pass

    def save(self, filepath):
        self.drawer.flush()
        self.img.save(filepath)







if __name__ == "__main__":

    # Test

    import Tkinter as tk

    window = tk.Tk()
    label = tk.Label(window)
    label.pack()


    import random
    def random_n(minval, maxval, n=1):
        ns = (random.randrange(minval,maxval) for _ in xrange(n))
        return tuple(ns)


    # initiate
    renderer = AggRenderer()
    renderer.new_image(1000, 600, random_n(0,222,n=3))
    renderer.coordinate_space([0, 0, 1000, 600], lock_ratio=True)

    # test zoom
    renderer.zoom_units(per_cm=50)
    renderer.coordinate_space([0,0,1763.8888697800926,1058.3333218680557])

    # polygon with hole
    renderer.draw_polygon(coords=[100,100, 900,100, 900,500, 100,500, 100,100],
                        holes=[[400,400, 600,400, 600,450, 400,450, 400,400]],
                        fillcolor=random_n(0,222,n=3),
                        outlinecolor=random_n(0,222,n=3),
                        outlinewidth=10)

    # random points
    for _ in xrange(100):
        renderer.draw_point(xy=random_n(0, 1000, n=2),
                            fillsize=22,
                            fillcolor=random_n(0,222,n=4),
                            outlinecolor=random_n(0,222,n=3),
                        outlinewidth=7)

    # cross lines in percent space
    renderer.percent_space()
    renderer.draw_lines([0,0, 100,100],
                        fillcolor=random_n(0,222,n=3),
                        outlinecolor=random_n(0,222,n=3),
                        outlinewidth=10)
    renderer.draw_lines([100,0, 0,100],
                        fillcolor=random_n(0,222,n=3),
                        outlinecolor=random_n(0,222,n=3),
                        outlinewidth=10)
    
##    renderer.draw_text(100, 100,
##                       text="Hello world!",
##                       textfont="default",
##                       textsize=9,
##                       textcolor=(222,222,222),
##                       textopacity=222,
##                       textboxfillcolor="",
##                       textboxfillsize=1.1,
##                       textboxoutlinecolor="",
##                       textboxoutlinewidth=2)
    
    img = renderer.get_tkimage()
    label["image"] = label.img = img

    window.mainloop()




