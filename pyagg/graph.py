"""
Contains classes for different types of graphs, intended for easy use.
Still a work in progress, and misses several features. 
"""

import itertools
import operator
import math
import random


from .canvas import Canvas
from . import units



# Globals

CANVASOPTIONS = {"width":1000,"height":500,
                 "background":(88,88,88),
                 "ppi":300}




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
        if _xmax > xmax: xmax = _xmax
        if _ymin < ymin: ymin = _ymin
        if _ymax > ymax: ymax = _ymax
    return xmin,ymin,xmax,ymax

import collections

def nested_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = nested_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


# 1 var

class Histogram:
    # create a barchart with 0 bargap
    def __init__(self, values, bins, **kwargs):
        # pool values into n bins and sum them
        self.options = kwargs
        self.bins = []
        minval, maxval = min(values), max(values)
        valuerange = maxval - minval
        binwidth = valuerange / float(bins)
        values = sorted(values)
        # begin
        count = 0
        curval = minval
        nextval = curval + binwidth
        for val in values:
            if val < nextval:
                count += 1
            else:
                self.bins.append(((curval,nextval), count))
                count = 0
                curval = nextval
                nextval = curval + binwidth
                # skip bins until find match
                while val >= nextval:
                    count = 0
                    self.bins.append(((curval,nextval), count))
                    curval = nextval
                    nextval = curval + binwidth
                # found next belonging bin
                count += 1 # count towards next bin
        # add the last bin
        self.bins.append(((curval,nextval), count))
        
    def draw(self, axisoptions={}, **kwargs):
        # use these aggregated bin values as bars arg, and the bin range text as barlabels
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)

        ranges,values = zip(*self.bins)
        xmin = ranges[0][0]
        xmax = ranges[-1][1]
        ymin,ymax = min(values),max(values)
        canvas.custom_space(xmin, ymax, xmax, 0)
        
        for (minval,maxval),value in self.bins:
            canvas.draw_box(bbox=[minval,value,maxval,0], **self.options)
            
##        graph = BarChart()
##        graph.bargap = 0
##        ranges, values = zip(*self.bins)
##        labels = ["%s - %s"%(format(_min,labelformat),format(_max,labelformat)) for _min,_max in ranges]
##        graph.add_category("",
##                           barlabels=labels,
##                           barvalues=values,
##                           **self.options)
            
        # add gradual ticks
        canvas.zoom_out(1.2)
        defaultaxisoptions = {"x":{"tickinterval":maxval-minval,
                                   "intercept":0,
                                   "ticklabeloptions":{"rotate":30, "anchor":"ne"}},
                              "y":{"intercept":xmin}}
        nested_update(defaultaxisoptions, axisoptions)
        canvas.draw_axis("x", xmin, xmax, **defaultaxisoptions["x"])
        if xmin < 0 and xmax > 0:
            zeroaxisoptions = defaultaxisoptions["y"].copy()
            zeroaxisoptions.update({"intercept":0, "noticklabels":True})
            canvas.draw_axis("y", 0, ymax, **zeroaxisoptions)
        canvas.draw_axis("y", 0, ymax, **defaultaxisoptions["y"])
        return canvas

