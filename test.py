import pyagg
import random

def test_smoothline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=None,
                     outlinecolor=(222,0,0),
                     outlinewidth=9)
    canvas.view()

def test_barchart():
    barlabels = range(10)
    bars = [random.randrange(-20,40) for _ in barlabels]
    graph = pyagg.graph.BarChart()
    graph.add_category("random bars",
                       barlabels=barlabels,
                       bars=bars,
                        fillcolor=(222,222,0),
                        outlinecolor=(0,0,222))
##    bars2 = [random.randrange(-20,40) for _ in barlabels]
##    graph.add_category("random bars2",
##                       barlabels=barlabels,
##                       bars=bars2,
##                        fillcolor=(222,0,0),
##                        outlinecolor=(0,0,222))
    graph.draw(1000, 500).view()

def test_linegraph():
    xs = range(100)
    ys = [random.randrange(40) for _ in xs]
    graph = pyagg.graph.LineGraph()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                       smooth=True,
                        fillcolor=None,
                        outlinecolor=(222,222,0),
                        outlinewidth=3)
    graph.draw(1000, 500).view()

def test_scatterplot():
    xs = range(1000)
    ys = [random.randrange(400) for _ in xs]
    graph = pyagg.graph.ScatterPlot()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                       fillsize=7,
                        fillcolor=(222,222,0),
                        outlinecolor=(0,0,222),
                        outlinewidth=0.5)
    graph.draw(1000, 500).view()

def test_bubbleplot():
    xs = range(1000)
    ys = [random.randrange(400) for _ in xs]
    zs = [random.randrange(1,15) for _ in xs]
    graph = pyagg.graph.BubblePlot()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                       zvalues=zs,
                        fillcolor=(222,222,0),
                        outlinecolor=(0,0,222),
                        outlinewidth=0.5)
    graph.draw(1000, 500).view()




if __name__ == "__main__":
    
    test_linegraph()


    


