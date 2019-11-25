"""
Canvas subclass specializing in being a Legend showing assigned symbology. 
"""

from .canvas import Canvas


#######


class _Symbol:
    def __init__(self, type, refcanvas=None, **kwargs):
        """
        - Type is the type of geometry to draw, eg box, circle, etc.
        """
        self.type = type
        self.refcanvas = refcanvas
        self.kwargs = dict(kwargs)

    def render(self):
        # WARNING: MESSY AND ONLY WORKING IN SOME CASES, OUTLINE NOT CURRENTLY CONSIDERED
        # NEED BETTER AND SIMPLER APPROACH...

        kwargs = dict(self.kwargs)
        
        # get required dimensions
        if hasattr(self.type, "__call__"):
            # symbol is specified with a function that returns its rendered canvas (lowlevel)
            rendered = self.type(**kwargs)
            reqwidth = rendered.width
            reqheight = rendered.height
            
        else:
            # symbol is specified with the canvas method type and args (more convenient)
            if self.refcanvas:
                # dimensions autoretrieved and converted to pixels from refcanvas
                info = dict(self.refcanvas._check_options(kwargs))
                if self.type == "line":
                    reqheight = info["fillsize"]
                    reqwidth = reqheight * 5  # 5 times longer to look like a line
                else:
                    reqwidth = info["fillwidth"]
                    reqheight = info["fillheight"]
            else:
                # user has to specify size manually
                info = dict(kwargs)
                info.update(fillwidth=info["fillsize"], fillheight=info["fillsize"])

                # calculate size
                if self.type in ("box","triangle"):
                    reqwidth,reqheight = info["fillwidth"]*2,info["fillheight"]*2
                elif self.type in ("circle","pie"):
                    reqwidth,reqheight = info["fillwidth"]*2,info["fillheight"]*2
                elif self.type == "line":
                    reqheight = info["fillsize"]
                    reqwidth = reqheight * 5  # 5 times longer to look like a line
                elif self.type == "polygon":
                    reqheight = info["fillheight"]
                    reqwidth = info["fillwidth"]
                else:
                    raise Exception("Symbol type not recognized")

            # make sure to pass size to drawing func
            kwargs["fillwidth"] = reqwidth
            kwargs["fillheight"] = reqheight
            kwargs["outlinewidth"] = info.get("outlinewidth")

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
            drawtype = "box" if self.type in ("polygon","line") else self.type
            func = getattr(c, "draw_"+drawtype)
            func(xy=(x,y), anchor="center", **kwargs)

        c.drawer.flush() # STRANGE BUG, DOESNT RENDER UNLESS CALLING FLUSH HERE...
        c.update_drawer_img()

        return c


class _Gradient(_Symbol):
    def __init__(self, gradient, 
                 length, thickness,
                 refcanvas=None,
                 direction="e",
                 padding=0.05):

        self.refcanvas = refcanvas

        self.gradient = gradient
        self.length = length
        self.thickness = thickness
        
        self.direction = direction
        self.padding = padding

    def render(self):
        # fillsize is used directly
        if self.refcanvas: 
            info = dict(length=self.refcanvas.parse_relative_dist(self.length),
                        thickness=self.refcanvas.parse_relative_dist(self.thickness))
        else:
            tempcanv = Canvas(10,10)
            info = dict(length=tempcanv.parse_relative_dist(self.length),
                        thickness=tempcanv.parse_relative_dist(self.thickness))

        # get size
        if self.direction in "ns":
            reqwidth, reqheight = info["thickness"],info["length"]
            line = [(reqwidth/2.0,0),(reqwidth/2.0,reqheight)] # south
            if self.direction == "n": line = [line[1],line[0]] # north
        else:
            reqwidth, reqheight = info["length"],info["thickness"]
            line = [(0,reqheight/2.0),(reqwidth,reqheight/2.0)] # east
            if self.direction == "w": line = [line[1],line[0]] # west
                    
        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        c.draw_gradient(line, self.gradient, info["thickness"]) 

        c.drawer.flush() # STRANGE BUG, DOESNT RENDER UNLESS CALLING FLUSH HERE...
        c.update_drawer_img()

        return c


