
import itertools, random, time



def random_n(minval, maxval, n=1):
    ns = (random.randrange(minval,maxval) for _ in xrange(n))
    return tuple(ns)



# Begin #

import rendererclass5 as pyagg
renderer = pyagg.AggRenderer()
renderer.new_image(1000,600, background=random_n(0,222,n=3) )
renderer.geographic_space()

# load the shapes in advance before timing
import geovis
#sf = geovis.shapefile_fork.Reader("D:/Test Data/cshapes/cshapes.shp")
sf = geovis.shapefile_fork.Reader("D:/Test Data/Global Subadmins/gadm2.shp")
shapes = [shape for shape in sf.iterShapes()]

def drawpoly(poly):
    ext = poly[0]
    if len(polys) > 1: holes = poly[1:]
    else: holes = []
    flatext = [xory for xy in ext for xory in xy]
    flatholes = [[xory for xy in hole for xory in xy] for hole in holes]
    renderer.draw_polygon(flatext,
                          holes=flatholes,
                          fillcolor=random_n(0,222,n=3),
                          outlinecolor=random_n(0,222,n=3),
                          outlinewidth=1.8)

t = time.clock()
for shape in shapes:
    if shape.__geo_interface__["type"] == "Polygon":
        poly = shape.__geo_interface__["coordinates"]
        drawpoly(poly)
    elif shape.__geo_interface__["type"] == "MultiPolygon":
        multipoly = shape.__geo_interface__["coordinates"]
        for poly in multipoly:
            drawpoly(poly)
print time.clock()-t,"seconds"

renderer.save("C:/Users/BIGKIMO/Desktop/pyaggworld.png")



