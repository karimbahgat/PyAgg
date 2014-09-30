import pyagg
import random

##canvas = pyagg.Canvas(1000,500)
##canvas.percent_space()
##canvas.draw_line([10,10, 50,90, 90,10],
##                 smooth=True,
##                 fillcolor=None,
##                 outlinecolor=(222,0,0),
##                 outlinewidth=9)
##canvas.view()


graph = pyagg.graph.LineGraph()
graph.add_category("random nrs",
                   range(100),
                   [random.randrange(40) for _ in xrange(100)] )
graph.draw()
