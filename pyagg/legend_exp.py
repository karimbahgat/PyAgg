"""
Canvas subclass specializing in being a Legend showing assigned symbology. 
"""

from .canvas import Canvas


#######


class _Symbol:
    def __init__(self, type, refcanvas=None, anchor="center", **kwargs):
        """
        - Type is the type of geometry to draw, eg box, circle, etc.
        """
        self.type = type
        print "symbol",refcanvas
        self.refcanvas = refcanvas
        self.anchor = anchor
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
            if self.refcanvas:
                print self.kwargs
                info = dict(self.refcanvas._check_options(self.kwargs))
                print info
                if self.type == "line":
                    reqheight = info["fillsize"]+info["outlinewidth"]
                    reqwidth = reqheight * 5  # 5 times longer to look like a line
                else:
                    reqwidth = info["fillwidth"]
                    reqheight = info["fillheight"]
            else:
                info = dict(self.kwargs)
                info.update(fillwidth=info["fillsize"], fillheight=info["fillsize"])

                # calculate size
                if self.type in ("box","triangle"):
                    reqwidth,reqheight = info["fillwidth"]*2,info["fillheight"]*2
                elif self.type in ("circle","pie"):
                    reqwidth,reqheight = info["fillwidth"]*2,info["fillheight"]*2
                elif self.type == "line":
                    reqheight = info["fillsize"]+info["outlinewidth"]
                    reqwidth = reqheight * 5  # 5 times longer to look like a line
                elif self.type == "polygon":
                    reqheight = info["fillheight"]
                    reqwidth = info["fillwidth"]
                else:
                    raise Exception("Symbol type not recognized")

            # make sure to pass size to drawing func
            self.kwargs["fillwidth"] = reqwidth
            self.kwargs["fillheight"] = reqheight

            # add outline to size (only affecting canvas size, not the draw size)
            outlinewidth = info.get("outlinewidth") if info.get("outlinewidth") and info.get("outlinecolor") else 0
            reqwidth += outlinewidth * 2
            reqheight += outlinewidth * 2

        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        x = reqwidth / 2.0
        y = reqheight / 2.0
        if hasattr(self.type, "__call__"):
            c.paste(rendered, (x,y), anchor="center")
        else:
            drawtype = "box" if self.type == "polygon" else self.type
            func = getattr(c, "draw_"+drawtype)
            func(xy=(x,y), anchor="center", **self.kwargs)

        c.drawer.flush() # STRANGE BUG, DOESNT RENDER UNLESS CALLING FLUSH HERE...
        c.update_drawer_img()

        return c


class Label(_Symbol):
    def __init__(self, text, refcanvas=None, anchor="center", **kwargs):
        self.text = text
        self.refcanvas = refcanvas
        self.anchor = anchor
        self.kwargs = dict(kwargs)

    def render(self):
        # fillsize is used directly
        if self.refcanvas: 
            info = dict(self.refcanvas._check_text_options(self.kwargs))
        else:
            info = dict(Canvas(10,10)._check_text_options(self.kwargs))

        # get size
        import PIL, PIL.ImageFont
        from . import fonthelper
        fontlocation = fonthelper.get_fontpath(info["font"])
        font = PIL.ImageFont.truetype(fontlocation, size=info["textsize"]) 
        reqwidth, reqheight = font.getsize(self.text)
                    
        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        x = reqwidth / 2.0
        y = reqheight / 2.0
        c.draw_text(self.text, xy=(x,y), anchor="center", **self.kwargs)

        return c


