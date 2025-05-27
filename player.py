PLAYER_SYMBOL = 'P'

class Player:
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col

    def get_position(self):
        return (self.row, self.col)

    def set_position(self, r, c):
        self.row = r
        self.col = c