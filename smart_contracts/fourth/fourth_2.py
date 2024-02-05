import smartpy as sp

@sp.module
def main():
    class Concat(sp.Contract):
        def __init__(self):
            self.data.r = sp.record(
                chaine = "",
                cpt = 0
            )
            
        @sp.entry_point
        def modify(self, word):
            with sp.modify_record(self.data.r) as d:
                if d.chaine == "":
                    d.chaine += word
                else:
                    d.chaine += ", " + word
                d.cpt += 1
            
@sp.add_test(name = "concatenation_test")
def test():
    scenario = sp.test_scenario(main)
    c = main.Concat()
    scenario += c
    c.modify("Bonjour")
    c.modify("Terre")