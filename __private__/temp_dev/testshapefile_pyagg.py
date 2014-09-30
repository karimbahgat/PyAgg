
import itertools, random, time



def random_n(minval, maxval, n=1):
    ns = (random.randrange(minval,maxval) for _ in xrange(n))
    return tuple(ns)




# load the shapes in advance before timing
import geovis
sf = geovis.shapefile_fork.Reader("D:/Test Data/cshapes/cshapes.shp")
#sf = geovis.shapefile_fork.Reader("/Volumes/karim/Desktop/Current Projects/Tanzania predictions/GIS Data/Context Data/Natural/PETRODATA/Petrodata_Onshore_V1.2.shp")
#sf = geovis.shapefile_fork.Reader("/Volumes/karim/Desktop/Current Projects/Tanzania predictions/GIS Data/Context Data/Natural/dams/GRanD_dams_v1_1.shp")
#sf = geovis.shapefile_fork.Reader("/Volumes/karim/Desktop/Current Projects/Tanzania predictions/GIS Data/Event Data/ACLED/1997-2013/acled.shp")
shapes = [shape for shape in sf.iterShapes()]

def drawpoly(poly):
    ext = poly[0]
    if len(poly) > 1: holes = poly[1:]
    else: holes = []
    flatext = [xory for xy in ext for xory in xy]
    flatholes = [[xory for xy in hole for xory in xy] for hole in holes]
    renderer.draw_polygon(flatext,
                          holes=flatholes,
                          fillcolor=random_n(0,222,n=3),
                          outlinecolor=random_n(0,222,n=3),
                          outlinewidth=1.8)

def drawpoint(point):
    renderer.draw_point(point,
                        symbol="square",
                        fillsize=0.05,
                          fillcolor=random_n(0,222,n=4),
                          outlinecolor=random_n(0,222,n=3),
                          outlinewidth=1.5)


# Begin #

import rendererclass9zoomerrorfixed as pyagg
renderer = pyagg.Canvas(1000,500, background=random_n(0,222,n=3) )
renderer.geographic_space()
xleft,ybottom,xright,ytop = sf.bbox
#renderer.zoom_bbox(0,90,180,0)
renderer.zoom_bbox(xleft,ytop,xright,ybottom)
renderer.zoom_factor(-1.2)

print len(shapes)

t = time.clock()
for shape in shapes:
    if shape.__geo_interface__["type"] == "Polygon":
        poly = shape.__geo_interface__["coordinates"]
        drawpoly(poly)
    elif shape.__geo_interface__["type"] == "MultiPolygon":
        multipoly = shape.__geo_interface__["coordinates"]
        for poly in multipoly:
            drawpoly(poly)
    elif shape.__geo_interface__["type"] == "Point":
        point = shape.__geo_interface__["coordinates"]
        drawpoint(point)
print time.clock()-t,"seconds"

#renderer.save("/Users/karim/Desktop/offshore.png")
renderer.view()



