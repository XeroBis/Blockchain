import smartpy as sp

@sp.module
def main():
    owner = sp.address("tz1eGd1Gzh9cpZjW1hpzre2fLSnMAsXqRdJy")
    class Account(sp.Contract):
        def __init__(self):
            self.data.total = 0
            self.data.last_user = owner
        
        @sp.entry_point
        def add(self, value):
            assert sp.sender != self.data.last_user, "Impossible de faire 2 opérations de suite"
            self.data.total += value
            self.data.last_user = sp.sender
        
        @sp.entry_point
        def sub(self, value):
            assert sp.sender != self.data.last_user, "Impossible de faire 2 opérations de suite"
            self.data.total -= value
            self.data.last_user = sp.sender


@sp.add_test(name = "Test Account")
def test():
    c = main.Account()
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    scenario = sp.test_scenario(main)
    scenario += c
    c.add(3).run(sender = alice)
    c.sub(1).run(sender = main.owner)