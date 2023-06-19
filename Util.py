"""
A collection of useful utilities that are utilized by other classes.
"""

import pyglet


def move_logic(board, position, action):
    """
    Handles transitioning a position to a new position based on an action.

    :param board: GameState representation of the current game board. See class GameState
    :param position: [3x1] list of [y,x,z] coordinates
    :param action: tuple of ('action', 'dir') where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
    :return: new_pos: deep-copied new position after action
    """
    new_pos = [position[0], position[1], position[2]]
    if action[1] == 'u':
        new_pos[0] -= 1
    elif action[1] == 'd':
        new_pos[0] += 1
    elif action[1] == 'r':
        new_pos[1] += 1
    elif action[1] == 'l':
        new_pos[1] -= 1
    elif action[1] == 'ur':
        new_pos[0] -= 1
        new_pos[1] += 1
    elif action[1] == 'dr':
        new_pos[0] += 1
        new_pos[1] += 1
    elif action[1] == 'ul':
        new_pos[0] -= 1
        new_pos[1] -= 1
    elif action[1] == 'dl':
        new_pos[0] += 1
        new_pos[1] -= 1

    if 0 <= new_pos[0] < len(board[:][0]) and 0 <= new_pos[1] < len(board[0][:]):
        new_pos[2] = board[new_pos[0]][new_pos[1]][1]

    return new_pos


def check_move_validity(board, start_pos, end_pos):
    """
    Check validity of a move based on board configuration and current position.

    :param board: GameState representation of the current game board. See class GameState
    :param start_pos: [3x1] list of [y,x,z] starting coordinates
    :param end_pos: [3x1] list of [y,x,z] ending coordinates
    :return: boolean representing if move is valid or not
    """
    if end_pos[0] < 0 or end_pos[0] >= len(board[:][0]) or end_pos[1] < 0 or end_pos[1] >= len(board[0][:]):
        return False
    if abs(start_pos[0] - end_pos[0]) > 1 or abs(start_pos[1] - end_pos[1]) > 1:
        return False
    if board[end_pos[0]][end_pos[1]][0] is None \
            and int(board[end_pos[0]][end_pos[1]][1]) <= int(start_pos[2]) + 1 \
            and end_pos[0] >= 0 and end_pos[1] >= 0 and board[end_pos[0]][end_pos[1]][1] < 4:
        return True
    return False


def check_build_validity(board, player_pos, build_pos):
    """
    Check validity of a build based on board configuration and current position.

    :param board: GameState representation of the current game board. See class GameState
    :param build_pos: [3x1] list of [y,x,z] coordinates of where build is desired
    :param player_pos: [3x1] list of [y,x,z] coordinates of where player is located
    :return: boolean representing if build is valid or not
    """
    if build_pos[0] < 0 or build_pos[0] >= len(board[:][0]) or build_pos[1] < 0 or build_pos[1] >= len(board[0][:]):
        return False
    if abs(player_pos[0] - build_pos[0]) > 1 or abs(player_pos[1] - build_pos[1]) > 1:
        return False
    if build_pos[0] >= 0 and build_pos[1] >= 0 and board[build_pos[0]][build_pos[1]][1] < 4 \
            and board[build_pos[0]][build_pos[1]][0] is None:
        return True
    return False


def get_move_action_space(board, position):
    """
    Enumerates list of all valid move actions from current state

    :param board: GameState representation of the current game board. See class GameState
    :param position: [3x1] list of [y,x,z] coordinates representing current position
    :return: action_list: list of valid actions, where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
    """
    move_actions = [('move', 'u'), ('move', 'd'), ('move', 'l'), ('move', 'r'), ('move', 'ul'), ('move', 'ur'), ('move', 'dl'), ('move', 'dr')]
    action_list = []

    for action in move_actions:
        new_pos = move_logic(board, position, action)
        if check_move_validity(board, position, new_pos):
            action_list.append(action)
    return action_list


def get_build_action_space(board, position):
    """
    Enumerates list of all valid build actions from current state

    :param board: GameState representation of the current game board. See class GameState
    :param position: [3x1] list of [y,x,z] coordinates representing current position
    :param player_pos: [3x1] list of [y,x,z] coordinates of where player is located
    :return: action_list: list of valid actions, where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
    """
    build_actions = [('build', 'u'), ('build', 'd'), ('build', 'l'), ('build', 'r'), ('build', 'ul'), ('build', 'ur'), ('build', 'dl'), ('build', 'dr')]
    action_list = []

    for action in build_actions:
        new_pos = move_logic(board, position, action)
        if check_build_validity(board, position, new_pos):
            action_list.append(action)
    return action_list


