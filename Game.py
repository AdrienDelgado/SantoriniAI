import argparse
import ConfigHandler
import Util

import pyglet
from pyglet.window import mouse
from pyglet.graphics import Group

from poubelle.FS import FSAgent
from poubelle.Random import RandomAgent
from MiniMax import MiniMaxAgent
from HumanPlayer import HumanAgent
from poubelle.NN import NNAgent

#__________________________________
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
#__________________________________

image_board = pyglet.resource.image('images/board.webp')
image_level_1 = pyglet.resource.image('images/level1_annotated.png')
image_level_2 = pyglet.resource.image('images/level2_annotated.png')
image_level_3 = pyglet.resource.image('images/level3_annotated.png')
image_level_4 = pyglet.resource.image('images/level4.png')
image_player_green = pyglet.resource.image('images/player_green.png')
image_player_blue = pyglet.resource.image('images/player_blue.png')
icon = pyglet.image.load('images/player_1.png')
levels = [None, image_level_1, image_level_2, image_level_3, image_level_4]
players = [image_player_green, image_player_blue]

class GameState(pyglet.window.Window):
    def __init__(self, config):
        super().__init__()

        self.configuration = config
        self.num_players = self.configuration.getint('Game', 'num_players')
        self.num_players = 2

        # players
        self.players = [Player(config, policy_type=config['Game']['agent_{}'.format(i)], player_number=i) for i in range(config.getint('Game', 'num_players'))]
        self.player_set = set(range(self.num_players))
        self.player_positions = [None for _ in range(self.num_players)]
        self.winner = None
        self.losers = set()

        # board
        self.board = [[[None, 0] for i in range(5)] for j in range(5)]

        # state
        self.flag = None # flag to keep track of game over state
        self.turn = 0 # [int] index that keeps track of whose turn it is
        self.turn_type = "move" # [string] what type of turn, 'move' or 'build'
        self.player_to_place = 0 # index of the next player to place on the board
        self.current_player = 0 # index of the next player to play

        # UI
        self.set_caption("Place the players")
        self.set_icon(icon)
        self.set_size(image_board.width, image_board.height)

    def start_game(self, players):
        """
        Initializes the game.
        """
        self.turn_type = 'move' # start with move turn
        self.turn = 0 # start with player 0
        for player_number, player in enumerate(players):
            position = player.choose_starting_position(self.board) # choose starting position
            self.board[position[0]][position[1]][0] = player_number # update board
            self.player_positions[player_number] = position # update internally stored position

    def print_board(self):
        spriteList = [pyglet.sprite.Sprite(img=image_board)]
        for row in range(5):
            for column in range(5):
                level = self.board[row][column][1]
                if level != 0:
                    sprite = sprite = pyglet.sprite.Sprite(img=levels[level])
                    sprite.y = building_pixel_row[row]
                    sprite.x = building_pixel_row[column]
                    spriteList.append(sprite)
                if self.board[row][column][0] != None:
                    sprite = sprite = pyglet.sprite.Sprite(img=players[self.board[row][column][0]])
                    sprite.y = building_pixel_row[row] + player_offset_per_level[level][0]
                    sprite.x = building_pixel_row[column] + player_offset_per_level[level][1]
                    spriteList.append(sprite)
        return spriteList
    
    def update_caption(self):
        if self.current_player == 0:
            player = "Green player"
        else:
            player = "Blue player"
        caption = "{}: {}".format(player, self.turn_type)
        self.set_caption(caption)

    def on_draw(self):
        self.clear()
        spriteList = self.print_board()
        for sprite in spriteList:
            sprite.draw()
    
    def game_loop(self, dt):
        if self.player_to_place < self.num_players or self.flag == 'game_over':
            return
        
        self.update_caption()
        player = self.players[self.current_player]
        if player.policy_type == "Human":
            return
        
        if player.player_number in self.losers:
            self.current_player = (self.current_player + 1) % self.num_players
        else:
            if self.turn_type == "move":
                player.move(self, 0)
            else:
                player.build(self, 0)
                self.current_player = (self.current_player + 1) % self.num_players

        self.clear()
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.flag == 'game_over':
            return
        chosen_position = get_tile_by_click(x, y, self.board)
        if self.player_to_place < self.num_players:
            if self.board[chosen_position[0]][chosen_position[1]][0] == None:
                position = self.players[self.player_to_place].choose_starting_position(chosen_position) # choose starting position
                self.board[position[0]][position[1]][0] = self.player_to_place # update board
                self.player_positions[self.player_to_place] = position # update internally stored position
                self.player_to_place += 1
        else:
            self.update_caption()
            if self.players[self.current_player].policy_type != "Human":
                return
            print("click on x:" + str(x) + " y:" + str(y))
            player = self.players[self.current_player]
            if player.player_number in self.losers:
                self.current_player = (self.current_player + 1) % self.num_players
            
            if self.turn_type == "move":
                if Util.check_move_validity(self.board, self.player_positions[player.player_number], chosen_position):
                    self.move_on_board(self.player_positions[player.player_number], chosen_position, player.player_number)
            else:
                if Util.check_build_validity(self.board, self.player_positions[player.player_number], chosen_position):
                    self.build_on_board(chosen_position)
                    self.current_player = (self.current_player + 1) % self.num_players

        self.clear()

    
    def move_on_board(self, old_position, new_position, player_number):
        """
        Updates the game board to reflect a movement action.

        :param old_position: [3x1] list of [y,x,z] coordinates representing old position on board
        :param new_position: [3x1] list of [y,x,z] coordinates representing new position on board
        :param player_number: int associated with current player
        """
        self.board[old_position[0]][old_position[1]][0] = None
        self.board[new_position[0]][new_position[1]][0] = player_number
        self.player_positions[player_number] = new_position # update internally stored position
        self.print_board()
        self.turn_type = 'build' # next turn type is build after a move
        self.check_for_game_over()

    def build_on_board(self, build_position):
        """
        Updates the game board to reflect a build action.

        :param build_position: [3x1] list of [y,x,z] coordinates representing the desired build location
        """
        self.board[build_position[0]][build_position[1]][1] = self.board[build_position[0]][build_position[1]][1] + 1
        self.print_board()
        self.turn = (self.turn + 1) % self.num_players # switch to next player's turn after a build
        self.turn_type = 'move' # next turn type is move after a build
        self.check_for_game_over()
    
    def check_for_game_over(self):
        """
        Checks positions of each player and determines if a game_over state has been reached. This could be due to a
        player reaching a height of 3, or a player running out of valid moves.
        """

        for player_number, position in enumerate(self.player_positions):
            if player_number not in self.losers:
                # check if a player has reached a height of 3 (win condition)
                if self.board[position[0]][position[1]][1] == 3:
                    self.flag = 'game_over'
                    self.winner = player_number
                    self.losers = self.player_set - {self.winner}
                    self.set_caption("Player {} wins!".format(player_number))
                    return
                # check if a player doesn't have any valid moves (that player loses)
                if not Util.get_move_action_space(self.board, position) or \
                   not Util.get_build_action_space(self.board, position):

                    self.losers.add(player_number)
                    self.board[position[0]][position[1]][0] = None
                    self.player_positions[player_number] = None

                    # if every player but 1 has lost, game is now over
                    if len(self.losers) == self.num_players - 1:
                        self.flag = 'game_over'
                        self.winner = (self.player_set - self.losers).pop() # use Set diff operation to find winner
                        self.set_caption("Player {} wins!".format(player_number))
                        return
                    else:
                        self.set_caption("Player {} loses!".format(player_number))
        return
    

