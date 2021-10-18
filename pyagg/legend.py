"""
Canvas subclass specializing in being a Legend showing assigned symbology. 
"""

from .canvas import Canvas

# PY3 fix
try: 
    str = unicode
except NameError:
    pass


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
                if self.type == "line":
                    kwargs["fillwidth"] = kwargs.get("fillwidth", '5%min') # line length
                    info = dict(self.refcanvas._check_options(kwargs))
                    reqwidth = info["fillwidth"]
                    reqheight = info["fillheight"] / 2.0 # for some reason the height of a box is twice the size of the corresponding outlinewidth
                else:
                    info = dict(self.refcanvas._check_options(kwargs))
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
                    reqheight = info["fillheight"] # line thickness
                    reqwidth = info["fillwidth"] # line length
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

            # add defaults for shapes requiring extra kwargs
            if self.type == 'pie':
                kwargs['startangle'] = kwargs.get('startangle', 0)
                kwargs['endangle'] = kwargs.get('endangle', 110)

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
                 padding=0.05,
                 ):

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
        text = self.text if isinstance(self.text, str) else str(self.text)
        textlines = text.split("\n")
        widths,heights = zip(*[font.getsize(line) for line in textlines])
        reqwidth, reqheight = max(widths),sum(heights)
                    
        # create canvas and draw
        c = Canvas(width=reqwidth, height=reqheight)
        c.set_default_unit("px")
        x = reqwidth / 2.0
        y = reqheight / 2.0
        info['anchor'] = 'center'
        #info['textsize'] /= c.ppi / 97.0 # canvas will blow up size based on ppi, so input the inverse to end up at same size
        c.draw_text(text, xy=(x,y), **info)
        #c.view()

        return c