class Label(_Symbol):
    def __init__(self, text, refcanvas=None, **kwargs):
        self.text = text
        self.refcanvas = refcanvas
        self.kwargs = dict(kwargs)
        self.kwargs["textsize"] = self.kwargs.get("textsize", "2.1%w") #8)

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
        text = self.text if isinstance(self.text, (unicode,str)) else str(self.text)
        textlines = text.split("\n")
        widths,heights = zip(*[font.getsize(line) for line in textlines])
        reqwidth, reqheight = max(widths),sum(heights)
                    
        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        x = reqwidth / 2.0
        y = reqheight / 2.0
        info['anchor'] = 'center'
        info['textsize'] /= c.ppi / 97.0 # canvas will blow up size based on ppi, so input the inverse to end up at same size
        c.draw_text(text, xy=(x,y), **info)
        #c.view()

        return c



class _BaseGroup:
    def __init__(self, items=None, direction="e", padding=0.05, anchor=None, **boxoptions):

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
        anchor = override.get("anchor") or self.anchor
        boxoptions = override.get("boxoptions") or self.boxoptions

        rensymbols = [s.render() for s in self.items]
        rensymbols = [s for s in rensymbols if s]
        if not rensymbols:
            return None
        
        if direction in ("e","w"):
            reqwidth = sum((symbol.width for symbol in rensymbols))
            reqheight = max((symbol.height for symbol in rensymbols))

            # padding
            padpx = reqwidth * padding
            reqwidth += padpx * (len(rensymbols)+1) # also pad start and end
            reqheight += padpx * 2 # also pad start and end

            # anchoring
            anchor = anchor or 'n'
            x = padpx + rensymbols[0].width / 2.0
            if anchor == "n":
                y = padpx
            elif anchor == "s":
                y = reqheight - padpx
            elif anchor in ("center","w","e"):
                y = reqheight / 2.0
            else:
                raise Exception("Invalid anchor value")
            
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
            anchor = anchor or 'w'
            y = padpx + rensymbols[0].height / 2.0
            if anchor == "e":
                x = reqwidth - padpx
            elif anchor == "w":
                x = padpx
            elif anchor in ("center","n","s"):
                x = reqwidth / 2.0
            else:
                raise Exception("Invalid anchor value")
            
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
            anchor = anchor or 'center'
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

        else:
            raise Exception("Invalid direction value")
        
        # create the canvas
        # TODO: Need to change, the outline is drawn on standalone canvas, so half of it spills outside
        c = Canvas(reqwidth, reqheight)
        c.draw_box(bbox=[0,0,reqwidth+0.5,reqheight-1], **boxoptions)

        # draw in direction
        #print "drawing group",reqwidth,reqheight
        for symbol in rensymbols:
            #print "child size",symbol.width,symbol.height
            #symbol.view()
            c.paste(symbol, (x,y), anchor=anchor)
            # TODO: fix error where semitransparent colors disappear entirely when pasting
            # ...
            
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

    def _default_boxoptions(self, **kwargs):
        boxoptions = dict(fillcolor=None,
                          outlinecolor=None)
        boxoptions.update(kwargs)
        return boxoptions


