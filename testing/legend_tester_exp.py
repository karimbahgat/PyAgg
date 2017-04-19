
from pyagg.legend import FillSizeSymbol, Label, SymbolGroup, Legend
from pyagg import Canvas



legend = Legend(direction="s",
                title="Legend", titleoptions=dict(font="calibri", textsize=20, side="w"),
                )


##def grouplabel():
##    c = Canvas(200,40)
##    c.draw_text("SymbolGroup 1",(0,0),anchor="nw", textsize="40%")
##    return c
##legend.add_item(Symbol(grouplabel))
##
##
##gr = SymbolGroup(direction="e", anchor="s")
##gr.add_item(Symbol("circle","fillsize",fillsize=100,outlinewidth=10))
##gr.add_item(Symbol("triangle","fillsize",fillsize=200,outlinewidth=10))
##gr.add_item(Symbol("box","fillsize",fillsize=300,outlinewidth=10))
##legend.add_item(gr)
##
##
##def grouplabel():
##    c = Canvas(200,40)
##    c.draw_text("SymbolGroup 2",(0,0),anchor="nw", textsize="40%")
##    return c
##legend.add_item(Symbol(grouplabel))
##
##
##gr = SymbolGroup(direction="w", anchor="s")
##gr.add_item(Symbol("circle","fillsize",fillsize=100,outlinewidth=10))
##gr.add_item(Symbol("triangle","fillsize",fillsize=200,outlinewidth=10))
##gr.add_item(Symbol("box","fillsize",fillsize=300,outlinewidth=10))
##legend.add_item(gr)


##def label(text):
##    c = Canvas(200,40)
##    c.draw_text(text,(0,0),anchor="nw", textsize="40%")
##    return c
##legend.add_item(Label("SymbolGroup 3", font="calibri", textsize=20))

sideways = SymbolGroup(direction="e", anchor="w",
                       #title="SymbolGroup3", titleoptions=dict(font="calibri", textsize=20))
                       )

##gr = SymbolGroup(items=[SymbolGroup([Symbol("circle","fillsize",fillsize=300,outlinewidth=10),
##                                     Label("Symbol 3")],
##                                    direction="e", anchor="n"),
##                         SymbolGroup([Symbol("circle","fillsize",fillsize=200,outlinewidth=10),
##                                     Label("Symbol 2")],
##                                    direction="e", anchor="n"),
##                         SymbolGroup([Symbol("circle","fillsize",fillsize=100,outlinewidth=10),
##                                     Label("Symbol 1")],
##                                    direction="e", anchor="n"),
##                        ],
##                 direction="center",
##                 anchor="center",
##                 )
gr = SymbolGroup(title="Circle fillsize",
                items=[FillSizeSymbol("circle",fillsize=300,outlinewidth=10,label="Symbol 3",anchor="center",labeloptions=dict(side="ne")),
                         FillSizeSymbol("circle",fillsize=200,outlinewidth=10,label="Symbol 2",anchor="center"),
                         FillSizeSymbol("circle",fillsize=100,outlinewidth=10,label="Symbol 1",anchor="center"),
                        ],
                 direction="s",
                 anchor="s",
                 fillcolor="blue",
                 )
sideways.add_item(gr)

##gr = SymbolGroup(direction="n", anchor="w")
##gr.add_item(Symbol(lambda: label("Symbol 1")))
##gr.add_item(Symbol(lambda: label("Symbol 2")))
##gr.add_item(Symbol(lambda: label("Symbol 3")))
##sideways.add_item(gr)

legend.add_item(gr)


legend.render().save("testlegend.png")



