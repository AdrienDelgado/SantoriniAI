import copy
import math
import Util
import random

import EvalHelper

class MiniMaxAgent:
    """
    Implements a Mini-Max agent to play Santorini. Moves are given by calling self.getAction().
    Implements alpha-beta pruning. Leaf nodes are evaluated using a heuristic evaluation function in
    self.evaluation_function().
    """

    def __init__(self, config, player_number):
        self.d = config.getint('MiniMax', 'd')      # solve depth
        self.alpha = -math.inf                      # max cutoff for min action
        self.beta = math.inf                        # min cutoff for max action
        self.player_number = player_number
        self.pi = None
        self.name = config['Game']['agent_{}_name'.format(player_number)]

    def transition(self, board, player_positions, action, player_number):
        """
        Function to deterministically transition from current state to next state based on the action. Returns
        deep-copies of board and position.

        :param board: GameState representation of the current game board. See class GameState
        :param player_positions: list of [y,x,z] coordinates of each Player
        :param action: tuple of ('action', 'dir') where 'action' = {'move', 'build'} and 'dir' can be 'u', 'd', etc...
        :param player_number: int representing index of Player taking the action
        :return: new_board: deep-copied board for next state
        :return: new_position: copied position for next state
        """
        new_board = copy.deepcopy(board)
        new_positions = copy.deepcopy(player_positions)

        if action[0] == 'move':
            old_position = player_positions[player_number]
            new_position = Util.move_logic(board, old_position, action)

            new_positions[player_number] = new_position
            new_board[old_position[0]][old_position[1]][0] = None
            new_board[new_position[0]][new_position[1]][0] = player_number
        else:
            build_loc = Util.move_logic(board, player_positions[player_number], action)
            new_board[build_loc[0]][build_loc[1]][1] = board[build_loc[0]][build_loc[1]][1] + 1
        return new_board, new_positions

    def evaluation_function(self, board, player_positions):
        """
        Function to evaluate the value of a board based on heuristics ("expert" knowledge)
        """
        your_player = self.player_number

        return player_positions[your_player][2] - EvalHelper.distance_between_players(player_positions)

    def alphabeta(self, board, num_players, player_positions, alpha, beta, d_solve, agent, action_type):
        """
        Implementation of mini-max search with alpha-beta pruning.

        :param board: GameState representation of the current game board. See class GameState
        :param num_players: int representing number of Players in game
        :param player_positions: list of [y,x,z] coordinates for each Player
        :param alpha: upper-bound cutoff for min ply
        :param beta:  lower-bound cutoff for max ply
        :param d_solve: solve depth
        :param agent: int representing who's turn it is (zero indexed)
        :param action_type: string representing what type of turn it is, action_type = {'move' or 'build'}
        :return: value: value of the root node after minimax search
        :return: action: greedy action corresponding to best value at root-node
        """

        # end states
        # reaching the top level
        if player_positions[agent][2] == 3:
            if agent == self.player_number:
                return math.inf, None # this agent has won
            else:
                return -math.inf, None  # another player has won
            
        # blocking the opponent
        if len(Util.get_move_action_space(board, player_positions[agent])) == 0:
            if agent == self.player_number:
                return -math.inf, None # this agent has lost
            else:
                return math.inf, None  # another player has lost
            
        # if d_solve == 0, we have reached the max depth to look for
        if d_solve == 0:
            return self.evaluation_function(board, player_positions), None # return heuristic

        # minimizing agent
        if agent != self.player_number:
            value = math.inf
            values = []
            if action_type == 'move':
                actions = Util.get_move_action_space(board, player_positions[agent])
                random.shuffle(actions)
                next_agent = agent
                next_action = 'build'
            else:
                actions = Util.get_build_action_space(board, player_positions[agent])
                random.shuffle(actions)
                next_agent = (agent + 1) % num_players
                next_action = 'move'
            if not actions:
                return self.evaluation_function(board, player_positions), None
            for action in actions:
                new_board, new_positions = self.transition(board, player_positions, action, agent)
                value = min(value, self.alphabeta(new_board, num_players, new_positions, alpha, beta, d_solve - 1, next_agent, next_action)[0])
                values.append(value)
                if value <= alpha:
                    break
                beta = min(beta, value)
            return value, actions[values.index(value)]

        # maximizing agent
        else:
            value = -math.inf
            values = []
            if action_type == 'move':
                actions = Util.get_move_action_space(board, player_positions[agent])
                random.shuffle(actions)
                next_agent = agent
                next_action = 'build'
            else:
                actions = Util.get_build_action_space(board, player_positions[agent])
                random.shuffle(actions)
                next_agent = (agent + 1) % num_players
                next_action = 'move'
            if not actions:
                return self.evaluation_function(board, player_positions), None
            for action in actions:
                new_board, new_positions = self.transition(board, player_positions, action, agent)
                value = max(value, self.alphabeta(new_board, num_players, new_positions, alpha, beta, d_solve - 1, next_agent, next_action)[0])
                values.append(value)
                if value >= beta:
                    break
                alpha = max(alpha, value)
            return value, actions[values.index(value)]

    def getAction(self, game):
        """
        Gets best action based on minimax search with alpha-beta pruning. Essentially a wrapper function for alphabeta()

        :param game: GameState representation of the current game board. See class GameState
        :return: action: greedy action corresponding to best value at root-node
        """

        board_copy = copy.deepcopy(game.board)
        positions_copy = copy.deepcopy(game.player_positions)
        num_players = game.num_players

        v, action = self.alphabeta(board_copy, num_players, positions_copy, self.alpha, self.beta, self.d, game.turn, game.turn_type)

        all_actions = Util.get_all_actions(game.turn_type)
        self.pi = [1 if action == a else 0 for a in all_actions]

        return action
