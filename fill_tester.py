
import pyagg as pa

c = pa.Canvas(500,500)
c.custom_space(-200,-200,200,200)

def linepattern(w,h):
    c = pa.Canvas(w,h,mode="RGB",background="black")
    incr = w*2//5
    for x in range(0,w*2,incr):
        x += incr//2
        c.draw_line([(0,x),(x,0)], fillsize=10, fillcolor="white")
    return c
def imgfill(w,h):
    return pa.load(r"C:\Users\kimo\Downloads\BM_Maps_100204710.jpg").resize(w,h)

c.draw_polygon([(10,10),(30,20),(90,18),(80,90),(20,80)],
               outlinewidth=0.5,
               fillcolor=imgfill,
               fillmask=linepattern)

c.view()
