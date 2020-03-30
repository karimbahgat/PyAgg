"""
Contains several helper functions for manipulating bounding boxes.
Mostly used internally.
"""

def conform_aspect(bbox, targetwidth, targetheight, fit=True):
    x1,y1,x2,y2 = bbox
    xs = x1,x2
    ys = y1,y2
    xwidth = newwidth = max(xs) - min(xs)
    yheight = newheight = max(ys) - min(ys)
    
##    targetaspect = targetwidth/float(targetheight)
##    if fit:
##        if newwidth < newheight:
##            # tall bbox
##            newwidth = newheight * targetaspect
##        if newwidth > newheight:
##            # wide bbox
##            newheight = newwidth / float(targetaspect)
##    else:
##        if newwidth > newheight:
##            # wide bbox
##            newwidth = newheight * targetaspect
##        if newwidth < newheight:
##            # tall bbox
##            newheight = newwidth / float(targetaspect)
##
##    return resize_dimensions(bbox, newwidth, newheight)

    xratio = newwidth / float(targetwidth)
    yratio = newheight / float(targetheight)
    if fit:
        ratio = max(xratio,yratio)
    else:
        ratio = min(xratio,yratio)

    newwidth = targetwidth * ratio
    newheight = targetheight * ratio

    return resize_dimensions(bbox, newwidth, newheight)

def resize_ratio(bbox, xratio, yratio):
    # remember old
    x1,y1,x2,y2 = bbox
    x2x = (x1,x2)
    y2y = (y1,y2)
    midx = sum(x2x) / 2.0
    midy = sum(y2y) / 2.0
    halfxwidth = (max(x2x)-min(x2x)) / 2.0
    halfyheight = (max(y2y)-min(y2y)) / 2.0
    # expand or shrink bbox
    if x1 < x2:
        x1 = midx - halfxwidth * xratio
        x2 = midx + halfxwidth * xratio
    else:
        x1 = midx + halfxwidth * xratio
        x2 = midx - halfxwidth * xratio
    if y1 < y2:
        y1 = midy - halfyheight * yratio
        y2 = midy + halfyheight * yratio
    else:
        y1 = midy + halfyheight * yratio
        y2 = midy - halfyheight * yratio
    return [x1,y1,x2,y2]

def resize_dimensions(bbox, newwidth, newheight):
    xleft,ytop,xright,ybottom = bbox
    x2x = (xleft,xright)
    y2y = (ytop,ybottom)
    xwidth = max(x2x) - min(x2x)
    yheight = max(y2y) - min(y2y)
    xratio = newwidth / float(xwidth)
    yratio = newheight / float(yheight)
    return resize_ratio(bbox, xratio, yratio)

def center(bbox, center):
    # remember old
    x1,y1,x2,y2 = bbox
    x2x = (x1,x2)
    y2y = (y1,y2)
    xmin,ymin = min(x2x),min(y2y)
    xmax,ymax = max(x2x),max(y2y)
    halfxwidth = (xmax-xmin) / 2.0
    halfyheight = (ymax-ymin) / 2.0
    centerx, centery = center
    # center it
    xmin = centerx - halfxwidth
    xmax = centerx + halfxwidth
    ymin = centery - halfyheight
    ymax = centery + halfyheight
    # make sure they have same bbox format as when came in
    if x1 < x2: x1,x2 = xmin,xmax
    else: x1,x2 = xmax,xmin
    if y1 < y2: y1,y2 = ymin,ymax
    else: y1,y2 = ymax,ymin
    return [x1,y1,x2,y2]

def offset(bbox, xoffset, yoffset):
    x1,y1,x2,y2 = bbox
    x1,x2 = x1+xoffset,x2+xoffset
    y1,y2 = y1+yoffset,y2+yoffset
    return [x1,y1,x2,y2]

