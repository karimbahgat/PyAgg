"""
Various interpolation algorithms in pure Python.
Karim Bahgat 2015

- Point interpolation of sample points to a grid of unknown values.
- Grid interpolation of values from source to destination grids with different coords.
- Basic image resampling of pixel values to new image dimensions.
"""

from __future__ import division

def pointinterp_idw(points, gridxs, gridys, neighbours=None, sensitivity=None):
    """
    Inverse distance weighing
    """
    #retrieve input options
    if neighbours == None:
        # TODO: not yet implemented
        neighbours = int(len(points)*0.10) #default neighbours is 10 percent of known points
    if sensitivity == None:
        sensitivity = 3 #same as power, ie that high sensitivity means much more effect from far away pointss
    # some precalcs
    senspow = (-sensitivity/2.0)
    #some defs
    def _calcvalue(gridx, gridy, points):
        weighted_values_sum = 0.0
        sum_of_weights = 0.0
        for px,py,pval in points:
            weight = ((gridx-px)**2 + (gridy-py)**2)**senspow
            sum_of_weights += weight
            weighted_values_sum += weight * pval
        return weighted_values_sum / sum_of_weights
    #calculate value
    for gridy in gridys:
        newrow = []
        for gridx in gridxs:
            try:
                # main calc
                newval = _calcvalue(gridx, gridy, points)
            except:
                # gridxy to calculate is exact same as one of the point xy, so just use same value
                newval = next(pval for px,py,pval in points if gridx == px and gridy == py) 
            newrow.append(newval)
        yield newrow
            
