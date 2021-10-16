
import pyagg as pa

c = pa.Canvas(500,500)
c.percent_space()

c.draw_text("""Long paragraph
broken up
into lines
and aligned to the left""", (0,0), anchor="nw", justify="left")

c.draw_text("""Long paragraph
broken up
into lines
aligned to the center
and rotated""", (50,50), anchor="center", justify="center", rotate=13)

c.draw_text("""Long paragraph
broken up
into lines
and aligned to the right""", (100,100), anchor="se", justify="right")

c.draw_text("This is an interesing textbox that should be autowrapped", bbox=[60,60,100,70])

c.draw_text("25%", (100,0), textsize="25%h", anchor="ne")

##for size in range(1,50,5):
##    c.draw_text("%s%%"%size, (500,500/100*size), textsize="%s%%w"%size, anchor="e")

c.view()
