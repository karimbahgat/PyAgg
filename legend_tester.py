
from pyagg.legend import Symbol, SymbolGroup, Legend

##symbol = Symbol("blabla")
##symbol.render(0.1).view()
##
##fdsfdsa


folder = r"C:\Users\kimo\Documents\GitHub\pshapes_site\(misc)\design ideas"

gr = SymbolGroup()
gr.add_symbol(Symbol(folder+r"\pshapes logo example.jpg"))
gr.add_symbol(Symbol(folder+r"\mailchimp-free.png"))
gr.add_symbol(Symbol(folder+r"\aqueduct.png"))
gr.render(direction="e", anchor="s").save("testlegend.png")

fdsfdsf

gr2 = SymbolGroup()
gr2.add_symbol(symbol)

lg = Legend()
lg.add_symbolgroup(gr)
lg.add_symbolgroup(gr2)

lg.render().view()
