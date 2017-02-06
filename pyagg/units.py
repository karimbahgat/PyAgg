"""
Parses distances formatted as strings with a unit suffix, converting them
to pixels.
Mostly used internally. 
"""

def px_to_px(diststring):
    diststring = diststring.replace("px", "")
    pixels = eval(diststring)
    return pixels

def pt_to_px(diststring, ppi):
    diststring = diststring.replace("pt", "")
    point = eval(diststring)
    inches = point / 72.0 # a type point is one 72th of an inch
    pixels = inches * ppi
    return pixels

def in_to_px(diststring, ppi):
    diststring = diststring.replace("in", "")
    inches = eval(diststring)
    pixels = inches * ppi
    return pixels

def mm_to_px(diststring, ppi):
    diststring = diststring.replace("mm", "")
    mm = eval(diststring)
    inches = mm * 0.0393700787
    pixels = inches * ppi
    return pixels

def cm_to_px(diststring, ppi):
    diststring = diststring.replace("cm", "")
    cm = eval(diststring)
    inches = cm * 0.393700787
    pixels = inches * ppi
    return pixels

def percwidth_to_px(diststring, width):
    diststring = diststring.replace("%w", "")
    perc = float(diststring)
    pixels = width / 100.0 * perc
    return pixels

def percheight_to_px(diststring, height):
    diststring = diststring.replace("%h", "")
    perc = float(diststring)
    pixels = height / 100.0 * perc
    return pixels

def percmin_to_px(diststring, width, height):
    diststring = diststring.replace("%min", "")
    perc = float(diststring)
    min_ = min([width,height])
    pixels = min_ / 100.0 * perc
    return pixels

def percmax_to_px(diststring, width, height):
    diststring = diststring.replace("%max", "")
    perc = float(diststring)
    max_ = max([width,height])
    pixels = max_ / 100.0 * perc
    return pixels

def x_to_px(diststring, width, coordwidth):
    diststring = diststring.replace("x", "")
    x = eval(diststring)
    relx = x / float(coordwidth)
    pixels = width * relx
    return pixels

def y_to_px(diststring, height, coordheight):
    diststring = diststring.replace("y", "")
    y = eval(diststring)
    rely = y / float(coordheight)
    pixels = height * rely
    return pixels

def px_to_x(columndist, width, coordwidth):
    relcol = columndist / float(width)
    x = coordwidth * relcol
    return x

def px_to_y(rowdist, height, coordheight):
    relrow = rowdist / float(height)
    y = coordheight * relrow
    return y

##def x_to_px(diststring, x2px_func):
##    diststring = diststring.replace("x", "")
##    xdist = eval(diststring)
##    pixels = x2px_func(xdist)
##    return pixels
##
##def y_to_px(diststring, y2px_func):
##    diststring = diststring.replace("y", "")
##    ydist = eval(diststring)
##    pixels = y2px_func(ydist)
##    return pixels

def parse_diststring(diststring, ppi=None, canvassize=None, coordsize=None):
    """
    Assuming distances are formatted as strings with a unit suffix, converts them
    to pixels. 
    """
    unit = diststring.lstrip('0123456789.-')
    
    if unit == "px":
        return px_to_px(diststring)

    elif unit == "pt":
        return pt_to_px(diststring, ppi)

    elif unit == "in":
        return in_to_px(diststring, ppi)

    elif unit == "mm":
        return mm_to_px(diststring, ppi)

    elif unit == "cm":
        return cm_to_px(diststring, ppi)

    elif unit == "x":
        width, height = canvassize
        coordwidth, coordheight = coordsize
        return x_to_px(diststring, width, coordwidth)

    elif unit == "y":
        width, height = canvassize
        coordwidth, coordheight = coordsize
        return y_to_px(diststring, height, coordheight)

    elif "%" in unit:
        # Somehow get size of canvas object and calculate percent of that
        # or should it be compared to parent object...?
        # But there are no nested hiearchies in PyAgg, only a single canvas
        # Indeed, preferred way is to create subcanvases and paste them into the main one
        # At least should have "%w" and "%h", or automatic determine if just "%"
        width, height = canvassize
        if unit == "%w":
            return percwidth_to_px(diststring, width)
        elif unit == "%h":
            return percheight_to_px(diststring, height)
        elif unit == "%min":
            return percmin_to_px(diststring, width, height)
        elif unit == "%max":
            return percmax_to_px(diststring, width, height)
        else:
            raise Exception("Percent distances must by %w, %h, %min, or %max, and should be determined relative x or y axis in advance")

    else:
        raise Exception("Unable to parse distance string: %s" % diststring)

def parse_dist(dist, ppi=None, default_unit=None, canvassize=None, coordsize=None):
    """
    Includes preprocessing step that makes sure the distance is formatted as a
    unit string before it converts it to pixels with the parse_diststring() method.
    Can be either nr in text, or pure nr. 
    """
    
    try:
        # if no unit was specified, use default unit of the canvas
        # ...which should be supplied from the canvas.default_unit attribute
        # ...as set by canvas.set_default_unit("cm")
        float(dist)
        diststring = str(dist)
        diststring += default_unit

    except:
        diststring = dist

    pixels = parse_diststring(diststring, ppi, canvassize, coordsize)
    return pixels

def split_unit(value_or_str):
    if isinstance(value_or_str, basestring):
        # from right to left, find index of first digit
        for i,val in reversed(enumerate(value_or_str)):
            if val.isdigit():
                break
        # return everything from left up to that point
        return eval(value_or_str[:i]), value_or_str[i:]
    else:
        return value_or_str, None