def gridinterp_near(oldgrid, oldxs, oldys, newxs, newys):
    """
    Nearest neighbour interpolation...

    NOTE: oldxs and oldys must both be increasing in size for some unknown reason. 
    """

    width = len(oldxs)-1
    height = len(oldys)-1
    oldxmin,oldymin = min(oldxs),min(oldys)
    oldxmax,oldymax = max(oldxs),max(oldys)
    oldwidth = oldxmax - oldxmin
    oldheight = oldymax - oldymin
    newxmin,newymin = min(newxs),min(newys)
    newxmax,newymax = max(newxs),max(newys)
    newwidth = newxmax - newxmin
    newheight = newymax - newymin
    
    print "newextremes",newxmin,newymin,newxmax,newymax

    # function for determining correct axis orientation
    def increases(values):
        valuegen = (val for val in values if (val or val==0) and val not in (float("Nan"),float("inf"),float("-inf")) )
        val1,val2 = next(valuegen),next(valuegen)
        if val1 < val2: return True
        elif val1 > val2: return False
        else: raise Exception("Found repeated neighbouring value in sequence, how to deal?")

    # determine correct old axis directions
    if increases(oldxs): oldxleft,oldxright = oldxmin,oldxmax
    else: oldxleft,oldxright = oldxmax,oldxmin
    if increases(oldys): oldytop,oldybottom = oldymin,oldymax
    else: oldytop,oldybottom = oldymax,oldymin

    print "oldbbox",oldxleft,oldytop,oldxright,oldybottom

    if len(newxs) == len(oldxs) and len(newys) == len(oldys):
        
        # determine correct new axis directions
        if increases(newxs): newxleft,newxright = newxmin,newxmax
        else: newxleft,newxright = newxmax,newxmin
        if increases(newys): newytop,newybottom = newymin,newymax
        else: newytop,newybottom = newymax,newymin

        # NOTE: below has not been updated
        # ...
        
        for rowi, (oldy, newy) in enumerate(zip(oldys, newys)):
            newrow = []
            
            # find the closest row
            newyratio = (newy - newymin) / float(newheight)
            # to retrieve pixel (not intuitive)
            #r1 = int(round(height*yratio))
            # to displace pixel
            oldyratio = (oldy - oldymin) / float(oldheight)
            newrowi = int(round(height*newyratio))
            oldrowi = int(round(height*oldyratio))
            rowdiff = newrowi-oldrowi
            r1 = oldrowi - rowdiff
            # prevent going out of bounds
            r1 = max((r1,0))
            r1 = min((r1,len(oldgrid)))

            for coli, (oldx, newx) in enumerate(zip(oldxs, newxs)):
                
                # find the closest column
                newxratio = (newx - newxmin) / float(newwidth)
                # to retrieve pixel (not intuitive)
                #c1 = int(round(height*yratio))
                # to displace pixel
                oldxratio = (oldx - oldxmin) / float(oldwidth)
                newcoli = int(round(width*newxratio))
                oldcoli = int(round(width*oldxratio))
                coldiff = newcoli-oldcoli
                c1 = oldcoli - coldiff
                # prevent going out of bounds
                c1 = max((c1,0))
                c1 = min((c1,len(oldgrid[0])))

                # find the old point that is nearest to the newpoint
                try:
                    val = oldgrid[r1][c1]
                    
                except IndexError:
                    # need better handling, why indexerror?
                    val = None
                    
                newrow.append(val)
                
            yield newrow

    elif len(newxs) == len(oldxs) * len(oldys) and len(newys) == len(oldys) * len(oldxs):

        # determine correct new axis directions
        for _i in range(len(oldxs)):
            _rownewxs = newxs[_i*len(oldys):_i*len(oldys)+len(oldxs)]
            if len(_rownewxs) > 1:
                if increases(_rownewxs): newxleft,newxright = newxmin,newxmax
                else: newxleft,newxright = newxmax,newxmin
                break
        for _i in range(len(oldys)):
            _rownewys = newys[_i::len(oldxs)]
            if len(_rownewys) > 1:
                if increases(_rownewys): newytop,newybottom = newymin,newymax
                else: newytop,newybottom = newymax,newymin
                break

        print "newbbox",newxleft,newytop,newxright,newybottom

        # ...
        newxs = (x for x in newxs)
        newys = (y for y in newys)

        # SORT OF WORKS, BUT NOT WITH MERCATOR, SO PROB NOT TRULY CORRECT...
        # help: http://www.cs.princeton.edu/courses/archive/spr11/cos426/notes/cos426_s11_lecture03_warping.pdf

        newxincr = newwidth/float(len(oldgrid[0]))
        newyincr = newheight/float(len(oldgrid))
        regularnewy = newytop

        for rowi,oldy in enumerate(oldys):
            regularnewx = newxleft
            newrow = []

            for coli,oldx in enumerate(oldxs):

                newx = next(newxs)
                newy = next(newys)

                # how much the forward mapping of the target cell's oldcoord
                # ...differed from the expected newcoord at the target cell.
                newyoffset = regularnewy - newy
                newxoffset = regularnewx - newx

                newyoffsetratio = newyoffset / float(newheight)
                newxoffsetratio = newxoffset / float(newwidth)

                # offset the oldcoord by that same amount
                oldyoffset = oldheight*newyoffsetratio
                oldxoffset = oldwidth*newxoffsetratio

                oldyratio = ((oldy - oldytop)+oldyoffset) / float(oldheight)
                oldxratio = ((oldx - oldxleft)+oldxoffset) / float(oldwidth)

                # get the pixel at the same ratio position as the offset oldcoord
                r1 = int(round(height*oldyratio))
                c1 = int(round(width*oldxratio))

                # prevent going out of bounds
                r1 = max((r1,0))
                r1 = min((r1,len(oldgrid)))
                c1 = max((c1,0))
                c1 = min((c1,len(oldgrid[0])))


                # find the old point that is nearest to the newpoint
                try:
                    val = oldgrid[r1][c1]
                    
                except IndexError:
                    # need better handling, why indexerror?
                    val = None
                    
                newrow.append(val)
                regularnewx += newxincr
                
            yield newrow
            regularnewy += newyincr
        
##        for rowi,oldy in enumerate(oldys):
##            newrow = []
##
##            for coli,oldx in enumerate(oldxs):
##
##                newx = next(newxs)
##                newy = next(newys)
##
##
####                # bleh
####                def to_src_px(pt):
####                    # linear transform from src_bbox to src_quad
####                    src_bbox = (xleft,ytop,
####                    src_quad = 
####                dst_quad = (coli,rowi)
####                dst_w = (newx,newy)
####                src_w = (oldx,oldy)
####                src_quad = to_src_px(src_w)
##
##                
##    
##                # find the closest row
##                newyratio = (newy - newytop) / float(newybottom-newytop)
##                oldyratio = (oldy - oldytop) / float(oldybottom-oldytop)
##                #newrowi = int(round(height*newyratio))
##                #oldrowi = int(round(height*oldyratio))
##                #rowdiff = newrowi-oldrowi
##                #r1 = oldrowi - rowdiff
##                diffyratio = oldyratio - newyratio
##                
##                #new2oldy = oldytop + oldheight * newyratio
##                #oldyratio = (new2oldy-oldytop) / float(oldwidth)
##                
##                r1 = int(round(height*(oldyratio+diffyratio)))
##                #print "y",oldy,oldyratio,newy,newyratio,diffyratio
##                #print oldyratio,diffyratio, r1
##                # prevent going out of bounds
##                r1 = max((r1,0))
##                r1 = min((r1,len(oldgrid)))
##                
##                # find the closest column
##                newxratio = (newx - newxleft) / float(newxright-newxleft)
##                oldxratio = (oldx - oldxleft) / float(oldxright-oldxleft)
##                #newcoli = int(round(width*newxratio))
##                #oldcoli = int(round(width*oldxratio))
##                #coldiff = newcoli-oldcoli
##                #c1 = oldcoli - coldiff
##                diffxratio = oldxratio - newxratio
##                c1 = int(round(width*(oldxratio+diffxratio)))
##                #print "x",oldx,oldxratio,newx,newxratio,diffxratio
##                # prevent going out of bounds
##                c1 = max((c1,0))
##                c1 = min((c1,len(oldgrid[0])))
##
##                # find the old point that is nearest to the newpoint
##                try:
##                    val = oldgrid[r1][c1]
##                    
##                except IndexError:
##                    # need better handling, why indexerror?
##                    val = None
##                    
##                newrow.append(val)
##                
##            yield newrow

    else:
        raise Exception("newcoords must be same length as oldcoords, or each be as long as the entire old grid.")

