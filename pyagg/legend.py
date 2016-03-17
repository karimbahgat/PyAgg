"""
Canvas subclass specializing in being a Legend showing assigned symbology. 
"""

from .canvas import Canvas, load


#######


class Symbol:
    def __init__(self, type, *args, **kwargs):
        self.type = type
        self.kwargs = kwargs

    def render(self):
        # get required dimensions
        # ...

        # create canvas and draw
        # (ALSO NEED WAY TO USE PRERENDERED IMAGE AS SYMBOL, eg for gradients etc)
        ##c = Canvas(width=reqwidth, height=reqheight)
        ##c.__get_attr__("draw_"+self.type)(*args, **self.kwargs)

        c = load(self.type)
        
        return c


class SymbolGroup:
    def __init__(self, direction="e", padding=0.05, anchor="center", **boxoptions):
        self.symbols = []
        self.direction = direction
        self.padding = padding
        self.anchor = anchor
        self.boxoptions = boxoptions

    def add_symbol(self, symbol):
        self.symbols.append(symbol)

    def render(self, **override):
        """
        Can go up, down, left, right, or just stay in center.
        Padding between each symbol can also be adjusted.
        Returns a grouping of these symbols drawn on a canvas
        with an optional outline and background.
        """
        direction = override.get("direction") or self.direction
        padding = override.get("padding") or self.padding
        anchor = override.get("anchor") or self.anchor
        boxoptions = override.get("boxoptions") or self.boxoptions

        rensymbols = [s.render() for s in self.symbols]
        
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
        boxoptions = dict(**boxoptions)
        boxoptions.update(fillcolor=boxoptions.get("fillcolor",None))
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
            
            

class Legend:

    # somehow needs to know the unit conversions of the canvas on which
    # it will be pasted if any of the symbols use non-pixel units.

    def __init__(self):
        self.symbolgroups = []
    
    def add_symbolgroup(self, symbolgroup):
        # each symbol being a dictionary with a "type" key for the drawing operation
        # and the remaining args as options passed to that operation.
        self.symbolgroups.append(symbolgroup)

    def render(self, canvas, **boxoptions):
        """
        Renders itself to a separate Canvas. Though most users
        will want to send it to a Canvas' insert_legend() method to
        place and render it in a context. The insert_legend() method
        will run this method while passing the necessary unit conversions etc,
        retrieve the rendered
        canvas, and paste it at an xy location with a given anchor and optional
        offset.
        OR...
        Maybe just renders itself directly on the given canvas...?
        """
        # position all the symbolgroups
        for symbolgroup in self.symbolgroups:
            rendered = symbolgroup.render()
            # ...
            # ACTUALLY, JUST SUBCLASS THE SYMBOLGROUP
            # TO REUSE THE LOGIC OF POSITIONING MULTIPLE RENDERED
            # ITEMS GOING IN A PARTICULAR DIRECTION WITH PADDING.
            # THIS WOULD ALSO ALLOW ENDLESS NESTINGS OF "DIVS"
            # AND MORE ADVANCED CONFIGURATIONS AND LAYOUTS.
            # ...
            
        
        # determine the necessary size of the legend to fit all the symbolgroups
        # ...
        pass


    
