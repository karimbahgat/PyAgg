import pyagg
import random
import math



# plot text width and height as increments of font size
##import PIL, PIL.ImageFont
##ws = []
##hs = []
##ow,oh = 0,0
##for i in range(1,40):
##    font = PIL.ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size=i) #, opacity=options["textopacity"])
##    w,h = font.getsize("Hello")
##    ws.append(w)
##    hs.append(h)
##    print w,h,"-", w-ow, h-oh
##    ow,oh = w,h
##    
##gr = pyagg.graph.LineGraph()
##gr.add_category(name="widths", xvalues=range(1,40), yvalues=ws)
##gr.add_category(name="heights", xvalues=range(1,40), yvalues=hs)
##gr.draw(500,500,"white").view()



def test_text():
    canvas = pyagg.Canvas("210mm","297mm", background=(222,222,222), ppi=97)
    #canvas.percent_space()
    canvas.custom_space(0,0,140,100)
    #canvas.flip(True, True)
    #canvas.rotate(30)
    canvas.draw_grid(33,33,10,10)
    
    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize="2cm")

    canvas.draw_text("Once upon a time", (50,20), fillcolor="white", textsize=32)
    canvas.draw_text("Someplace Near Boulder", (50,30), textsize=12)
    canvas.draw_text("There was a reflection", (50,40), textsize=12, anchor="e")
    canvas.draw_text("There was a reflection", (50,40), textsize=12, anchor="w")

    canvas.draw_text("Testing text wrap testing textwrap testing. Testing textwrap.",
                     bbox=(40,60,60,80), textsize=17,
                     fillcolor="white", outlinecolor="black",
                     justify="center")
    
    for d in ("nw","n","ne","e","se","s","sw","w"):
        canvas.draw_text(d, (50,90), textsize=32,
                         anchor=d)
    canvas.default_unit = "cm"
    canvas.draw_circle((50,50),fillsize="1", fillcolor=(0,222,0))
    canvas.draw_box((50,50),fillsize="1", fillcolor=(0,0,0, 111))
    canvas.draw_triangle((50,50),fillsize="1", fillcolor=(0,0,0, 111))
    canvas.default_unit = "in"
    canvas.draw_circle((50,50),fillsize="1", fillcolor=(0,222,0,111))
    canvas.draw_box((50,50),fillsize="1", fillcolor=(0,0,0, 111))
    canvas.draw_triangle((50,50),fillsize="1", fillcolor=(0,0,0, 111))

    #miniimg = pyagg.load("C:/Users/kimo/Desktop/ble.png")
    #canvas.paste(miniimg, bbox=[10,10,130,40], lock_ratio=True, fit=True)
    
    #canvas.zoom_bbox(11,0,112,40, lock_ratio=True)
    #canvas.zoom_bbox(40,10,80,140, lock_ratio=True, fit=True)
    #canvas.zoom_factor(2)
    #print canvas.coordspace_units
    #canvas.zoom_units(1)
    #print canvas.coordspace_units
    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize="2cm")

    # draw corner coords
    xy = canvas.pixel2coord(0,0)
    canvas.draw_text(str(xy), xy, textsize=33, anchor="nw")
    xy = canvas.pixel2coord(canvas.width,canvas.height)
    canvas.draw_text(str(xy), xy, textsize=33, anchor="se")

    #canvas.rotate(45)
    #canvas.crop(14,54,55,81)
##    canvas.resize(1100,300,lock_ratio=True)
##    print canvas.coordspace_bbox
##    canvas.draw_line([10,10, 50,90, 90,10],
##                     smooth=True,
##                     fillcolor=(222,0,0),
##                     fillsize="2cm")
    #canvas.transparency(111)
    #canvas.transparent_color((222,0,0), tolerance=0.1)
    #canvas.replace_color((0,0,0), (0,222,211), tolerance=0.2)
    #canvas.blur(1)
    #canvas.equalize()
    #canvas.contrast(2)
    canvas.color_tint((222,0,0))
    
    canvas.save("C:/Users/kimo/Desktop/ble.png")#view()




if __name__ == "__main__":
    
    test_text()


    


