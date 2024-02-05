import smartpy as sp

@sp.module
def main():
    class Account(sp.Contract):
        def __init__(self):
            self.data.total = 0
            self.data.last_user = None
        
        @sp.entry_point
        def add(self, value):
            if self.data.last_user.is_none():
                self.data.total += value
                self.data.last_user = sp.Some(sp.sender)
            else:
                assert sp.sender != self.data.last_user.unwrap_some(), "Impossible de faire deux operations de suite"
                self.data.total += value
                self.data.last_user = sp.Some(sp.sender)
        
        @sp.entry_point
        def sub(self, value):
            if self.data.last_user.is_none():
                self.data.total -= value
                self.data.last_user = sp.Some(sp.sender)
            else:
                assert sp.sender != self.data.last_user.unwrap_some(), "Impossible de faire deux operations de suite"
                self.data.total -= value
                self.data.last_user = sp.Some(sp.sender)


@sp.add_test(name = "Test Account")
def test():
    c = main.Account()
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    scenario = sp.test_scenario(main)
    scenario += c
    c.add(3).run(sender = alice)
    c.sub(1).run(sender = bob)