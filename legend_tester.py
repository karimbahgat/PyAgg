
from pyagg.legend import Symbol, SymbolGroup, Legend
from pyagg import Canvas



legend = Legend(direction="s", anchor="w")


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


def label(text):
    c = Canvas(200,40)
    c.draw_text(text,(0,0),anchor="nw", textsize="40%")
    return c
legend.add_item(Symbol(lambda: label("SymbolGroup 3")))

sideways = SymbolGroup(direction="e", anchor="s")

gr = SymbolGroup(items=[SymbolGroup([Symbol("circle","fillsize",fillsize=300,outlinewidth=10),
                                     Symbol(lambda: label("Symbol 3"))],
                                    direction="e", anchor="n"),
                         SymbolGroup([Symbol("circle","fillsize",fillsize=200,outlinewidth=10),
                                     Symbol(lambda: label("Symbol 2"))],
                                    direction="e", anchor="n"),
                         SymbolGroup([Symbol("circle","fillsize",fillsize=100,outlinewidth=10),
                                     Symbol(lambda: label("Symbol 1"))],
                                    direction="e", anchor="n"),
                        ],
                 direction="center",
                 anchor="center",
                 )
sideways.add_item(gr)

##gr = SymbolGroup(direction="n", anchor="w")
##gr.add_item(Symbol(lambda: label("Symbol 1")))
##gr.add_item(Symbol(lambda: label("Symbol 2")))
##gr.add_item(Symbol(lambda: label("Symbol 3")))
##sideways.add_item(gr)

legend.add_item(sideways)


legend.render().save("testlegend.png")



