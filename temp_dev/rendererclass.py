
# Check dependencies
try:
    import PIL, PIL.Image, PIL.ImageTk
except ImportError:
    raise Exception("The renderer requires PIL or Pillow but could not find it")
try:
    import aggdraw
except ImportError:
    raise Exception("The renderer requires aggdraw but could not find it")




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

    def coordinate_space(self, bbox):
        """
        Check link for how to do this: http://docs.opencv.org/doc/tutorials/imgproc/imgtrans/warp_affine/warp_affine.html
        """
        # its ratio compared to original * new + offset as ratio of orig * new
        xleft,ytop,xright,ybottom = bbox
        x2x = (xleft,xright)
        y2y = (ybottom,ytop)
        xwidth = max(x2x)-min(x2x)
        yheight = max(y2y)-min(y2y)
        #xprod = self.width * self.width / float(xwidth * self.width)
        #yprod = self.height * self.height / float(yheight * self.height)
        xprod = self.width / float(xwidth)
        yprod = self.height / float(yheight)
        xoffset = (-xleft / float(xwidth) * self.width) #- (xwidth * xprod)
        yoffset = (-ytop / float(yheight) * self.height) #- (yheight * yprod)
        transcoeffs = (xprod, 0, xoffset,
                       0, yprod, yoffset)
        print transcoeffs
        a,b,c,d,e,f = transcoeffs
        for x,y in grouper([100,100, 900,100, 900,500, 100,500, 100,100], 2):
            print (x,y),"=",(x*a + y*b + c, x*d + y*e + f)
        self.drawer.settransform(transcoeffs)

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
    renderer.new_image(300, 300)
    renderer.coordinate_space([0,0,1000,600])
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