class _BaseGroup:
    def __init__(self, items=None, direction="e", padding=0.05, anchor="center", **boxoptions):

        # TODO: make sure that direction and anchor dont contradict each other, since this leads to weird results
        # eg direction s and anchor n
        # ...
        
        self.items = list(items) if items else []        
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
        direction = override.get("direction") or self.direction
        padding = override.get("padding") or self.padding
        boxoptions = override.get("boxoptions") or self.boxoptions

        rensymbols = [(s,s.render()) for s in self.items]

        if direction in ("e","w"):
            reqwidth = sum((rendered.width for symbol,rendered in rensymbols))
            reqheight = max((rendered.height for symbol,rendered in rensymbols))

            # padding
            padpx = reqwidth * padding
            reqwidth += padpx * (len(rensymbols)+1) # also pad start and end
            reqheight += padpx * 2 # also pad start and end
            
        elif direction in ("n","s"):
            reqwidth = max((rendered.width for symbol,rendered in rensymbols))
            reqheight = sum((rendered.height for symbol,rendered in rensymbols))

            # padding
            padpx = reqheight * padding
            reqheight += padpx * (len(rensymbols)+1) # also pad start and end
            reqwidth += padpx * 2 # also pad start and end
                
        elif direction == "center":
            reqwidth = max((rendered.width for symbol,rendered in rensymbols))
            reqheight = max((rendered.height for symbol,rendered in rensymbols))

            # padding
            padpx = reqwidth * padding # aribtrary here that uses width since goes in two directions
            reqwidth += padpx * 2 # also pad start and end
            reqheight += padpx * 2 # also pad start and end
            
        else:
            raise Exception("Invalid direction value")

        # create the canvas
        c = Canvas(reqwidth, reqheight, background=None)
        c.draw_box(bbox=[0,0,reqwidth-1,reqheight-1], **boxoptions)

        # define anchoring
        if direction in ("e","w"):
            def anchorfunc(symbol, rendered):
                # anchoring
                anchor = symbol.anchor
                x = padpx + rendered.width / 2.0
                if anchor == "n":
                    y = padpx
                elif anchor == "s":
                    y = reqheight - padpx
                elif anchor in ("center","w","e"):
                    y = reqheight / 2.0
                else:
                    raise Exception("Invalid anchor value")

                return x,y

            symbol,rendered = rensymbols[0]
            x,y = anchorfunc(symbol,rendered)
            if direction == "w":
                x = reqwidth - x # from the right

        elif direction in ("n","s"):
            def anchorfunc(symbol, rendered):
                # anchoring
                anchor = symbol.anchor
                y = padpx + rendered.height / 2.0
                if anchor == "e":
                    x = reqwidth - padpx
                elif anchor == "w":
                    x = padpx
                elif anchor in ("center","n","s"):
                    x = reqwidth / 2.0
                else:
                    raise Exception("Invalid anchor value")

                return x,y

            symbol,rendered = rensymbols[0]
            x,y = anchorfunc(symbol,rendered)
            print "start",x,y
            if direction == "n":
                y = reqheight - y # from the bottom

        elif direction == "center":
            def anchorfunc(symbol, rendered):
                # anchoring
                anchor = symbol.anchor
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
                else:
                    raise Exception("Invalid anchor value")

                return x,y

            symbol,rendered = rensymbols[0]
            x,y = anchorfunc(symbol,rendered)

        else:
            raise Exception("Invalid direction value")

        # draw in direction
        for i,(symbol,rendered) in enumerate(rensymbols):
            xoff,yoff = anchorfunc(symbol, rendered)
            print "off",xoff,yoff
            c.paste(rendered, (x+xoff,y+yoff), anchor=symbol.anchor)
            print "final",x+xoff,y+yoff
            
            # increment to next symbol position
            nextindex = i+1
            nextitem = rensymbols[nextindex] if nextindex < len(rensymbols) else None
            if nextitem:
                nextsymbol,nextrendered = nextitem
                if direction == "e":
                    x += padpx + rendered.width / 2.0 + nextrendered.width / 2.0
                elif direction == "w":
                    x -= padpx + rendered.width / 2.0 + nextrendered.width  / 2.0
                elif direction == "s":
                    y += padpx + rendered.height / 2.0 + nextrendered.height / 2.0
                elif direction == "n":
                    y -= padpx + rendered.height / 2.0 + nextrendered.height / 2.0

        return c

    def _default_boxoptions(self, fillcolor=None, outlinecolor=None):
        boxoptions = dict(fillcolor=fillcolor,
                          outlinecolor=outlinecolor)
        return boxoptions


