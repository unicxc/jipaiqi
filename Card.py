class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_rank(self):
        return self.rank

    def get_suit(self):
        return self.suit

    def get_card_name(self):
        rank_names = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        rank_name = rank_names.get(self.rank, str(self.rank))
        suit_name = self.suit.capitalize()
        return f"{rank_name} {suit_name}"
