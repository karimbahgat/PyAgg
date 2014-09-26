
# Check dependencies
import PIL, PIL.Image, PIL.ImageTk
import aggdraw
import affine



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
        pass

    def rotate(self, angle):
        pass

    def flip():
        pass

    def move():
        pass

    def crop():
        pass

    def skew():
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



    # Drawing

    def coordinate_space(self, bbox=None, center=None, width=None, height=None, lock_ratio=False):
        """
        Defines which areas of the screen represent which areas in the
        given drawing coordinates. Default is to draw directly with
        screen pixel coordinates. Call this method with no arguments to
        reset to this default. The screen coordinates can be specified in
        two ways: with a bounding box, or with a coordinate point to center
        the view on. WARNING: Currently, if using the center approach you
        cannot specify the direction of the axes, so the zero-point is simply
        assumed to be in the topleft. 

        - bbox: If supplied, each corner of the bbox will be mapped to each corner of the screen.
        - center: The coordinate point to focus on at the center of the screen.
        - width: Width to see around the center point. 
        - height: Height to see around the center point.
        - lock_ratio: Set to True if wanting to constrain the coordinate space to have the same width/height ratio as the image, in order to avoid distortion. Default is False. 

        """
        # default to pixel coords if empty
        if bbox == center == width == height == None:
            self.drawer.settransform()

        # basic info
        xleft,ytop,xright,ybottom = bbox
        x2x = (xleft,xright)
        y2y = (ybottom,ytop)
        xwidth = max(x2x)-min(x2x)
        yheight = max(y2y)-min(y2y)

        # calculate bbox from center if provided
        if not bbox and center:
            midx,midy = center
            halfwidth = width / 2.0
            halfheight = height / 2.0
            bbox = [midx - halfwidth, midy - halfheight,
                    midx + halfwidth, midy + halfheight]

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
                    
##            if screenratio < 1:
##                yheight = xwidth/float(screenratio)
##            elif screenratio > 1:
##                xwidth = yheight * screenratio
            
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
        a,b,c,d,e,f = transcoeffs
        self.drawer.settransform((a,b,c,d,e,f))

    def draw_point(self, xy, symbol="circle", **options):
        """
        Draw a point as one of several symbol types.
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

    def draw_lines(self, coords, **options):
        """
        Connect a series of flattened coordinate points with one or more lines.
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




    # Interactive

    def pixelcoord(px, py):
        pass




    # Viewing and Saving

    def get_tkimage(self):
        self.drawer.flush()
        return PIL.ImageTk.PhotoImage(self.img)

    def save(self, filepath):
        self.drawer.flush()
        self.img.save(filepath)


##    def draw_text(self, relx, rely, text, options):
##        """
##        draws basic text, no effects
##        """
##        fontlocation = self.sysfontfolders[OSSYSTEM]+self.fontfilenames[options["textfont"]]
##        font = aggdraw.Font(color=options["textcolor"], file=fontlocation, size=options["textsize"], opacity=options["textopacity"])
##        fontwidth, fontheight = self.drawer.textsize(text, font)
##        textanchor = options.get("textanchor")
##        if textanchor:
##            textanchor = textanchor.lower()
##            if textanchor == "center":
##                x = int(MAPWIDTH*relx) - int(fontwidth/2.0)
##                y = int(MAPHEIGHT*rely) - int(fontheight/2.0)
##            else:
##                x = int(MAPWIDTH*relx) - int(fontwidth/2.0)
##                y = int(MAPHEIGHT*rely) - int(fontheight/2.0)
##                if "n" in textanchor:
##                    y = int(MAPHEIGHT*rely)
##                elif "s" in textanchor:
##                    y = int(MAPHEIGHT*rely) - int(fontheight)
##                if "e" in textanchor:
##                    x = int(MAPWIDTH*relx) - int(fontwidth)
##                elif "w" in textanchor:
##                    x = int(MAPWIDTH*relx)
##        if options.get("textboxfillcolor") or options.get("textboxoutlinecolor"):
##            relfontwidth, relfontheight = (fontwidth/float(MAPWIDTH), fontheight/float(MAPHEIGHT))
##            relxmid,relymid = (x/float(MAPWIDTH)+relfontwidth/2.0,y/float(MAPHEIGHT)+relfontheight/2.0)
##            relupperleft = (relxmid-relfontwidth*options["textboxfillsize"]/2.0, relymid-relfontheight*options["textboxfillsize"]/2.0)
##            relbottomright = (relxmid+relfontwidth*options["textboxfillsize"]/2.0, relymid+relfontheight*options["textboxfillsize"]/2.0)
##            options["fillcolor"] = options["textboxfillcolor"]
##            options["outlinecolor"] = options["textboxoutlinecolor"]
##            options["outlinewidth"] = options["textboxoutlinewidth"]
##            self.RenderRectangle(relupperleft, relbottomright, options)
##        self.drawer.text((x,y), text, font)









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


    renderer = AggRenderer()
    renderer.new_image(600, 600, (222,0,0))
    renderer.coordinate_space([0, 0, 1000, 600], lock_ratio=True)
    renderer.draw_polygon(coords=[100,100, 900,100, 900,500, 100,500, 100,100],
                        holes=[[400,400, 600,400, 600,450, 400,450, 400,400]],
                        fillcolor=random_n(0,222,n=3),
                        outlinecolor=random_n(0,222,n=3),
                        outlinewidth=10)
    renderer.draw_point(xy=random_n(0, 300, n=2),
                        fillsize=22,
                        fillcolor=random_n(0,222,n=3),
                        outlinecolor=random_n(0,222,n=3),
                        outlinewidth=10)
    img = renderer.get_tkimage()
    label["image"] = label.img = img


    window.mainloop()