def gridinterp_bilin(oldgrid, oldxs, oldys, newxs, newys):
    """
    Bilinear interpolation
    
    'each of the grid points in the dest grid contains the average of the nearest four
    grid points in the source grid, weighted by their distance from the destination
    grid point. If any of the four surrounding input grid points contain missing
    data, the interpolated value will be flagged as missing.'

    http://www.iges.org/grads/gadoc/gradfunclterp.html
    """
    
    width = len(oldxs)-1
    height = len(oldys)-1

    oldxmin,oldymin = min(oldxs),min(oldys)
    oldxmax,oldymax = max(oldxs),max(oldys)
    oldwidth = oldxmax - oldxmin
    oldheight = oldymax - oldymin
    newxmin,newymin = min(newxs),min(newys)
    newxmax,newymax = max(newxs),max(newys)
    newwidth = newxmax - newxmin
    newheight = newymax - newymin    

    # newcoords can be rectangular or vary all over
    if len(newxs) == len(oldxs) and len(newys) == len(oldys):
        
        for rowi, (oldy, newy) in enumerate(zip(oldys,newys)):
            #print rowi,oldy,newy
            newrow = []
            
            yratio = (newy - newymin) / float(newheight)
            #print yratio,oldy,newy
            new2oldy = oldymin + oldheight * yratio

            # find the two closest rows
            r1 = int(round(height*yratio))
            r2 = int(round(height*yratio+1))
            #if oldys[r1]==oldys[r2]:
            #    print r1,r2,oldys[r1],oldys[r2]

            for coli, (oldx, newx) in enumerate(zip(oldxs,newxs)):
                xratio = (newx - newxmin) / float(newwidth)
                new2oldx = oldxmin + oldwidth * xratio

                # find the two closest columns
                c1 = int(round(width*xratio))
                c2 = int(round(width*xratio+1))
                #if oldxs[c1]==oldxs[c2]:
                #    print c1,c2,oldxs[c1],oldxs[c2]

                # find the four old points that are nearest to the newpoint
                # and take bilinear interp between those
                try:
                    intraxratio = (new2oldx - oldxs[c1]) / float(oldxs[c2] - oldxs[c1])
                    interp_xtop = oldgrid[r1][c1] + (oldgrid[r1][c2] - oldgrid[r1][c1]) * intraxratio
                    interp_xbottom = oldgrid[r2][c1] + (oldgrid[r2][c2] - oldgrid[r2][c1]) * intraxratio
                    #print "xs", intraxratio, interp_xtop, interp_xbottom

                    intrayratio = (new2oldy - oldys[r1]) / float(oldys[r2] - oldys[r1])
                    #print "ys",oldys[r1], new2oldy, oldys[r2], intrayratio
                    val = interp_xtop + (interp_xbottom - interp_xtop) * intrayratio
                    
                except IndexError:
                    # need better handling, why indexerror?
                    val = None

                except ZeroDivisionError:
                    # need better handling, shouldnt happen
                    val = None
                    
                newrow.append(val)
                
            yield newrow
        
    elif len(newxs) == len(oldxs) * len(oldys) and len(newys) == len(oldys) * len(oldxs):
        newxs = (x for x in newxs)
        newys = (y for y in newys)
        
        for rowi in range(len(oldys)):

            newrow = []

            for coli in range(len(oldxs)):

                newy = next(newys)
                newx = next(newxs)
                
                yratio = (newy - newymin) / float(newheight)
                new2oldy = oldymin + oldheight * yratio

                # find the two closest rows
                r1 = int(round(height*yratio))
                r2 = int(round(height*yratio+1))

                xratio = (newx - newxmin) / float(newwidth)
                new2oldx = oldxmin + oldwidth * xratio

                # find the two closest columns
                c1 = int(round(width*xratio))
                c2 = int(round(width*xratio+1))

                # find the four old points that are nearest to the newpoint
                # and take bilinear interp between those
                try:
                    intraxratio = (new2oldx - oldxs[c1]) / float(oldxs[c2] - oldxs[c1])
                    interp_xtop = oldgrid[r1][c1] + (oldgrid[r1][c2] - oldgrid[r1][c1]) * intraxratio
                    interp_xbottom = oldgrid[r2][c1] + (oldgrid[r2][c2] - oldgrid[r2][c1]) * intraxratio
                    #print "xs", intraxratio, interp_xtop, interp_xbottom

                    intrayratio = (new2oldy - oldys[r1]) / float(oldys[r2] - oldys[r1])
                    #print "ys",oldys[r1], new2oldy, oldys[r2], intrayratio
                    val = interp_xtop + (interp_xbottom - interp_xtop) * intrayratio
                    
                except IndexError:
                    # need better handling, why indexerror?
                    val = None

                except ZeroDivisionError:
                    # need better handling, shouldnt happen
                    val = None
                    
                newrow.append(val)
                
            yield newrow
        
    else:
        raise Exception("newcoords must be same length as oldcoords, or each be as long as the entire old grid.")



