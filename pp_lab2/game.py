import numpy as np
import itertools
import sys
from termcolor import colored
import time
import numpy as np
import os

class Game:
    CPU = 1
    HUMAN = 2

    def __init__(self, rows=6, cols=7):
        self._rows = rows
        self._cols = cols
        self._board = []
        self._counter = {}
        for i in range(cols):
            self._board.append([0] * rows)
            self._counter[i] = rows - 1

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    def move_legal(self, col):
        # ako stupac ne postoji ili je pun
        if col > self._cols or col < 1 or self._counter[col - 1] == -1:
            return 0
        return 1

    def move(self, col, player):
        if not self.move_legal(col):
            return 0

        self._board[col - 1][self._counter[col - 1]] = player
        self._counter[col - 1] -= 1

    def undo_move(self, col):
        # ako stupac ne postoji ili je prazan
        if col > self._cols or self._counter[col - 1] == self._rows - 1:
            return 0
        self._board[col - 1][self._counter[col - 1] + 1] = 0
        self._counter[col - 1] += 1

    def game_end(self, col):
        if col > self._cols:
            return 0
        cols = self.cols
        rows = self.rows
        col = col - 1

        row = self._counter[col]
        row = row + 1 if row < 5 else row

        player = self._board[col][row]
        board = self._board

        # vertikalno
        seq = board[col][row:]
        if len(seq) >= 4 and seq[:4].count(seq[0]) == 4:
            return 1

        # horizontalno
        board = np.array(board).T.tolist()
        seq = board[row][:]
        c = col
        ct = 0
        while (c - 1) >= 0 and board[row][c - 1] == player:
            c -= 1
        if len(seq[c:]) >= 4:
            while c < cols and board[row][c] == player:
                ct += 1
                c += 1
        if ct > 3:
            return 1

        # dijagonale
        ct = 0
        r = row
        c = col
        while (c - 1) >= 0 and (r - 1) >= 0:
            if not board[r - 1][c - 1] == player:
                break
            c -= 1
            r -= 1
        while c < cols and r < rows:
            if not board[r][c] == player:
                break
            c += 1
            r += 1
            ct += 1
        if ct > 3:
            return 1

        ct = 0
        r = row
        c = col
        while (c - 1) >= 0 and (r + 1) < rows:
            if not board[r + 1][c - 1] == player:
                break
            c -= 1
            r += 1
        while c < cols and r >= 0:
            if not board[r][c] == player:
                break
            c += 1
            r -= 1
            ct += 1
        if ct > 3:
            return 1

        return 0

    def print_board(self):
        for r in range(self._rows):
            print("| ", end="")
            for c in range(self._cols):
                if self._board[c][r] == self.CPU:
                    print(colored("C", "blue", attrs=["bold"]), end=" | ")
                elif self._board[c][r] == self.HUMAN:
                    print(colored("H", "red", attrs=["bold"]), end=" | ")
                else:
                    print(" ", end=" | ")
                sys.stdout.flush()

            print()
            print("".join(["-" for i in range(29)]))
        print()
        sys.stdout.flush()
