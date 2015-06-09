import pyagg

# startup

canvas = pyagg.Canvas("500px", "500px", background="orange")
canvas.percent_space()


# draw pyagg logos background
##from random import randrange
##for _ in range(500):
##    xy = (randrange(0, 100), randrange(0, 100))
##    size = randrange(1, 2+xy[1]/3)
##    canvas.draw_text(xy, "PyAgg", textsize=size, textcolor=(222,222,222,100) )

# draw beer

### bubbles
from random import randrange
for _ in range(500):
    xy = (randrange(30,70), randrange(5,86))
    size = "%i" % randrange(1, 2+xy[1]/10)
    canvas.draw_circle(xy,
                       fillsize=size+"px", fillcolor=None,
                       outlinewidth="1%w", outlinecolor=(222,222,222,100) )
### the middle
canvas.draw_box(bbox=[27, 90, 73, 30],
                fillcolor=(222,222,222,100),
                outlinewidth="5%w", outlinecolor=(122,122,222,100) )
### the handle
canvas.draw_line([(73,70), (90,55), (73,40)],
                 smooth=True,
                 fillcolor=(122,122,222,100),
                 fillsize="5%w")

# draw text
canvas.draw_text((50,15),"Cheers!",
                textanchor="center",
                textfont="Segoe UI",
                textsize=52)
canvas.draw_text((50,50),"To another 5 years of",
                textanchor="center",
                textfont="Segoe UI",
                textsize=32)
canvas.draw_text((50,60),"beautiful AGG drawing!",
                textanchor="center",
                textfont="Segoe UI",
                textsize=32)

#canvas.save("test.png")
canvas.view()