class BarChart:
    
    def __init__(self):
        self.categories = dict()
        self.bargap = 0.2
        self.barwidth = 1
        self.categorygap = 0
        self.padding = 0.2
        
    def add_category(self, name, baritems=[], barlabels=[], barvalues=[], **kwargs):
        if baritems:
            if len(baritems[0]) != 2:
                raise Exception("all baritems must have length 2")
            barlabels,barvalues = zip(*baritems)
        elif barlabels and barvalues:
            if len(barlabels) != len(barvalues):
                raise Exception("bar labels and values series must be same length")
        else:
            raise Exception("you must choose either baritems or both barlabels and barvalues")
        if "fillcolor" not in kwargs:
            kwargs["fillcolor"] = (random.randrange(256),random.randrange(256),random.randrange(256))
        self.categories[name] = {"pos":len(self.categories), "barlabels":barlabels, "bars":barvalues, "options":kwargs}

    def draw(self, axisoptions={}, **kwargs):
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)
        ymin = min((min(dict["bars"]) for category,dict in self.categories.items()))
        ymin = min(0, ymin)     # to ensure snapping to 0 if ymin is not negative
        ymax = max((max(dict["bars"]) for category,dict in self.categories.items()))
        _barcount = sum((len(dict["bars"]) for category,dict in self.categories.items()))
        _clustercount = len(set((dict["bars"] for category,dict in self.categories.items())))
        xmin = 0
        xmax = self.bargap + ( (self.barwidth + self.categorygap) * _barcount) + self.bargap * _clustercount - self.categorygap * _clustercount
        
        # set coordinate bbox
        canvas.custom_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1-self.padding)

        # default axis options
        defaultaxisoptions = {"x":{"minval":self.bargap+self.barwidth/2.0,
                                   "maxval":xmax-self.bargap-self.barwidth/2.0,
                                   "tickinterval":1+self.bargap,
                                   "intercept":ymin,
                                   "noticks":True,
                                   "noticklabels":False,
                                   "ticklabeloptions":{"rotate":30, "anchor":"ne"}},
                              "y":{"minval":ymin,
                                   "maxval":ymax,
                                   "ticknum":5,
                                   "intercept":xmin,
                                   "ticklabeloptions":{"anchor":"e"},
                                   }
                              }
        nested_update(defaultaxisoptions, axisoptions)
               
        # draw categories
        textlabeloptions = defaultaxisoptions["x"]["ticklabeloptions"]
        baroffset = 0
        for category,cdict in sorted(self.categories.items(), key=lambda x: x[1]["pos"]):
            curx = self.bargap + baroffset

            # valuelabel options
            valuelabeloptions = cdict["options"].get("valuelabeloptions",{})
            valuelabelformat = cdict["options"].get("valuelabelformat")
            novaluelabels = cdict["options"].get("novaluelabels", True)
            if not valuelabelformat:
                valrange = ymax - ymin
                if valrange < 1:
                    valuelabelformat = ".6f"
                elif valrange < 10:
                    valuelabelformat = ".1f"
                else:
                    valuelabelformat = ".0f"
            if isinstance(valuelabelformat, str):
                _frmt = valuelabelformat
                valuelabelformat = lambda s: format(s, _frmt)
            
            # loop
            for barlabel,barvalue in itertools.izip(cdict["barlabels"], cdict["bars"]):
                flat = [curx,0, curx+self.barwidth,0, curx+self.barwidth,barvalue, curx,barvalue]
                canvas.draw_polygon(flat, **cdict["options"])
                if not novaluelabels:
                    barvaluelabel = valuelabelformat(barvalue)
                    canvas.draw_text(barvaluelabel, xy=(curx+self.barwidth/2.0,barvalue), **valuelabeloptions)
                curx += self.barwidth * len(self.categories) + self.categorygap * (len(self.categories)-1) + self.bargap
            baroffset += self.barwidth + self.categorygap

        # draw category labels
        xincr = self.barwidth * len(self.categories) + self.categorygap * (len(self.categories)-1) + self.bargap
        curx = self.bargap + xincr / 2.0 - self.barwidth
        cdict = self.categories.values()[0]
        for barlabel in cdict["barlabels"]:
            if not defaultaxisoptions["x"]["noticklabels"]:
                canvas.draw_text(barlabel, xy=(curx,0), **textlabeloptions)
            curx += xincr

        # draw axes
        nolabelaxisoptions = dict()
        nested_update(nolabelaxisoptions, defaultaxisoptions)
        nolabelaxisoptions["x"]["noticklabels"] = True  # override no x labels, since those are handled manually when drawing each bar
        nolabelaxisoptions["x"]["minval"] = xmin
        nolabelaxisoptions["x"]["maxval"] = xmax
        if ymin < 0 and ymax > 0:
            # just the line if both positive and negative values
            canvas.draw_axis("x", minval=self.bargap,
                             maxval=xmax,
                             noticks=True,
                             noticklabels=True)
        canvas.draw_axis("y", **nolabelaxisoptions["y"])
        canvas.draw_axis("x", **nolabelaxisoptions["x"])
            
        # return the drawed canvas
        return canvas

