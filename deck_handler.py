import random

class DeckHandler():
    
    def __init__(self):
        
        # card storage
        self.deck = []
        self.hand = []
        self.discard = []
        
        # limit variables
        self.max_hand_size = 5
        
    # all cards
    def get_all_cards(self):
        
        return self.deck + self.hand + self.discard
    
    # deck functions
    def add_spell(self, spell): self.deck.append(spell)
    
    # hand functions
    def refill_hand(self):
        
        while len(self.deck) > 0 and len(self.hand) < self.max_hand_size:
            spell = random.choice(self.deck)
            self.deck.remove(spell)
            self.hand.append(spell)
    
    def discard_from_hand(self, index):
        
        spell = self.hand.pop(index)
        self.discard.append(spell)
        return spell
    
    # discard functions
    def undiscard(self, count = 1):
        
        while count > 0 and len(self.discard) > 0:
            spell = random.choice(self.discard)
            self.discard.remove(spell)
            self.deck.append(spell)