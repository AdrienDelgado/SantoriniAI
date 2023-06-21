# This file regroups helper functions and example of simple evaluation functions

import Util

# Helper functions
def get_positions_around(board, position):
    """
    Enumerates list of all valid positions around the player

    :param board: GameState representation of the current game board. See class GameState
    :param position: [3x1] list of [y,x,z] coordinates representing current position
    :return: pos_list: list of valid positions
    """
    move_actions = [('move', 'u'), ('move', 'd'), ('move', 'l'), ('move', 'r'), ('move', 'ul'), ('move', 'ur'), ('move', 'dl'), ('move', 'dr')]
    pos_list = []

    for action in move_actions:
        new_pos = move_logic(board, position, action)
        if Util.check_pos_in_grid(board, new_pos):
            pos_list.append(new_pos)
    return pos_list

def get_reachable_positions(board, position):
    """
    Enumerates list of all valid positions reachable from current state

    :param board: GameState representation of the current game board. See class GameState
    :param position: [3x1] list of [y,x,z] coordinates representing current position
    :return: pos_list: list of valid reachable positions
    """

    for new_pos in get_positions_around(board, position):
        if check_move_validity(board, position, new_pos):
            pos_list.append(new_pos)
    return pos_list

def distance_between_players(player_positions):
    """
    Calculates the distance between players 

    :param board: GameState representation of the current game board. See class GameState
    :param player_positions: list of [y,x,z] coordinates for each Player
    :return: distance: distance between the two players 
    """
    distance = max(abs(player_positions[0][0] - player_positions[1][0]), abs(player_positions[0][1] - player_positions[1][1]))
    return distance

def distance_to_center(position):
    """
    Calculates the distance between a position and the center of the board 

    :param position: [3x1] list of [y,x,z] coordinates representing current position
    :return: distance: distance between the two players 
    """
    distance = max(abs(position[0] - 2), abs(position[1] - 2))
    return distance


# Example evaluation functions. 
# This is where you create and return a score to evaluate the situation on the board. 
# Criteria that are good for you should be counted in POSITIVE, and those good for the opponent in NEGATIVE
# 
# Simple functions. You can take them as a base to get ideas or start from there.
def evaluation_function_example(self, board, player_positions):
    """
    Function that tries to maximize the height of your player
    """
    your_player = self.player_number # This is your player index in player_positions

    return player_positions[your_player][2] # This returns your player's height. 



# Composite functions. You can build evaluation functions with multiple criteria
def evaluation_function_example(self, board, player_positions):
    """
    Function that tries to maximize the height of your player and minimize the height of your opponent
    """
    your_player = self.player_number # This is your player index in player_positions
    opponent_player = (self.player_number + 1) % 2 # This the opponent player index in player_positions

    your_height = player_positions[your_player][2] # This is your player's height. 
    opponent_height = player_positions[opponent_player][2] # This is your opponent's height. 

    # This maximizes your player's height, and minimizes your opponent's height.
    # You can choose the importance of your different criteria. 
    # In this example we choose that your height is 2x more important than your opponent's height.
    return 2 * your_height - opponent_height 