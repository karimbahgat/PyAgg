
import Tkinter as tk
from PIL import Image, ImageTk
import aggdraw

window = tk.Tk()
label = tk.Label(window)
label.pack()




# schedule changing images
import itertools, random, time

def agg2tkimg(aggimage):
    t = time.clock()
    img = aggimage
    colorlength = len(img.mode)
    width,height = img.size
    imgbytes = img.tostring()

    # via PIL/PILLOW for fast window updates
    tempimg = Image.fromstring("RGBA", (width,height), data=imgbytes)
    tkimg = ImageTk.PhotoImage(image=tempimg)
    
    return tkimg

def random_n(minval, maxval, n=1):
    ns = (random.randrange(minval,maxval) for _ in xrange(n))
    return tuple(ns)

def draw_polygon(img, coords):
    pen = aggdraw.Pen(random_n(0,222,n=3), width=int(img.size[0]*0.001))
    brush = aggdraw.Brush(random_n(0,222,n=3))
    # draw
    img.polygon(coords, pen, brush)

def update(img):
    # update
    img.flush()
    tkimg = agg2tkimg(img)
    label["image"] = label.img = tkimg


# Begin #

img = aggdraw.Draw("RGBA", (1000,600), random_n(0,222,n=3) )

import geovis
sf = geovis.shapefile_fork.Reader("D:/Test Data/cshapes/cshapes.shp")
for shape in sf.iterShapes():
    if shape.__geo_interface__["type"] == "Polygon":
        flatcoords = [xory+350 for xy in shape.__geo_interface__["coordinates"][0] for xory in xy]
        draw_polygon(img, flatcoords)

update(img)

window.mainloop()


