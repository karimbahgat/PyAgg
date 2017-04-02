
import pyagg as pa

c = pa.Canvas(500,500)

c.draw_text("""Long paragraph
broken up
into lines
and aligned to the left""", (0,0), anchor="nw", justify="left")

c.draw_text("""Long paragraph
broken up
into lines
and aligned to the center""", (0,200), anchor="nw", justify="center", rotate=13)

c.draw_text("""Long paragraph
broken up
into lines
and aligned to the right""", (0,400), anchor="nw", justify="right")

c.draw_text("Rotated", (250,250), anchor="center", rotate=-45)

c.draw_text("This is an interesing textbox that should be autowrapped", bbox=[100,100,200,200])

c.view()
