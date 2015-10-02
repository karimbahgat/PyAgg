import pyagg
import random
import math

def test_smoothline():
    canvas = pyagg.Canvas(1000,500)
    canvas.percent_space()
    for x1,x2 in zip(range(-50, 100, 10), range(0, 150, 10)):
        canvas.draw_line([x2,0, x1,100])
    canvas.draw_line([10,10, 50,90, 90,10],
                     smooth=True,
                     fillcolor=(222,0,0),
                     fillsize=2)
    canvas.draw_text("Hello", (50,50), textfont="segoe print bold", textsize=55)
    return canvas

def test_histogram():
    values = [math.sin(i) for i in xrange(10000)]
    graph = pyagg.graph.Histogram(values=values,
                                  bins=10,
                                  fillcolor=(0,88,255),
                                  outlinecolor=(222,222,0),
                                  outlinewidth=2)
    return graph.draw(1000, 500)

def test_barchart():
    barlabels = range(10)
    bars = [random.randrange(-20,40) for _ in barlabels]
    graph = pyagg.graph.BarChart()
    graph.add_category("random bars",
                       barlabels=barlabels,
                       bars=bars,
                        fillcolor=(222,222,0),
                        outlinecolor=(222,0,222),
                       outlinewidth=2)
##    bars2 = [random.randrange(-20,40) for _ in barlabels]
##    graph.add_category("random bars2",
##                       barlabels=barlabels,
##                       bars=bars2,
##                        fillcolor=(222,0,0),
##                        outlinecolor=(0,0,222))
    return graph.draw(1000, 500)

def test_piechart():
    name_values = [(nr,nr) for nr in range(1,15)]
    graph = pyagg.graph.PieChart()
    for name,value in name_values:
        graph.add_category(str(name),
                           value=value,
                            fillcolor=tuple(random.randrange(255) for _ in range(3)),
                            fillsize="40%min",
                           outlinewidth=1,
                           textsize=38,
                           textfont="segoe ui")
    return graph.draw(1500, 1000, background=(22,22,22))

def test_linegraph():
    xs = range(100)
    y = 50
    ys = []
    for _ in xs:
        y += random.randrange(-10,10)
        ys.append(y)
    graph = pyagg.graph.LineGraph()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                        fillcolor=(222,222,0),
                        outlinecolor=(0,0,222),
                       fillsize=1.5)
    xs = range(100)
    y = 50
    ys = []
    for _ in xs:
        y += random.randrange(-10,10)
        ys.append(y)
    graph.add_category("random nrs2",
                       xvalues=xs,
                       yvalues=ys,
                        fillcolor=(0,222,0),
                        outlinecolor=(0,0,222),
                       fillsize=1.5)
    return graph.draw(1000, 500)

def test_scatterplot():
    xs = range(1000)
    ys = [random.randrange(400) for _ in xs]
    graph = pyagg.graph.ScatterPlot()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                       fillsize=0.8,
                        fillcolor=(222,222,0),
                        outlinecolor=(222,0,222),
                       outlinewidth=0.4)
    xs = range(1000)
    ys = [random.randrange(200) for _ in xs]
    graph.add_category("random nrs2",
                       xvalues=xs,
                       yvalues=ys,
                       fillsize=0.8,
                        fillcolor=(0,222,0),
                        outlinecolor=(222,111,0),
                       outlinewidth=0.4)
    return graph.draw(1000, 500)

def test_bubbleplot():
    xs = range(1000)
    ys = [random.randrange(400) for _ in xs]
    zs = [random.uniform(0.5,1.5) for _ in xs]
    graph = pyagg.graph.BubblePlot()
    graph.add_category("random nrs",
                       xvalues=xs,
                       yvalues=ys,
                       zvalues=zs,
                        fillcolor=(222,222,0),
                        outlinecolor=(0,222,222),
                        outlinewidth=0.4)
    return graph.draw(1000, 500)




if __name__ == "__main__":

    
    test_smoothline().save("__private__/test_output/smoothline.png")
    test_histogram().save("__private__/test_output/histogram.png")
    test_barchart().save("__private__/test_output/barchart.png")
    test_piechart().save("__private__/test_output/piechart.png")
    test_linegraph().save("__private__/test_output/linegraph.png")
    test_scatterplot().save("__private__/test_output/scatterplot.png")
    test_bubbleplot().save("__private__/test_output/bubbleplot.png")


    


