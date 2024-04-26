import random

class DeckHandler():
    
    def __init__(self, player):
        
        # card storage
        self.deck = []
        self.hand = []
        self.discard = []
        
        self.inventory = []
        
        # limit variables
        self.max_hand_size = 5
        
        self.player = player
        
    # all cards not in inventory
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
            
        self.player.entity_handler.object_handler.scene.ui_handler.update_texture = 2
    
    def discard_from_hand(self, index):
        
        spell = self.hand.pop(index)
        self.discard.append(spell)
        return spell
    
    # discard functions
    def undiscard(self, count = 1):
        
        # retrieves cards from discard pile
        while count > 0 and len(self.discard) > 0:
            spell = random.choice(self.discard)
            self.discard.remove(spell)
            self.deck.append(spell)
            count -= 1
            
        # automatically refills hand
        self.refill_hand()
        
    # inventory functions
    def inventory_to_deck(self, spell): 
        self.inventory.remove(spell)
        self.deck.append(spell)
        
    def deck_to_inventory(self, spell):
        self.deck.remove(spell)
        self.inventory.append(spell)
    
    # removes spell from any location and adds it to hand
    def all_to_inventory(self, spell):
        if spell in self.deck: self.deck.remove(spell)
        elif spell in self.hand: 
            self.hand.remove(spell)
            self.refill_hand()
        elif spell in self.discard: self.discard.remove(spell)
        else: assert False, 'spell does not exist in player'
        self.inventory.append(spell)