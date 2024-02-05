import smartpy as sp

@sp.module
def main():
    class Counter(sp.Contract):
        def __init__(self):
            self.data.t = ""
    
        @sp.entry_point
        def add(self, str):
            if self.data.t == "":
                self.data.t += str
            else:
                self.data.t += ", "+str


@sp.add_test(name = "mytest")
def test():
    scenario = sp.test_scenario(main)
    c = main.Counter()
    scenario += c
    c.add(sp.string("Hello"))
    c.add(sp.string("World"))
    


