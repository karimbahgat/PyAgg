# pyagg/units.py

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
    diststring = diststring.replace("%x", "")
    perc = float(diststring)
    pixels = width / 100.0 * perc
    return pixels

def percheight_to_px(diststring, height):
    diststring = diststring.replace("%y", "")
    perc = float(diststring)
    pixels = height / 100.0 * perc
    return pixels

def parse_diststring(diststring, ppi=None, canvassize=None):
    if "px" in diststring:
        return px_to_px(diststring)

    elif "pt" in diststring:
        return pt_to_px(diststring, ppi)

    elif "in" in diststring:
        return in_to_px(diststring, ppi)

    elif "mm" in diststring:
        return mm_to_px(diststring, ppi)

    elif "cm" in diststring:
        return cm_to_px(diststring, ppi)

    elif "%" in diststring:
        # Somehow get size of canvas object and calculate percent of that
        # or should it be compared to parent object...?
        # But there are no nested hiearchies in PyAgg, only a single canvas
        # Indeed, preferred way is to create subcanvases and paste them into the main one
        # At least should have "%x" and "%y", or automatic determine if just "%"
        width, height = canvassize
        if diststring.endswith("%x"):
            return percwidth_to_px(diststring, width)
        elif diststring.endswith("%y"):
            return percheight_to_px(diststring, height)
        else:
            raise Exception("Percent distances must by %x or %y and should be determined relative x or y axis in advance")

    else:
        raise Exception("Unable to parse distance string: %s" % diststring)

def parse_dist(dist, ppi=None, default_unit=None, canvassize=None):
    "can be either nr in text, or pure nr"
    
    try:
        # if no unit was specified, use default unit of the canvas
        # ...as set by canvas.set_default_unit("cm")
        float(dist)
        diststring = str(dist)
        diststring += default_unit

    except:
        diststring = dist

    pixels = parse_diststring(diststring, ppi, canvassize)
    return pixels







