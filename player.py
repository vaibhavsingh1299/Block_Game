"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    players = []

    num_player = num_human + num_random + len(smart_players)
    goal = generate_goals(num_player)

    for player in range(num_human):
        players.append(HumanPlayer(player, goal[player]))
    for player in range(num_human, num_human + num_random):
        players.append(RandomPlayer(player, goal[player]))
    for player in range(num_human + num_random, num_player):
        new = num_human + num_random
        players.append(SmartPlayer(player, goal[player],
                                   smart_players[player - new]))
    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    pos_1 = block.position[0]
    pos_2 = block.position[1]

    bound_1 = pos_1 + block.size
    bound_2 = pos_2 + block.size

    if pos_1 <= location[0] < bound_1 and pos_2 <= location[1] < bound_2:

        if level == block.level or block.level == block.max_depth:
            return block

        else:

            return _get_block_helper(block, location, level)

    return None


def _get_block_helper(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """
    this is a helper method to avoid 'too many nested loop' PyTA error in the
    _get_block method.
    It recurse inside the children of that block if it has any
    """
    for i in block.children:
        if _get_block(i, location, level) is not None:
            return _get_block(i, location, level)

    return None


def _random_valid_moves(block: Block, goal: Goal) -> \
        Tuple[Optional[Tuple[str, Optional[int], Block]], int]:
    """
     This is a helper functions for the generate_move methods for both Random
     Player and Smart Player that takes the player's goal a blocks then returns
     a random valid move that can be preformed on the block
    """
    temp_board = block.create_copy()

    random_level = random.randint(0, block.max_depth)
    random_position_x = random.randint(0, block.position[0] + block.size)
    random_position_y = random.randint(0, block.position[1] + block.size)

    new_block = _get_block(temp_board, (random_position_x, random_position_y),\
                           random_level)
    if new_block:
        new_block = new_block.create_copy()
    else:
        return _random_valid_moves(block, goal)

    random_move = random.randint(1, 7)

    if random_move == 1:
        if new_block.rotate(1):
            score = goal.score(temp_board)
            return _create_move(ROTATE_CLOCKWISE, new_block), score
    if random_move == 2:
        if new_block.rotate(3):
            score = goal.score(temp_board)
            return _create_move(ROTATE_COUNTER_CLOCKWISE, new_block), score
    if random_move == 3:
        if new_block.swap(0):
            score = goal.score(temp_board)
            return _create_move(SWAP_HORIZONTAL, new_block), score
    if random_move == 4:
        if new_block.swap(1):
            score = goal.score(temp_board)
            return _create_move(SWAP_VERTICAL, new_block), score
    if random_move == 5:
        if new_block.smash():
            score = goal.score(temp_board)
            return _create_move(SMASH, new_block), score
    if random_move == 6:
        if new_block.combine():
            score = goal.score(temp_board)
            return _create_move(COMBINE, new_block), score
    if random_move == 7:
        random_color = goal.colour
        if new_block.paint(random_color):
            score = goal.score(temp_board)
            return _create_move(PAINT, new_block), score

    return _random_valid_moves(block, goal)


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    === Private Attributes ===
    _level:
        The level of the Block that the user selected most recently.
    _desired_action:
        The most recent action that the user is attempting to do.

    == Representation Invariants concerning the private attributes ==
        _level >= 0
    """
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """
    A player who plays a random valid move.
     === Private Attributes ===
     _proceed:
      True when the player should make a move, False when the player should
     wait.
    """

    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None

        move = _random_valid_moves(board, self.goal)
        self._proceed = False
        return move[0]


class SmartPlayer(Player):
    """
    A player who chooses from a list of random moves to score the
    maximum possible points.

     === Private Attributes ===
     _proceed:
       True when the player should make a move, False when the player should
       wait.
    """
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False
        self._difficulty = difficulty

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        moves = []
        if not self._proceed:
            return None  # Do not remove

        for _ in range(self._difficulty):
            moves.append(_random_valid_moves(board, self.goal))

        max_score_move = self.goal.score(board)
        best_move = ()
        for move in moves:
            # checking the score of each move
            score = move[1]
            if score > max_score_move:
                max_score_move = score
                best_move = (move[0])

        current_score = self.goal.score(board)
        if max_score_move > current_score:
            return best_move
        return _create_move(PASS, board)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
