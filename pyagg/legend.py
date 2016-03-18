"""
Canvas subclass specializing in being a Legend showing assigned symbology. 
"""

from .canvas import Canvas


#######


class Symbol:
    def __init__(self, type, mode=None, refcanvas=None, **kwargs):
        """
        - Type is the type of geometry to draw, eg box, circle, etc.
        - Mode is which part of the geometry to focus on, fillcolor, fillsize,
        outlinewidth, or outlinecolor. Not needed if type is a function call. 
        """
        self.type = type
        self.mode = mode
        self.refcanvas = refcanvas
        self.kwargs = dict(kwargs)

    def render(self):
        # WARNING: MESSY AND ONLY WORKING IN SOME CASES, OUTLINE NOT CURRENTLY CONSIDERED
        # NEED BETTER AND SIMPLER APPROACH...
        
        # get required dimensions
        if hasattr(self.type, "__call__"):
            # symbol is specified with a function that returns its rendered canvas (lowlevel)
            rendered = self.type(**self.kwargs)
            reqwidth = rendered.width
            reqheight = rendered.height
            
        else:
            # symbol is specified with the canvas method type and args (more convenient)
            if self.mode == "fillsize":
                # fillsize is used directly
                if self.refcanvas: 
                    info = dict(refcanvas._check_options(self.kwargs))
                else:
                    info = dict(self.kwargs)
                    info.update(fillwidth=info["fillsize"], fillheight=info["fillsize"])
                    
                if self.type in ("box","triangle"):
                    reqwidth,reqheight = info["fillwidth"]*2+info["outlinewidth"],info["fillheight"]*2+info["outlinewidth"]
                elif self.type in ("circle","pie"):
                    reqwidth,reqheight = info["fillwidth"]*2+info["outlinewidth"],info["fillheight"]*2+info["outlinewidth"]
                elif self.type == "line":
                    reqheight = info["fillsize"]+info["outlinewidth"]
                    reqwidth = reqheight * 5  # 5 times longer to look like a line
                    
            elif self.mode == "fillcolor":
                # only color is important, so ignore fillsize, using only some basic size for all
                raise Exception("Not yet implemented")

        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        x = reqwidth / 2.0
        y = reqheight / 2.0
        if hasattr(self.type, "__call__"):
            c.paste(rendered, (x,y), anchor="center")
        else:
            func = getattr(c, "draw_"+self.type)
            func(xy=(x,y), anchor="center", **self.kwargs)

        c.view() #update_drawer_img() # STRANGE BUG, DOESNT RENDER UNLESS CALLING VIEW HERE...
        return c


