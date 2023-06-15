class HumanAgent:
    """
    Implements a Human agent to play Santorini. Moves are given by calling self.getAction().
    Actions are simply given by asking the user to input a move/build via the keyboard
    """

    def __init__(self, config, player_number):
        self.player_number = player_number