class _BaseGroup:
    def __init__(self, refcanvas=None, items=None, direction="e", padding=0.05, anchor=None, **boxoptions):

        # TODO: make sure that direction and anchor dont contradict each other, since this leads to weird results
        # eg direction s and anchor n
        # ...

        self.refcanvas = refcanvas
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
        if self.refcanvas:
            boxoptions = self.refcanvas._check_options(boxoptions)

        rensymbols = [s.render() for s in self.items]
        rensymbols = [s for s in rensymbols if s]
        if not rensymbols:
            return None
        
        if direction in ("e","w"):
            reqwidth = sum((symbol.width for symbol in rensymbols))
            reqheight = max((symbol.height for symbol in rensymbols))

            # outline
            if boxoptions['outlinewidth'] and boxoptions['outlinecolor']:
                reqwidth += boxoptions['outlinewidth']
                reqheight += boxoptions['outlinewidth']

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

            # outline
            if boxoptions['outlinewidth'] and boxoptions['outlinecolor']:
                reqwidth += boxoptions['outlinewidth']
                reqheight += boxoptions['outlinewidth']

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

            # outline
            if boxoptions['outlinewidth'] and boxoptions['outlinecolor']:
                reqwidth += boxoptions['outlinewidth']
                reqheight += boxoptions['outlinewidth']

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
        c.draw_box(bbox=[0,0,reqwidth,reqheight-1], **boxoptions)

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
    # This is a bit special, wrapper for _BaseGroup to only contain 1) title if any, and 2) a sub _BaseGroup for all the items
    # This is to allow independent 'side' of title visavis items
    # A bit messy though, might need some reworking...
    
    # TODO: All others with titles or labels should inherit from this one?
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
        self._basegroup = obj = _BaseGroup(refcanvas=refcanvas, items=items, direction=direction, padding=padding, anchor=anchor) #, **boxoptions)
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

        if not valueformat:
            minval = min(breaks)
            maxval = max(breaks)
            valrange = maxval - minval
            if valrange <= 1:
                valueformat = ".3f"
            elif valrange <= 10:
                valueformat = ".1f"
            else:
                valueformat = ".0f"
        
        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = valueformat
                if not frmtstring.startswith(","): frmtstring = ","+frmtstring # adds thousand separator
                valueformat = lambda val: format(val, frmtstring)

        if valuetype == "proportional":
            ## creates a color scalebar gradient
            if not "side" in labeloptions: labeloptions["side"] = "e" # not sure what does...?
            _symboloptions = dict(symboloptions)
            # TODO: symgroup south dir makes correct, but same dir goes kookoo...
            # ...
            # NOTE: valueformat is passed on to and handled by GradientSymbol
            group = SymbolGroup(refcanvas=self.refcanvas, direction="s", anchor=anchor, title=title, titleoptions=titleoptions, padding=0)
            minval = min(breaks)
            maxval = max(breaks)
            if 'length' not in _symboloptions: raise Exception("Proportional fillcolors requires a gradient 'length' arg")
            length = _symboloptions.pop("length")
            if 'thickness' not in _symboloptions: raise Exception("Proportional fillcolors requires a gradient 'thickness' arg")
            thickness = _symboloptions.pop("thickness")
            obj = GradientSymbol(classvalues, length=length, thickness=thickness,
                                 minval=minval, maxval=maxval,
                                 padding=padding,
                                 refcanvas=self.refcanvas,
                                 direction=direction, anchor=anchor, labeloptions=labeloptions,
                                 ticklabelformat=valueformat,
                                 **_symboloptions)
            group.add_item(obj)
            self.add_item(group)
            
        elif valuetype == "continuous":
            ## creates a continuous set of distinct colors immediately next to each other
            if not "side" in labeloptions: labeloptions["side"] = "e" # not sure what does...?
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
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
            ## creates a discrete set of distinct colors with spacing between
            if not "side" in labeloptions: labeloptions["side"] = "e" # not sure what does...?
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
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
            # same as discrete i think? 
            if not "side" in labeloptions: labeloptions["side"] = "e" # not sure what does...?
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
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

        if not valueformat:
            minval = min(breaks)
            maxval = max(breaks)
            valrange = maxval - minval
            if valrange <= 1:
                valueformat = ".3f"
            elif valrange <= 10:
                valueformat = ".1f"
            else:
                valueformat = ".0f"

        if valueformat:
            # can be callable or formatstring
            if not hasattr(valueformat, "__call__"):
                # formatstring
                frmtstring = valueformat
                if not frmtstring.startswith(","): frmtstring = ","+frmtstring # adds thousand separator
                valueformat = lambda val: format(val, frmtstring)

        if valuetype == "proportional":
            ## creates overlapping minimum and maximum size symbols
            ## to show the min-max range of proportional size values
            # TODO: Experimental, not fully tested...
            if not "side" in labeloptions: labeloptions["side"] = "n" 
            group = SymbolGroup(refcanvas=self.refcanvas, direction="center", anchor="s", title=title, titleoptions=titleoptions, padding=0) # for continuous, sizes stay in one place
            breaks = [breaks[0], breaks[-1]]
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
            classvalues = [classvalues[0], classvalues[-1]]
            for brk,classval in sorted(zip(breaks, classvalues), key=lambda b_cv: b_cv[1], reverse=True):
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
            ## creates overlapping sets of multiple continuous size steps
            if not "side" in labeloptions: labeloptions["side"] = "e"
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
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
            ## creates discrete standalone size shapes
            if not "side" in labeloptions: labeloptions["side"] = "e"
            breaks = [valueformat(brk) if valueformat else brk
                      for brk in breaks]
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
    def __init__(self, gradient, #ticks,
                 length, thickness,
                 minval, maxval,
                 refcanvas=None,
                 direction="e", tickside=None, anchor="center", # not sure what anchor does....
                 title="",
                 titleoptions=None,
                 labeloptions=None,
                 padding=0.05,
                 **kwargs):

        titleoptions = titleoptions or dict()

        defaults = Label('').kwargs #{}#'textsize':'3%max'}
        defaults.update(labeloptions or {})
        labeloptions = defaults

        tickoptions = kwargs.get('tickoptions', {})
        
        defaults = {'outlinewidth':"0.3%min"}
        defaults.update(kwargs)
        kwargs = defaults

        axisoptions = {'fillsize':kwargs['outlinewidth']} # not used?
        
        #if "padding" not in labeloptions: labeloptions["padding"] = padding
        BaseGroup.__init__(self, refcanvas=refcanvas, title=title, titleoptions=titleoptions, padding=padding, direction=direction)

        # gradient
        grad = _Gradient(gradient, length, thickness, refcanvas=refcanvas,
                         direction=direction, padding=0)

        origrender = grad.render

        def wraprender(**overrides):
            c = origrender()

            # parse correct sizes based on refcanvas
            _kwargs = refcanvas._check_options(kwargs) if refcanvas else c._check_options(kwargs)
            _kwargs['tickoptions'] = refcanvas._check_options(tickoptions) if refcanvas else c._check_options(tickoptions)            
            _kwargs['tickoptions']['fillcolor'] = _kwargs['tickoptions']['outlinecolor']
            _kwargs['tickoptions']['outlinecolor'] = None
            if direction in 'ew':
                # overrides any manually specified tickoptions fillwidth/height
                _kwargs['tickoptions']['fillwidth'] = _kwargs['outlinewidth'] # actually same for both, fillwidth here means thickness
                _kwargs['tickoptions']['fillheight'] = _kwargs['outlinewidth'] * 4
            elif direction in 'ns':
                # overrides any manually specified tickoptions fillwidth/height
                _kwargs['tickoptions']['fillwidth'] = _kwargs['outlinewidth'] # actually same for both, fillwidth here means thickness
                _kwargs['tickoptions']['fillheight'] = _kwargs['outlinewidth'] * 4
            _axisoptions = {'fillsize':_kwargs['outlinewidth'], 'fillcolor':_kwargs['outlinecolor']}
            _labeloptions = labeloptions
            if refcanvas and 'textsize' in _labeloptions:
                _labeloptions['textsize'] = refcanvas._check_text_options(_labeloptions)['textsize']
                _labeloptions['textsize_is_internal'] = True
            #_labeloptions = refcanvas._check_text_options(labeloptions) if refcanvas else c._check_text_options(labeloptions)

            # set coordspace
            if direction == 'e':
                c.custom_space(xleft=minval, ytop=1, xright=maxval, ybottom=0, lock_ratio=True)
            elif direction == 'w':
                c.custom_space(xleft=maxval, ytop=1, xright=minval, ybottom=0, lock_ratio=True)
            elif direction == 'n':
                c.custom_space(xleft=0, ytop=maxval, xright=1, ybottom=minval, lock_ratio=True)
            elif direction == 's':
                c.custom_space(xleft=0, ytop=minval, xright=1, ybottom=maxval, lock_ratio=True)
            
            # expand to allow for unknown sized tick labels
            factor = 2
            xw,yh = c.coordspace_width,c.coordspace_height
            pad = min(xw,yh) * factor # pad by some fraction of the shortest side
            x1,y1,x2,y2 = c.coordspace_bbox
            xmin,ymin,xmax,ymax = min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)
            c.crop(xmin-pad, ymin-pad, xmax+pad, ymax+pad)

            # get gradient line
            if direction in "ns":
                line = [((x1+x2)/2.0,y1),((x1+x2)/2.0,y2)] # south
                if direction == "n": line = [line[1],line[0]] # north
                linethick = xw
            else:
                line = [(x1,(y1+y2)/2.0),(x2,(y1+y2)/2.0)] # east
                if direction == "w": line = [line[1],line[0]] # west
                linethick = yh

            # draw gradient outline
            c.set_default_unit("px")
            c.draw_line(line, fillcolor=None, fillsize=str(linethick)+'x', outlinecolor=_kwargs['outlinecolor'], outlinewidth=_kwargs['outlinewidth'])

            # include tickmarks...
            alltickoptions = dict([(k,v) for k,v in _kwargs.items() if 'tick' in k])
            alltickoptions['ticklabeloptions'] = _labeloptions
            if direction in "ns":
                _tickside = tickside or 'right'
                if _tickside == 'left':
                    intercept = x1
                elif _tickside == 'right':
                    intercept = x2
                else:
                    raise Exception("tickside arg must be 'left' or 'right' for the y-axis, not %s" % _tickside)
                c.draw_axis('y', minval=minval, maxval=maxval, intercept=intercept, tickside=_tickside, fillsize=_axisoptions['fillsize'], fillcolor=_axisoptions['fillcolor'], **alltickoptions)
            else:
                _tickside = tickside or 'bottom'
                if _tickside == 'top':
                    intercept = y1
                elif _tickside == 'bottom':
                    intercept = y2
                else:
                    raise Exception("tickside arg must be 'top' or 'bottom' for the x-axis, not %s" % tickside)
                c.draw_axis('x', minval=minval, maxval=maxval, intercept=intercept, tickside=_tickside, fillsize=_axisoptions['fillsize'], fillcolor=_axisoptions['fillcolor'], **alltickoptions)

            # finally reduce to valid pixel region
            c.drawer.flush()
            c.img = c.img.crop(c.img.getbbox())
            c.update_drawer_img()

            return c
            
        grad.render = wraprender

        #self.add_item(Label(ticks[0], refcanvas=refcanvas, **labeloptions))
        self.add_item(grad)
        #self.add_item(Label(ticks[-1], refcanvas=refcanvas, **labeloptions))



class SymbolGroup(BaseGroup):
    pass


class Legend(BaseGroup):

    def _default_boxoptions(self, **kwargs):
        boxoptions = dict(fillcolor='white',
                          outlinecolor='black',
                          outlinewidth='0.3%min')
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


    