class Player:
    """
    Implements an Opponent to play Santorini against. Uses one of the various Agent implementations such as FS or
    MiniMax to generate moves.
    """
    def __init__(self, config, policy_type="Random", player_number=0):
        self.policy_type = policy_type
        self.player_number = player_number
        print(policy_type)

        # chose policy Agent
        if policy_type == 'MiniMax':
            self.Agent = MiniMaxAgent(config, self.player_number)
        elif policy_type == 'Human':
            self.Agent = HumanAgent(config, self.player_number)
        else:
            raise Exception("Invalid Agent selection '{}' for player {}!".format(policy_type, player_number))

    def choose_starting_position(self, position):

        """
        Function to choose a starting position on the board. Is called once during Game.start_game().
        This is a wrapper function for an Agent's specific choose_starting_positon() member function

        :param board: GameState representation of the current game board. See class GameState
        :return: starting_position: a [3x1] List of [x, y, z] coordinates representing starting position
        """
        return [position[0], position[1], 0]

    def move(self, game, position):
        """
        Execute a move turn for opponent. Chooses action generated by the policy Agent.
        :param game: GameState representation of the current game board. See class GameState
        """
        old_position = game.player_positions[self.player_number].copy()
        action = self.Agent.getAction(game) # get action from Agent
        new_position = Util.move_logic(game.board, old_position, action)
        game.move_on_board(old_position, new_position, self.player_number)

    def build(self, game, position):
        """
        Execute a build turn for opponent. Chooses action generated by the policy Agent.
        :param game: GameState representation of the current game board. See class GameState
        """
        position = game.player_positions[self.player_number].copy()
        action = self.Agent.getAction(game)
        build_location = Util.move_logic(game.board, position, action)
        game.build_on_board(build_location)

def main():
    """
    Runs a game of Santorini with an AI adversary.
    """
    # parse command-line inputs (these will override config.ini settings)
    parser = argparse.ArgumentParser()
    parser.add_argument("--green_player", type=str, help="Choose the type of green player", choices=['Human', 'MiniMax'])
    parser.add_argument("--blue_player", type=str, help="Choose the type of blue player", choices=['Human', 'MiniMax'])
    args = parser.parse_args()

    # load in config file
    config = ConfigHandler.read_config('config/simple.ini')

    if args.green_player is not None:
        config['Game']['agent_0'] = str(args.green_player)
    if args.blue_player is not None:
        config['Game']['agent_1'] = str(args.blue_player)
    
    game = GameState(config=config)
    pyglet.clock.schedule_interval(game.game_loop, 1/60.0)
    pyglet.app.run()

if __name__ == '__main__':
    main()