def img_resize_near(grid, w2, h2):
    """
    From techalgorithm.com
    """
    w1 = len(grid[0])
    h1 = len(grid)
    
    newgrid = []
    x_ratio = w1/float(w2)
    y_ratio = h1/float(h2)
    for i in xrange(0, h2):
        py = int(i*y_ratio)
        newrow = []
        for j in xrange(0, w2):
            px = int(j*x_ratio)
            newval = grid[py][px]
            newrow.append(newval)
        newgrid.append(newrow)
    return newgrid

def img_resize_bilinear(grid, w2, h2):
    """
    From techalgorithm.com
    """

    w = len(grid[0])
    h = len(grid)
    
    newgrid = []
    x_ratio = (w-1)/float(w2)
    y_ratio = (h-1)/float(h2)
    for i in xrange(0, h2):
        y = int(y_ratio * i)
        y_diff = (y_ratio * i) - y
        newrow = []
        for j in xrange(0, w2):
            x = int(x_ratio * j)
            x_diff = (x_ratio * j) - x
            
            A = grid[y][x]
            B = grid[y][x+1]
            C = grid[y+1][x]
            D = grid[y+1][x+1]
            
            # Y = A(1-w)(1-h) + B(w)(1-h) + C(h)(1-w) + Dwh
            newval = A*(1-x_diff)*(1-y_diff) +  B*(x_diff)*(1-y_diff) + C*(y_diff)*(1-x_diff) +  D*(x_diff*y_diff)
            
            newrow.append(newval)
        newgrid.append(newrow)
    return newgrid





if __name__ == "__main__":
    import PIL, PIL.Image, PIL.ImageOps
    import math
    from random import randrange

    # test idw
##    import time
##    gridxs,gridys = range(720),range(360)
##    w,h = len(gridxs),len(gridys)
##    points = [(randrange(10,710), randrange(10,350), randrange(255))
##              for _ in range(30)]
##    t = time.clock()
##    grid = pointinterp_idw(points, gridxs, gridys)
##    img = PIL.Image.new("L", (w,h))
##    img.putdata([val for row in grid for val in row])
##    print time.clock()-t
##    img.save("idw.png")
##    fdfsdfsd

    ###################

    # from math
    w,h = 1000,1000
    oldxs = range(w)
    oldys = range(h)
    oldgrid = [[(x+y)/10 for x in oldxs] for y in oldys]

    # or from img
##    img = PIL.Image.open("ble.png").convert("L")
##    w,h = img.size
##    oldxs = range(w)
##    oldys = range(h)
##    oldgrid = list(img.getdata())
##    oldgrid = zip(*[oldgrid[i::w] for i in range(w)])

    # put data  
    img = PIL.Image.new("L", (w,h))
    img.putdata([val for row in oldgrid for val in row])
    img.save("orig.png")

    for row in oldgrid:
        pass #print row

    # transform coords, interp, and put data
    newxs = [x**3 for x in oldxs]
    newys = [math.sin(y/100) for y in oldys]
    newgrid = list(gridinterp_near(oldgrid, oldxs, oldys, newxs, newys))
    img = PIL.Image.new("L", (w,h))
    print len([val for row in newgrid for val in row])
    img.putdata([val for row in newgrid for val in row])
    img.save("new.png")

    for row in newgrid:
        pass #print row




    
