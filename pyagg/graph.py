from .canvas import Canvas

# 1 var

class Histogram:
    pass

class BarChart:
    pass

class PieChart:
    pass

# 2 vars

class LineGraph:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xtime, yvalues, idvalues=None):
        if len(xtime) != len(yvalues):
            raise Exception("x and y series must be same length")
        self.categories[name] = {"x":xtime, "y":yvalues}
    
    def draw(self):
        canvas = Canvas(1000,500,background=(0,0,0))
        category,dict = self.categories.items()[0]
        xmin,xmax = min(dict["x"]),max(dict["x"])
        ymin,ymax = min(dict["y"]),max(dict["y"])
        # get bbox
        for category,dict in self.categories.items():
            _xmin,_xmax = min(dict["x"]),max(dict["x"])
            _ymin,_ymax = min(dict["y"]),max(dict["y"])
            if _xmin < xmin: xmin = _xmin
            if _xmax < xmax: xmax = _xmax
            if _ymin < ymin: ymin = _ymin
            if _ymax < ymax: ymax = _ymax
        # set coordinate bbox
        canvas.coordinate_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"])
            flat = [xory for xy in valuepairs for xory in xy]
            canvas.draw_line(flat, smooth=True,
                             fillcolor=None,
                             outlinecolor=(0,222,0),
                             outlinewidth=3)
        canvas.view()

class ScatterPlot:
    pass

# 3 vars

class BubblePlot:
    pass






