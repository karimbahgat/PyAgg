import pyagg
import random
import math

def test_text():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    
    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize=1)
    
    canvas.draw_text((50,20),"Once upon a time", textsize=32)
    canvas.draw_text((50,30),"Someplace Near Boulder", textsize=12)
    canvas.draw_text((50,40),"There was a reflection", textsize=12, textanchor="e")
    canvas.draw_text((50,40),"There was a reflection", textsize=12, textanchor="w")

    
    for d in ("nw","n","ne","e","se","s","sw","w"):
        canvas.draw_text((50,50), d, textsize=32,
                         textanchor=d)
    canvas.draw_circle((50,50),fillsize=0.5, fillcolor=(0,222,0))
    canvas.view()




if __name__ == "__main__":
    
    test_text()


    


