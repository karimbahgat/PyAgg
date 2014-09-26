
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
    print time.clock()-t
    
    return tkimg

def random_n(minval, maxval, n=1):
    ns = (random.randrange(minval,maxval) for _ in xrange(n))
    return tuple(ns)

def random_graphic(width, height):
    img = aggdraw.Draw("RGBA", (width,height), random_n(0,222,n=3) )
    pen = aggdraw.Pen(random_n(0,222,n=3), width=int(width*0.10))
    brush = aggdraw.Brush(random_n(0,222,n=3))
    # draw
    img.line(random_n(1,width-1,n=4), pen)
    img.arc(random_n(1,width-1,n=4), 0, 113, pen)
    img.ellipse(random_n(1,width-1,n=4), pen)
    img.polygon(random_n(1,width-1,n=12), pen, brush)
    # update
    img.flush()
    tkimg = agg2tkimg(img)
    label["image"] = label.img = tkimg

def loop_graphics():
    random_graphic(1000,600)
    print "new graphic drawn"
    window.after(10, loop_graphics)

window.after(1, loop_graphics)

window.mainloop()


