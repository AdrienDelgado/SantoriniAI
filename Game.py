import argparse
import ConfigHandler
import Util

import pyglet

from MiniMax import MiniMaxAgent
from HumanPlayer import HumanAgent

icon = pyglet.image.load('images/player_1.png')

class GameState(pyglet.window.Window):
    def __init__(self, config):
        super().__init__()

        self.configuration = config
        self.num_players = 2

        # players
        player_colors = ['green', 'blue']
        self.players = [Player(config, policy_type=config['Game']['agent_{}'.format(i)], player_number=i) for i in range(self.num_players)]
        self.player_names = ["{} ({})".format(config['Game']['agent_{}_name'.format(i)], player_colors[i]) for i in range(self.num_players)]
        self.player_set = set(range(self.num_players))
        self.player_positions = [None for _ in range(self.num_players)]
        self.winner = None

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
        self.set_size(768, 768)

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
    
    def update_caption(self):
        caption = "{}: {}".format(self.player_names[self.current_player], self.turn_type)
        self.set_caption(caption)

    def on_draw(self):
        self.clear()
        spriteList = Util.print_board(self.board)
        for sprite in spriteList:
            sprite.draw()
    
    def game_loop(self, dt):
        if self.player_to_place < self.num_players or self.flag == 'game_over':
            return
        
        self.update_caption()
        player = self.players[self.current_player]
        if player.policy_type == "Human":
            return
        
        if self.turn_type == "move":
            player.move(self, 0)
        else:
            player.build(self, 0)
            self.current_player = (self.current_player + 1) % self.num_players
            self.check_for_game_over()

        self.clear()
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.flag == 'game_over':
            return
        chosen_position = Util.get_tile_by_click(x, y, self.board)

        # Initial phase to choose the player positions 
        if self.player_to_place < self.num_players:
            if self.board[chosen_position[0]][chosen_position[1]][0] == None:
                position = self.players[self.player_to_place].choose_starting_position(chosen_position) # choose starting position
                self.board[position[0]][position[1]][0] = self.player_to_place # update board
                self.player_positions[self.player_to_place] = position # update internally stored position
                self.player_to_place += 1
        
        # Otherwise normal movement and build
        else:
            self.update_caption()
            if self.players[self.current_player].policy_type != "Human":
                return
            player = self.players[self.current_player]
            
            if self.turn_type == "move":
                if Util.check_move_validity(self.board, self.player_positions[player.player_number], chosen_position):
                    self.move_on_board(self.player_positions[player.player_number], chosen_position, player.player_number)
            else:
                if Util.check_build_validity(self.board, self.player_positions[player.player_number], chosen_position):
                    self.build_on_board(chosen_position)
                    self.current_player = (self.current_player + 1) % self.num_players
                    self.check_for_game_over()

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
        Util.print_board(self.board)
        print("{}:\n - Move from {} to {}".format(self.player_names[player_number], old_position, new_position))
        self.turn_type = 'build' # next turn type is build after a move
        self.check_for_game_over()

    def build_on_board(self, build_position):
        """
        Updates the game board to reflect a build action.

        :param build_position: [3x1] list of [y,x,z] coordinates representing the desired build location
        """
        self.board[build_position[0]][build_position[1]][1] = self.board[build_position[0]][build_position[1]][1] + 1
        Util.print_board(self.board)
        self.turn = (self.turn + 1) % self.num_players # switch to next player's turn after a build
        print(" - Build on {}".format(build_position))
        self.turn_type = 'move' # next turn type is move after a build
    
    def check_for_game_over(self):
        """
        Checks positions of each player and determines if a game_over state has been reached. This could be due to a
        player reaching a height of 3, or a player running out of valid moves.
        """

        for player_number, position in enumerate(self.player_positions):
            # if player_number not in self.losers:
            # check if a player has reached a height of 3 (win condition)
            if self.board[position[0]][position[1]][1] == 3:
                self.flag = 'game_over'
                self.winner = player_number
                self.set_caption("{} wins by reaching the top!".format(self.player_names[player_number]))
                print("{} wins by reaching the top!".format(self.player_names[player_number]))
                return
            # check if a player doesn't have any valid moves (that player loses)
            if not Util.get_move_action_space(self.board, position) and \
                self.turn_type == "move" and \
                self.current_player == player_number:

                self.flag = 'game_over'
                self.winner = (player_number + 1) % self.num_players
                self.set_caption("{} wins by KO!".format(self.player_names[self.winner]))
                print("{} wins by KO!".format(self.player_names[self.winner]))
                return
        return
    

class Player:
    """
    Implements an Opponent to play Santorini against. Uses one of the various Agent implementations such as FS or
    MiniMax to generate moves.
    """
    def __init__(self, config, policy_type="Human", player_number=0):
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
    pyglet.clock.schedule_interval(game.game_loop, 1/5.0)
    pyglet.app.run()

if __name__ == '__main__':
    main()