class BaseGroup(_BaseGroup):
    # TODO: This is where title should be allowed
    # all others with titles or labels should inherit from this one
    # TODO: Label should be expressed as % of symbol maybe???
    # ...
    def __init__(self, refcanvas=None, items=None, title="", titleoptions=None, direction="e", padding=0.01, anchor=None, **boxoptions):
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

    def add_symbol(self, shape, label="", labeloptions=None, padding=0.01, **symboloptions):
        labeloptions = labeloptions or dict()
        if not "side" in labeloptions: labeloptions["side"] = "e"
        obj = Symbol(shape=shape,
                       refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                       label=label, labeloptions=labeloptions,
                       **symboloptions)
        self.add_item(obj)

    def add_symbols(self, symbols, direction="s", anchor="w", title="", titleoptions=None, padding=0, labeloptions=None):
        """- symbols is sequence of shape,label,symboloptions tuples"""
        labeloptions = labeloptions or dict()

        if not "side" in labeloptions: labeloptions["side"] = "e"
        group = SymbolGroup(refcanvas=self.refcanvas, direction="center", anchor=anchor, title=title, titleoptions=titleoptions, padding=0) # for continuous, sizes stay in one place
        for shape,label,symboloptions in symbols:
            _symboloptions = dict(symboloptions)
            obj = Symbol(shape=shape,
                           refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                           label=label, labeloptions=labeloptions,
                           **_symboloptions)
            group.add_item(obj)
        self.add_item(group)

    def add_fillcolors(self, shape, breaks, classvalues, valuetype="discrete", valueformat=None, direction="s", anchor="w", title="", titleoptions=None, padding=0.01, labeloptions=None, **symboloptions):

        # NOTE: refcanvas is not inherited here, since this would lead to unexpected sizes after unit conversion
        # TODO: maybe allow specific size units by splitting away unit, then calculating, then adding the unit back in
        # ...

        labeloptions = labeloptions or dict()
        
        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = valueformat
                if not frmtstring.startswith(","): frmtstring = ","+frmtstring # adds thousand separator
                valueformat = lambda val: format(val, frmtstring)
            breaks = [valueformat(brk) for brk in breaks]

        if valuetype == "proportional":
            # TODO: maybe also proportional sizes....
            if not "side" in labeloptions: labeloptions["side"] = "e"
            _symboloptions = dict(symboloptions)
            # TODO: symgroup south dir makes correct, but same dir goes kookoo...
            # ...
            group = SymbolGroup(refcanvas=self.refcanvas, direction="s", anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            obj = GradientSymbol(classvalues, breaks, length=_symboloptions["length"], thickness=_symboloptions["thickness"],
                                 padding=padding,
                                 refcanvas=self.refcanvas,
                                 direction=direction, anchor=anchor, labeloptions=labeloptions)
            group.add_item(obj)
            self.add_item(group)
            
        elif valuetype == "continuous":
            if not "side" in labeloptions: labeloptions["side"] = "e"
            prevbrk = breaks[0]
            group = SymbolGroup(refcanvas=self.refcanvas, direction=direction, anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classvalues[i], outlinecolor=None)
                obj = FillColorSymbol(shape=shape,
                                      refcanvas=self.refcanvas,
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                       padding=0, # crucial to make them into a continuous gradient
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)
            
        elif valuetype == "discrete":
            if not "side" in labeloptions: labeloptions["side"] = "e"
            prevbrk = breaks[0]
            group = SymbolGroup(refcanvas=self.refcanvas, direction=direction, anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classvalues[i])
                obj = FillColorSymbol(shape=shape,
                                      refcanvas=self.refcanvas,
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                      padding=padding,
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)

        elif valuetype == "categorical":
            if not "side" in labeloptions: labeloptions["side"] = "e"
            group = SymbolGroup(refcanvas=self.refcanvas, direction=direction, anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            for category,classval in zip(breaks,classvalues):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillcolor=classval)
                obj = FillColorSymbol(shape=shape,
                                      refcanvas=self.refcanvas,
                                       label="%s"%category, labeloptions=labeloptions,
                                      padding=padding,
                                       **_symboloptions)
                group.add_item(obj)
            self.add_item(group)

        else:
            raise Exception("Unknown valuetype")

    def add_fillsizes(self, shape, breaks, classvalues, valuetype="discrete", valueformat=None, direction="s", anchor="w", title="", titleoptions=None, padding=0, labeloptions=None, **symboloptions):
        
        labeloptions = labeloptions or dict()

        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = valueformat
                if not frmtstring.startswith(","): frmtstring = ","+frmtstring # adds thousand separator
                valueformat = lambda val: format(val, frmtstring)
            breaks = [valueformat(brk) for brk in breaks]

        if valuetype == "proportional":
            # TODO: Experimental, not fully tested...
            if not "side" in labeloptions: labeloptions["side"] = "n" 
            group = SymbolGroup(refcanvas=self.refcanvas, direction="center", anchor="s", title=title, titleoptions=titleoptions, padding=0) # for continuous, sizes stay in one place
            breaks = [breaks[0], breaks[-1]]
            classvalues = [classvalues[0], classvalues[-1]]
            for brk,classval in sorted(zip(breaks, classvalues), key=lambda(b,cv): cv, reverse=True):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillsize=classval)
                obj = FillSizeSymbol(shape=shape,
                                       refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                                       label="%s"%brk, labeloptions=labeloptions,
                                       padding=0, # crucial to make them into a continuous gradient
                                       **_symboloptions)
                group.add_item(obj)
            self.add_item(group)

        elif valuetype == "continuous":
            if not "side" in labeloptions: labeloptions["side"] = "e"
            prevbrk = breaks[0]
            group = SymbolGroup(refcanvas=self.refcanvas, direction="center", anchor=anchor, title=title, titleoptions=titleoptions, padding=0) # for continuous, sizes stay in one place
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
            if not "side" in labeloptions: labeloptions["side"] = "e"
            prevbrk = breaks[0]
            group = SymbolGroup(refcanvas=self.refcanvas, direction=direction, anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            for i,nextbrk in enumerate(breaks[1:]):
                _symboloptions = dict(symboloptions)
                _symboloptions.update(fillsize=classvalues[i])
                obj = FillSizeSymbol(shape=shape,
                                       refcanvas=self.refcanvas, # draw sizes relative to refcanvas
                                       label="%s to %s"%(prevbrk,nextbrk), labeloptions=labeloptions,
                                     padding=padding,
                                       **_symboloptions)
                group.add_item(obj)
                prevbrk = nextbrk
            self.add_item(group)

        else:
            raise Exception("Unknown valuetype")


class Symbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.01,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, refcanvas=refcanvas, title=label, titleoptions=labeloptions, padding=padding)
        
        symboloptions = dict(symboloptions)
        
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)


class FillSizeSymbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.01,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, refcanvas=refcanvas, title=label, titleoptions=labeloptions, padding=padding)

        if not "fillsize" in symboloptions:
            raise Exception("Fillsize must be set when creating a FillSizeSymbol")
        
        symboloptions = dict(symboloptions)
        symboloptions["fillcolor"] = symboloptions.get("fillcolor", None)
        symboloptions["outlinecolor"] = symboloptions.get("outlinecolor", "black")
        symboloptions["outlinewidth"] = symboloptions.get("outlinewidth", "0.5%min")
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)


class FillColorSymbol(BaseGroup):
    def __init__(self, shape, refcanvas=None,
                 label="", labeloptions=None,
                 padding=0.01,
                 **symboloptions):
        labeloptions = labeloptions or dict()
        if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, refcanvas=refcanvas, title=label, titleoptions=labeloptions, padding=padding)

        if not "fillcolor" in symboloptions:
            raise Exception("Fillcolor must be set when creating a FillColorSymbol")
        
        symboloptions = dict(symboloptions)
        symboloptions["fillsize"] = symboloptions.get("fillsize", "2%min")
        symboloptions["outlinecolor"] = symboloptions.get("outlinecolor", "black")
        symboloptions["outlinewidth"] = symboloptions.get("outlinewidth", "0.5%min")
        
        obj = _Symbol(type=shape, refcanvas=refcanvas, **symboloptions)
        self.add_item(obj)



class GradientSymbol(BaseGroup):
    def __init__(self, gradient, ticks,
                 length, thickness,
                 refcanvas=None,
                 direction="e", anchor="center",
                 title="",
                 titleoptions=None,
                 label="",
                 labeloptions=None, padding=0.05):

        titleoptions = titleoptions or dict()
        labeloptions = labeloptions or dict()
        #if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, refcanvas=refcanvas, title=title, titleoptions=titleoptions, padding=padding, direction=direction)

        grad = _Gradient(gradient, length, thickness, refcanvas=refcanvas,
                         direction=direction, padding=0)

        self.add_item(Label(ticks[0], refcanvas=refcanvas, **labeloptions))
        self.add_item(grad)
        self.add_item(Label(ticks[-1], refcanvas=refcanvas, **labeloptions))




class SymbolGroup(BaseGroup):
    pass


class Legend(BaseGroup):

    def _default_boxoptions(self, **kwargs):
        boxoptions = dict(fillcolor='white',
                          outlinecolor='black',
                          outlinewidth='3%min')
        boxoptions.update(kwargs)
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


    