class PieChart:
    # similar to barchart, but each pie size decided by value's %share of total
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, value, **kwargs):
        # only one possible category
        self.categories[name] = {"value":value, "options":kwargs}

    def draw(self, orderby="value", **kwargs):
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)
        
        canvas.custom_space(-50, 50, 50, -50, lock_ratio=True)
        total = sum(cat["value"] for cat in self.categories.values())
        
        if orderby == "value": categories = list(sorted(self.categories.items(), key=lambda x: x[1]["value"]))
        elif orderby == "name": categories = list(sorted(self.categories.items(), key=lambda x: x[1]["name"]))
        else: categories = list(self.categories.items())

        # first pies
        curangle = 90
        for name,category in categories:
            value = category["value"]
            ratio = value / float(total)
            degrees = 360 * ratio
            canvas.draw_pie((0,0), curangle, curangle + degrees,
                            **category["options"])
            curangle += degrees

        # text label offsets
        x,y = canvas.coord2pixel(0,0)
        offset = units.parse_dist(category["options"]["fillsize"],
                                 ppi=canvas.ppi,
                                 default_unit=canvas.default_unit,
                                 canvassize=[canvas.width,canvas.height],
                                 coordsize=[canvas.coordspace_width,canvas.coordspace_height])
        offset *= 0.75

        # then text labels
        canvas.pixel_space()
        curangle = 90
        for name, category in categories:
            value = category["value"]
            ratio = value / float(total)
            degrees = 360 * ratio
            midangle = curangle + (degrees / 2.0)
            midrad = math.radians(midangle)
            tx,ty = x + offset * math.cos(midrad), y - offset * math.sin(midrad)
            canvas.draw_text(name, (tx,ty), **category["options"])
            curangle += degrees
        return canvas
            
            



# 2 vars

