import pyagg
import random
import math

#linepath = [10,10, 50,90, 90,10]
linepath = [(random.randrange(10,90),random.randrange(10,90)) for _ in range(6)]

def test_normalline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line(linepath,
                     fillcolor=(222,0,0),
                     fillsize=0.1,
                     outlinewidth=0.3)
    return canvas

def test_normalsmoothline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line(linepath,
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize=0.1,
                     outlinewidth=0.3)
    return canvas

def test_flowline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line(linepath,
                     volume=lambda p,x,y: 1*p + 0.1,
                     fillcolor=(222,0,0),
                     outlinecolor="black",
                     outlinewidth=0.3)
    return canvas

def test_flowsmoothline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line(linepath,
                     volume=lambda p,x,y: 1*p + 0.1,
                     smooth=True,
                     fillcolor=(222,0,0),
                     outlinecolor="black",
                     outlinewidth=0.3)
    return canvas

def test_arrow():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line(linepath,
                     volume=lambda p,x,y: 1*p + 0.1,
                     #smooth=True,
                     end="arrow", #lambda line,left,right: [left,right],
                     fillcolor=(222,0,0),
                     outlinecolor="black",
                     outlinewidth=0.3)
    return canvas





if __name__ == "__main__":
    test_normalline().save("__private__/test_output/normalline.png")
    test_normalsmoothline().save("__private__/test_output/normalsmoothline.png")
    test_flowline().save("__private__/test_output/flowline.png")
    test_flowsmoothline().save("__private__/test_output/flowsmoothline.png")
    test_arrow().save("__private__/test_output/arrow.png")


    