class BaseGroup(_BaseGroup):
    # TODO: This is where title should be allowed
    # all others with titles or labels should inherit from this one
    def __init__(self, refcanvas=None, items=None, title="", titleoptions=None, direction="e", padding=0.05, anchor="center", **boxoptions):
        print items
        self.items = []

        titleoptions = titleoptions or dict()
        if title:
            obj = Label(text=title, refcanvas=refcanvas, **titleoptions)
            self.items.append(obj)

        # add a sub basegroup that contains the actual items
        self.refcanvas = refcanvas
        self._basegroup = obj = _BaseGroup(items=items, direction=direction, padding=padding, anchor=anchor) #, **boxoptions)
        self.items.append(obj)

        # title anchor
        self.padding = titleoptions.get("padding", 0.05)
        self.boxoptions = self._default_boxoptions(**boxoptions)
        side = titleoptions.get("side", "nw")
        # direction
        if side[0] == "n":
            self.direction = "s"
        elif side[0] == "s":
            self.direction = "n"
        elif side[0] == "e":
            self.direction = "w"
        elif side[0] == "w":
            self.direction = "e"
        # justify
        if len(side) > 1:
            self.anchor = side[1]
        else:
            self.anchor = "center"

    def add_item(self, item):
        self._basegroup.items.append(item)

    def add_fillcolors(self, shape, breaks, classvalues, valuetype="discrete", valueformat=None, direction="s", anchor="w", title="", padding=0, labeloptions=None, **symboloptions):

        # NOTE: refcanvas is not inherited here, since this would lead to unexpected sizes after unit conversion
        # TODO: maybe allow specific size units by splitting away unit, then calculating, then adding the unit back in
        # ...

        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = "%" + valueformat
                valueformat = lambda val: frmtstring % val
            breaks = [valueformat(brk) for brk in breaks]

        if valuetype == "continuous":
            labeloptions = labeloptions or dict(side="e")
            prevbrk = breaks[0]
            group = SymbolGroup(direction=direction, anchor=anchor, title=title, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classvalues[i], outlinecolor=None)
                obj = FillColorSymbol(shape=shape,
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                       padding=0, # crucial to make them into a continuous gradient
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)
            
        elif valuetype == "discrete":
            labeloptions = labeloptions or dict(side="e")
            prevbrk = breaks[0]
            group = SymbolGroup(direction=direction, anchor=anchor, title=title, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classvalues[i])
                obj = FillColorSymbol(shape=shape,
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)

        elif valuetype == "categorical":
            labeloptions = labeloptions or dict(side="e")
            group = SymbolGroup(direction=direction, anchor=anchor, title=title, padding=0)
            for category,classval in zip(breaks,classvalues):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classval)
                obj = FillColorSymbol(shape=shape,
                                       label="%s"%category, labeloptions=labeloptions,
                                       **_symboloptions)
                group.add_item(obj)
            self.add_item(group)

        else:
            raise Exception("Unknown valuetype")

    def add_fillsizes(self, shape, breaks, classvalues, valuetype="discrete", valueformat=None, direction="s", anchor="w", title="", padding=0, labeloptions=None, **symboloptions):
        
        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = "%" + valueformat
                valueformat = lambda val: frmtstring % val
            breaks = [valueformat(brk) for brk in breaks]

        if valuetype == "continuous":
            labeloptions = labeloptions or dict(side="e")
            prevbrk = breaks[0]
            group = SymbolGroup(direction="center", anchor=anchor, title=title, padding=0) # for continuous, sizes stay in one place
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillsize=classvalues[i])
                obj = FillSizeSymbol(shape=shape,
                                       refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                       padding=0, # crucial to make them into a continuous gradient
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)
            
        elif valuetype == "discrete":
            labeloptions = labeloptions or dict(side="e")
            prevbrk = breaks[0]
            group = SymbolGroup(direction=direction, anchor=anchor, title=title, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillsize=classvalues[i])
                print _symboloptions
                obj = FillSizeSymbol(shape=shape,
                                       refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)

        else:
            raise Exception("Unknown valuetype")


class Symbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.05,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, title=label, titleoptions=labeloptions, padding=padding)
        
        symboloptions = dict(symboloptions)
        
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)


class FillSizeSymbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.05,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, title=label, titleoptions=labeloptions, padding=padding)

        if not "fillsize" in symboloptions:
            raise Exception("Fillsize must be set when creating a FillSizeSymbol")
        
        symboloptions = dict(symboloptions)
        symboloptions["fillcolor"] = symboloptions.get("fillcolor", None)
        symboloptions["outlinecolor"] = symboloptions.get("outlinecolor", "black")
        symboloptions["outlinewidth"] = symboloptions.get("outlinewidth", 1)
        
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)


class FillColorSymbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.05,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, title=label, titleoptions=labeloptions, padding=padding)

        if not "fillcolor" in symboloptions:
            raise Exception("Fillcolor must be set when creating a FillColorSymbol")
        
        symboloptions = dict(symboloptions)
        symboloptions["fillsize"] = symboloptions.get("fillsize", 20)
        symboloptions["outlinecolor"] = symboloptions.get("outlinecolor", "black")
        symboloptions["outlinewidth"] = symboloptions.get("outlinewidth", 1)
        
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)


class SymbolGroup(BaseGroup):
    pass


class Legend(BaseGroup):

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


    
