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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    goal_lst = []
    colour_lst = []

    num = len(COLOUR_LIST) - 1
    rand = random.randint(0, 1)

    if rand == 1:
        while len(goal_lst) < num_goals:
            new = COLOUR_LIST[random.randint(0, num)]
            if not colour_lst.__contains__(new):
                colour_lst.append(new)
                goal_lst.append(PerimeterGoal(new))
    while len(goal_lst) < num_goals:
        x = COLOUR_LIST[random.randint(0, num)]
        if not colour_lst.__contains__(x):
            colour_lst.append(x)
            goal_lst.append(BlobGoal(x))
    return goal_lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    two_d = []
    dimension = 2 ** (block.max_depth - block.level)

    if not block.children:
        for _ in range(dimension):
            dim_lst = []
            for __ in range(dimension):
                dim_lst.append(block.colour)
            two_d.append(dim_lst)
        return two_d
    else:
        f1 = _flatten(block.children[0])
        f2 = _flatten(block.children[1])
        f3 = _flatten(block.children[2])
        f4 = _flatten(block.children[3])
        for flat in range(len(f2)):
            f2[flat].extend(f3[flat])
            f1[flat].extend(f4[flat])
        f2.extend(f1)
        return f2


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """
    A type of goal in which the player must aim to put the most possible units
    of a given colour 'c' on the outer perimeter of the board. The player’s
    score is the total number of unit cells of colour c that are on
    the perimeter.

    ===Attributes===
        colour: The target colour for this goal, that is the colour to which
        this goal applies.
    """

    def score(self, board: Block) -> int:
        total = 0
        new_board = _flatten(board)
        size = range(len(new_board))

        for count in size:
            if new_board[count][0] is self.colour:
                total += 1

        for count in size:
            if new_board[count][len(new_board[0]) - 1] is self.colour:
                total += 1

        for count in new_board[0]:
            if count == self.colour:
                total += 1

        for count in new_board[len(new_board) - 1]:
            if count == self.colour:
                total += 1

        return total

    def description(self) -> str:
        statement = 'Achieve squares of' + colour_name(self.colour) + \
                    'to touch the perimeter of the board.'
        return statement


class BlobGoal(Goal):
    """
        A type of goal in which the player must aim  for the largest "blob" of a
        given colour. The player's score is the number of unit cells in
        the largest blob of colour c.

        ===Attributes===
        colour: The target colour for this goal, that is the colour to which
            this goal applies.
    """

    def score(self, board: Block) -> int:

        temp_lst = []
        new_board = _flatten(board)
        num = range(len(new_board))
        total = 0

        for _ in num:
            row = []

            for _ in num:
                row.append(-1)

            temp_lst.append(row)

        for pos_1 in num:
            for pos_2 in num:

                target = (pos_1, pos_2)
                new_target = self._undiscovered_blob_size(target,\
                                                          new_board, temp_lst)

                if new_target > total:
                    total = new_target

        return total

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        count = len(board)

        if pos[0] >= count or pos[1] >= count:
            return 0

        if visited[pos[0]][pos[1]] == 1 or visited[pos[0]][pos[1]] == 0:
            return 0

        if board[pos[0]][pos[1]] is not self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0

        visited[pos[0]][pos[1]] = 1

        top = self._undiscovered_blob_size((pos[0], pos[1] - 1),\
                                           board, visited)

        bottom = self._undiscovered_blob_size((pos[0], pos[1] + 1),\
                                              board, visited)

        right = self._undiscovered_blob_size((pos[0] + 1, pos[1]),\
                                             board, visited)

        left = self._undiscovered_blob_size((pos[0] - 1, pos[1]),\
                                            board, visited)

        total = 1 + top + bottom + right + left
        return total

    def description(self) -> str:
        statement = 'Biggest group of blobs of' + colour_name(self.colour)
        return statement


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
