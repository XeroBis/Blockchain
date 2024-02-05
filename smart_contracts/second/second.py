import smartpy as sp

@sp.module
def main():
    class Counter(sp.Contract):
        def __init__(self):
            self.data.v = 0
    
        @sp.entry_point
        def inc(self):
            self.data.v += 1

        @sp.entry_point
        def dec(self):
            self.data.v -= 1

@sp.add_test(name = "mytest")
def test():
    scenario = sp.test_scenario(main)
    c = main.Counter()
    scenario += c
    c.inc()
    c.dec()
    


