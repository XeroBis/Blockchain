import smartpy as sp

@sp.module
def main():
    class Counter(sp.Contract):
        def __init__(self):
            self.data.p = ("", 0)
    
        @sp.entry_point
        def add(self, str):
            if sp.fst(self.data.p) == "":
                self.data.p = (str, 1)
            else:
                self.data.p = (sp.fst(self.data.p)+", "+str, sp.snd(self.data.p)+1)


@sp.add_test(name = "mytest")
def test():
    scenario = sp.test_scenario(main)
    c = main.Counter()
    scenario += c
    c.add(sp.string("Hello"))
    c.add(sp.string("World"))
    


