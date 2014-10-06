from .canvas import Canvas



# Helpers

def bbox_categories(categories):
    category,dict = categories.items()[0]
    xmin,xmax = min(dict["x"]),max(dict["x"])
    ymin,ymax = min(dict["y"]),max(dict["y"])
    # get bbox
    for category,dict in categories.items():
        _xmin,_xmax = min(dict["x"]),max(dict["x"])
        _ymin,_ymax = min(dict["y"]),max(dict["y"])
        if _xmin < xmin: xmin = _xmin
        if _xmax < xmax: xmax = _xmax
        if _ymin < ymin: ymin = _ymin
        if _ymax < ymax: ymax = _ymax
    return xmin,ymin,xmax,ymax



# 1 var

class Histogram:
    # create a barchart with 0 bargap
    # pool values into n bins and sum them
    # use these aggregated bin values as bars arg, and the bin range text as barlabels
    pass

class BarChart:
    # NOT FINISHED...
    
    def __init__(self):
        self.categories = dict()
        self.bargap = 3
        self.barwidth = 30
        
    def add_category(self, name, barlabels, bars, **kwargs):
        self.categories[name] = {"bars":bars, "barlabels":barlabels, "options":kwargs}

    def draw(self, width, height, background=(0,0,0)):
        canvas = Canvas(width, height, background)
        ymin = min((min(dict["bars"]) for category,dict in self.categories.items()))
        ymax = max((max(dict["bars"]) for category,dict in self.categories.items()))
        _barcount = sum((len(dict["bars"]) for category,dict in self.categories.items()))
        xmin = 0
        xmax = self.bargap + ( (self.barwidth + self.bargap) * _barcount)
        # set coordinate bbox
        canvas.coordinate_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        # draw categories
        baroffset = 0
        for category,dict in self.categories.items():
            curx = self.bargap + baroffset
            for barvalue in dict["bars"]:
                flat = [curx,0, curx,barvalue]
                # convert barwidth coords to barwidth pixels bc drawer outlinewidht is interpreted as pixel width
                # ...
                canvas.draw_line(flat, outlinewidth=self.barwidth, **dict["options"])
                curx += self.barwidth + self.bargap
            baroffset += self.barwidth
        # return the drawed canvas
        return canvas

class PieChart:
    # similar to barchart, but each pie size decided by value's %share of total
    pass



# 2 vars

class LineGraph:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xvalues, yvalues, **kwargs):
        if len(xvalues) != len(yvalues):
            raise Exception("x and y series must be same length")
        self.categories[name] = {"x":xvalues, "y":yvalues, "options":kwargs}

    def draw(self, width, height, background=(0,0,0)):
        canvas = Canvas(width, height, background)
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        # set coordinate bbox
        canvas.coordinate_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"])
            flat = [xory for xy in valuepairs for xory in xy]
            canvas.draw_line(flat, **dict["options"])
        # return the drawed canvas
        return canvas

class ScatterPlot:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xvalues, yvalues, **kwargs):
        if len(xvalues) != len(yvalues):
            raise Exception("x and y series must be same length")
        self.categories[name] = {"x":xvalues, "y":yvalues, "options":kwargs}

    def draw(self, width, height, background=(0,0,0)):
        canvas = Canvas(width, height, background)
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        # set coordinate bbox
        canvas.coordinate_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"])
            for xy in valuepairs:
                canvas.draw_point(xy, symbol="circle", **dict["options"])
        # return the drawed canvas
        return canvas



# 3 vars

class BubblePlot:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xvalues, yvalues, zvalues, **kwargs):
        if len(xvalues) != len(yvalues):
            raise Exception("x and y series must be same length")
        self.categories[name] = {"x":xvalues, "y":yvalues, "z":zvalues, "options":kwargs}

    def draw(self, width, height, background=(0,0,0)):
        canvas = Canvas(width, height, background)
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        # set coordinate bbox
        canvas.coordinate_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"], dict["z"])
            for xyz in valuepairs:
                x,y,z = xyz
                # convert z value to some minmax symbolsize
                # ...
                # draw the bubble
                canvas.draw_point((x,y), symbol="circle", fillsize=z, **dict["options"])
        # return the drawed canvas
        return canvas