class LineGraph:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xyvalues=[], xvalues=[], yvalues=[], **kwargs):
        if xyvalues:
            if len(xyvalues[0]) != 2:
                raise Exception("all xy series items must have length 2")
            xvalues,yvalues = zip(*xyvalues)
        elif xvalues and yvalues:
            if len(xvalues) != len(yvalues):
                raise Exception("x and y series must be same length")
        else:
            raise Exception("you must choose either xy values or both xvalues and yvalues")
        # default options
        kwargs = kwargs.copy()
        if not "placelabel" in kwargs:
            kwargs["placelabel"] = "lineend"
        labeloptions = {"fillcolor":(255,255,255,222)}
        if "labeloptions" in kwargs:
            labeloptions.update(kwargs.pop("labeloptions"))
        self.categories[name] = {"x":xvalues, "y":yvalues,
                                 "options":kwargs,
                                 "labeloptions":labeloptions}

    def draw(self, **kwargs):
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)

        # set coordinate bbox
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        canvas.custom_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)
        
        # draw axes
        if ymin < 0 and ymax > 0:
            canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=ymin,
                         ticklabeloptions={"anchor":"n"})
        if xmin < 0 and xmax > 0:
            canvas.draw_axis("y", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("y", ymin, ymax, tickinterval=(ymax-ymin)/5.0, intercept=xmin,
                         ticklabeloptions={"anchor":"e"})
        
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"])
            canvas.draw_line(valuepairs, **dict["options"])
            # test add label next to last line point
            if dict["options"]["placelabel"] == "lineend":
                canvas.draw_text(category, xy=valuepairs[-1],
                                 **dict["labeloptions"])
        #canvas.draw_text((xmax,ymin), unicode(xmax), textcolor=(222,222,222))
        #canvas.draw_text((xmin,ymax), unicode(ymax), textcolor=(222,222,222))
        #canvas.draw_text((xmin+5,ymin), unicode(xmin), textcolor=(222,222,222))
        #canvas.draw_text((xmin,ymin+5), unicode(ymin), textcolor=(222,222,222))
        
        # return the drawed canvas
        return canvas

class ScatterPlot:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xyvalues=[], xvalues=[], yvalues=[], **kwargs):
        if xyvalues:
            if len(xyvalues[0]) != 2:
                raise Exception("all xy series items must have length 2")
            xvalues,yvalues = zip(*xyvalues)
        elif xvalues and yvalues:
            if len(xvalues) != len(yvalues):
                raise Exception("x and y series must be same length")
        else:
            raise Exception("you must choose either xy values or both xvalues and yvalues")
        self.categories[name] = {"x":xvalues, "y":yvalues, "options":kwargs}

    def draw(self, **kwargs):
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)

        # set coordinate bbox
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        canvas.custom_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)

        # draw axes
        if ymin < 0 and ymax > 0:
            canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=ymin,
                         ticklabeloptions={"anchor":"n"})
        if xmin < 0 and xmax > 0:
            canvas.draw_axis("y", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("y", ymin, ymax, tickinterval=(ymax-ymin)/5.0, intercept=xmin,
                         ticklabeloptions={"anchor":"e"})
        
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"])
            for xy in valuepairs:
                canvas.draw_circle(xy, **dict["options"])
                
        # return the drawed canvas
        return canvas



# 3 vars

class BubblePlot:
    
    def __init__(self):
        self.categories = dict()
        
    def add_category(self, name, xyvalues=[], xvalues=[], yvalues=[], zvalues=[], **kwargs):
        if xyvalues:
            if len(xyvalues[0]) != 2:
                raise Exception("all xy series items must have length 2")
            xvalues,yvalues = zip(*xyvalues)
        elif xvalues and yvalues:
            if len(xvalues) != len(yvalues):
                raise Exception("x and y series must be same length")
        else:
            raise Exception("you must choose either xy values or both xvalues and yvalues")
        if not zvalues:
            raise Exception("you must provide z-values")
        # ...
        self.categories[name] = {"x":xvalues, "y":yvalues, "z":zvalues, "options":kwargs}

    def draw(self, **kwargs):
        canvasoptions = CANVASOPTIONS.copy()
        canvasoptions.update(kwargs)
        canvas = Canvas(**canvasoptions)

        # set coordinate bbox
        xmin,ymin,xmax,ymax = bbox_categories(self.categories)
        canvas.custom_space(xmin,ymax,xmax,ymin)
        canvas.zoom_factor(-1.2)

        # draw axes
        if ymin < 0 and ymax > 0:
            canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("x", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=ymin,
                         ticklabeloptions={"anchor":"n"})
        if xmin < 0 and xmax > 0:
            canvas.draw_axis("y", xmin, xmax, tickinterval=(xmax-xmin)/5.0, intercept=0,
                             noticklabels=True)
        canvas.draw_axis("y", ymin, ymax, tickinterval=(ymax-ymin)/5.0, intercept=xmin,
                         ticklabeloptions={"anchor":"e"})
        
        # draw categories
        for category,dict in self.categories.items():
            valuepairs = zip(dict["x"], dict["y"], dict["z"])
            for xyz in valuepairs:
                x,y,z = xyz
                # convert z value to some minmax symbolsize
                # ...
                # draw the bubble
                canvas.draw_circle((x,y), fillsize=z, **dict["options"])
                
        # return the drawed canvas
        return canvas






