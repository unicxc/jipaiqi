class Player:
    def __init__(self, name):
        self.name = name
        self.hand_cards = []
    def get_card_count(self, card_name):
        return self.hand_cards.count(card_name)

    def get_name(self):
        return self.name

    def get_hand_cards(self):
        return self.hand_cards

    def set_hand_cards(self, cards):
        self.hand_cards = cards

    def add_card(self, card):
        self.hand_cards.append(card)

    def remove_card(self, card):
        if card in self.hand_cards:
            self.hand_cards.remove(card)

    def clear_hand_cards(self):
        self.hand_cards = []

    def count_hand_cards(self):
        return len(self.hand_cards)

    def has_card(self, card_name):
        return card_name in self.hand_cards