def get_action_space(board, position, action_type):
    if action_type == 'move':
        return get_move_action_space(board, position)
    else:
        return get_build_action_space(board, position)


def what_is_next_turn(player_positions, agent, action_type):
    if action_type == 'move':
        next_agent = agent
        next_action = 'build'
    else:
        next_agent = (agent + 1) % len(player_positions)
        next_action = 'move'
    return next_agent, next_action


def get_all_actions(action_type):
    """
    Returns a list of all actions disregarding building/movement rules

    :param action_type: 'move' or 'build'
    :return: list of valid actions, where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
    """
    if action_type == 'move':
        return [('move', 'u'), ('move', 'd'), ('move', 'l'), ('move', 'r'), ('move', 'ul'), ('move', 'ur'), ('move', 'dl'), ('move', 'dr')]
    else:
        return [('build', 'u'), ('build', 'd'), ('build', 'l'), ('build', 'r'), ('build', 'ul'), ('build', 'ur'), ('build', 'dl'), ('build', 'dr')]


def transition(board, player_positions, action, player_number):
    """
    Function to deterministically transition from current state to next state based on the action. Returns
    deep-copies of board and position.

    :param board: GameState representation of the current game board. See class GameState
    :param player_positions: list of [x,y,z] coordinates of each player
    :param action: tuple of ('action', 'dir') where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
    :param player_number: int, representing player index
    :return: new_board: deep-copied board for next state
    :return: new_position: copied position for next state
    """

    import copy

    new_board = copy.deepcopy(board)
    new_positions = copy.deepcopy(player_positions)

    if action[0] == 'move':
        old_position = player_positions[player_number]
        new_position = move_logic(board, old_position, action)

        new_positions[player_number] = new_position
        new_board[old_position[0]][old_position[1]][0] = None
        new_board[new_position[0]][new_position[1]][0] = player_number
    else:
        build_loc = move_logic(board, player_positions[player_number], action)
        new_board[build_loc[0]][build_loc[1]][1] = board[build_loc[0]][build_loc[1]][1] + 1
    return new_board, new_positions

#_____________________________
# UI Helpers
#_____________________________
building_pixel_row = [105, 216, 331, 446, 559]
building_pixel_column = [106, 218, 333, 450, 561]
player_offset_per_level = [(20, 20),(20, 25),(35, 15),(38, 38)]

def get_tile_by_click(x, y, board):
    row = 0
    column = 0
    for i in range(5):
        if x >= building_pixel_column[i]:
            column += 1
        else:
            break
    column -=1
    for j in range(5):
        if y >= building_pixel_row[j]:
            row += 1
        else:
            break
    row -=1
    return [row, column, board[row][column][1]]

image_board = pyglet.resource.image('images/board.webp')
image_level_1 = pyglet.resource.image('images/level1_annotated.png')
image_level_2 = pyglet.resource.image('images/level2_annotated.png')
image_level_3 = pyglet.resource.image('images/level3_annotated.png')
image_level_4 = pyglet.resource.image('images/level4.png')
image_player_green = pyglet.resource.image('images/player_green.png')
image_player_blue = pyglet.resource.image('images/player_blue.png')
levels = [None, image_level_1, image_level_2, image_level_3, image_level_4]
players = [image_player_green, image_player_blue]

def print_board(board):
        spriteList = [pyglet.sprite.Sprite(img=image_board)]
        for row in range(5):
            for column in range(5):
                level = board[row][column][1]
                if level != 0:
                    sprite = sprite = pyglet.sprite.Sprite(img=levels[level])
                    sprite.y = building_pixel_row[row]
                    sprite.x = building_pixel_row[column]
                    spriteList.append(sprite)
                if board[row][column][0] != None:
                    sprite = sprite = pyglet.sprite.Sprite(img=players[board[row][column][0]])
                    sprite.y = building_pixel_row[row] + player_offset_per_level[level][0]
                    sprite.x = building_pixel_row[column] + player_offset_per_level[level][1]
                    spriteList.append(sprite)
        return spriteList