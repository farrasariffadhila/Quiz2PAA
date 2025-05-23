# player.py

# Simbol Pemain (Player Symbol)
PLAYER_SYMBOL = 'P'

class Player:
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col
        self.has_second_chance = True

    def get_position(self):
        return (self.row, self.col)

    def set_position(self, r, c):
        self.row = r
        self.col = c

    def use_second_chance(self):
        if self.has_second_chance:
            self.has_second_chance = False
            return True # Second chance used
        return False # No second chance was available

    def has_second_chance_available(self):
        return self.has_second_chance