class _BaseGroup:
    def __init__(self, items=None, title="", direction="e", padding=0.05, anchor="center", **boxoptions):
        print items
        self.items = list(items) if items else []
        self.title = title
        self.direction = direction
        self.padding = padding
        self.anchor = anchor
        self.boxoptions = self._default_boxoptions(**boxoptions)

    def add_item(self, item):
        self.items.append(item)

    def render(self, **override):
        """
        Can go up, down, left, right, or just stay in center.
        Padding between each symbol can also be adjusted.
        Returns a grouping of these symbols drawn on a canvas
        with an optional outline and background.
        """
        title = override.get("title") or self.title
        direction = override.get("direction") or self.direction
        padding = override.get("padding") or self.padding
        anchor = override.get("anchor") or self.anchor
        boxoptions = override.get("boxoptions") or self.boxoptions

        rensymbols = [s.render() for s in self.items]
        
        if direction in ("e","w"):
            reqwidth = sum((symbol.width for symbol in rensymbols))
            reqheight = max((symbol.height for symbol in rensymbols))

            # padding
            padpx = reqwidth * padding
            reqwidth += padpx * (len(rensymbols)+1) # also pad start and end
            reqheight += padpx * 2 # also pad start and end

            # anchoring
            x = padpx + rensymbols[0].width / 2.0
            if anchor == "n":
                y = padpx
            elif anchor == "s":
                y = reqheight - padpx
            elif anchor in ("center","w","e"):
                y = reqheight / 2.0
            
            if direction == "w":
                x = reqwidth - x # from the right
            
        elif direction in ("n","s"):
            reqwidth = max((symbol.width for symbol in rensymbols))
            reqheight = sum((symbol.height for symbol in rensymbols))

            # padding
            padpx = reqheight * padding
            reqheight += padpx * (len(rensymbols)+1) # also pad start and end
            reqwidth += padpx * 2 # also pad start and end

            # anchoring
            y = padpx + rensymbols[0].height / 2.0
            if anchor == "e":
                x = reqwidth - padpx
            elif anchor == "w":
                x = padpx
            elif anchor in ("center","n","s"):
                x = reqwidth / 2.0
            
            if direction == "n":
                y = reqheight - y # from the bottom
                
        elif direction == "center":
            reqwidth = max((symbol.width for symbol in rensymbols))
            reqheight = max((symbol.height for symbol in rensymbols))

            # padding
            padpx = reqwidth * padding # aribtrary here that uses width since goes in two directions
            reqwidth += padpx * 2 # also pad start and end
            reqheight += padpx * 2 # also pad start and end

            # anchoring
            x = reqwidth / 2.0
            y = reqheight / 2.0
            
            if anchor == "e":
                x = reqwidth - padpx
            elif anchor == "w":
                x = padpx
            elif anchor == "n":
                y = padpx
            elif anchor == "s":
                y = reqheight - padpx

        # create the canvas
        c = Canvas(reqwidth, reqheight, background=None)
        c.draw_box(bbox=[0,0,reqwidth-1,reqheight-1], **boxoptions)

        # draw in direction
        for symbol in rensymbols:
            c.paste(symbol, (x,y), anchor=anchor)
            
            # increment to next symbol position
            nextindex = rensymbols.index(symbol)+1
            nextsymbol = rensymbols[nextindex] if nextindex < len(rensymbols) else None
            if nextsymbol:
                if direction == "e":
                    x += padpx + symbol.width / 2.0 + nextsymbol.width / 2.0
                elif direction == "w":
                    x -= padpx + symbol.width / 2.0 + nextsymbol.width  / 2.0
                elif direction == "s":
                    y += padpx + symbol.height / 2.0 + nextsymbol.height / 2.0
                elif direction == "n":
                    y -= padpx + symbol.height / 2.0 + nextsymbol.height / 2.0

        return c

    def _default_boxoptions(self, fillcolor=None, outlinecolor=None):
        boxoptions = dict(fillcolor=fillcolor,
                          outlinecolor=outlinecolor)
        return boxoptions
            

class SymbolGroup(_BaseGroup): pass


class Legend(_BaseGroup):

    def _default_boxoptions(self, fillcolor="white", outlinecolor="black"):
        boxoptions = dict(fillcolor=fillcolor,
                          outlinecolor=outlinecolor)
        return boxoptions

        
            











##class Legend:
##
##    # somehow needs to know the unit conversions of the canvas on which
##    # it will be pasted if any of the symbols use non-pixel units.
##
##    def __init__(self):
##        self.symbolgroups = []
##    
##    def add_symbolgroup(self, symbolgroup):
##        # each symbol being a dictionary with a "type" key for the drawing operation
##        # and the remaining args as options passed to that operation.
##        self.symbolgroups.append(symbolgroup)
##
##    def render(self, canvas, **boxoptions):
##        """
##        Renders itself to a separate Canvas. Though most users
##        will want to send it to a Canvas' insert_legend() method to
##        place and render it in a context. The insert_legend() method
##        will run this method while passing the necessary unit conversions etc,
##        retrieve the rendered
##        canvas, and paste it at an xy location with a given anchor and optional
##        offset.
##        OR...
##        Maybe just renders itself directly on the given canvas...?
##        """
##        # position all the symbolgroups
##        for symbolgroup in self.symbolgroups:
##            rendered = symbolgroup.render()
##            # ...
##            # ACTUALLY, JUST SUBCLASS THE SYMBOLGROUP
##            # TO REUSE THE LOGIC OF POSITIONING MULTIPLE RENDERED
##            # ITEMS GOING IN A PARTICULAR DIRECTION WITH PADDING.
##            # THIS WOULD ALSO ALLOW ENDLESS NESTINGS OF "DIVS"
##            # AND MORE ADVANCED CONFIGURATIONS AND LAYOUTS.
##            # ...
##            
##        
##        # determine the necessary size of the legend to fit all the symbolgroups
##        # ...
##        pass


    
