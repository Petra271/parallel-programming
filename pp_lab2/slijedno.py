import mpi4py
from mpi4py import MPI
from game import Game
from random import random
from collections import defaultdict
import sys
import copy
import time


def get_move(game, depth):
    best = -1
    best_col = -1
    t1 = time.time()
    while best == -1 and depth > 0:
        for col in range(1, game.cols + 1):
            if game.move_legal(col):
                if best_col == -1:
                    best_col = col
                game.move(col, Game.CPU)
                res = eval(game, Game.CPU, col, depth - 1)
                game.undo_move(col)
                if res > best or (res == best and random() > 0.5):
                    best = res
                    best_col = col
        depth //= 2
    print(time.time() - t1)
    return best_col


def eval(game, player, col, depth):
    if game.game_end(col):
        res = 1 if player == game.CPU else -1
        return res

    if depth == 0:
        return 0

    curr_player = game.HUMAN
    if player == game.HUMAN:
        curr_player = game.CPU

    depth -= 1
    moves_ct = 0
    evaluation = 0
    win_a = 1
    lose_a = 1

    for i in range(1, game.cols + 1):
        legal = game.move_legal(i)
        if legal:
            game.move(i, curr_player)
            res = eval(game, curr_player, i, depth)
            game.undo_move(i)
            if res != 1:
                win_a = 0
            if res > -1:
                lose_a = 0
            if res == 1 and curr_player == game.CPU:
                return 1
            if res == -1 and curr_player == game.HUMAN:
                return -1
            if res > 0:
                res += 0.2
            evaluation += res
            moves_ct += 1

    if win_a:
        return 1
    if lose_a:
        return -1

    evaluation /= moves_ct
    return evaluation


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    num = comm.size
    rank = comm.Get_rank()

    game = Game()
    while 1:
        depth = 7
        # covjek na potezu
        while 1:
            try:
                col = int(input("Enter column > "))
                if game.move_legal(col):
                    game.move(col, Game.HUMAN)
                    break
                raise ValueError()
            except ValueError:
                print("Input must be a number in range [1, 7].")

        print("\nBoard after HUMAN move:")
        game.print_board()
        if game.game_end(col):
            print("Game finished! (HUMAN won)")
            break

        # racunalo na potezu
        best_col = get_move(game, depth)
        game.move(best_col, Game.CPU)
        print("Board after CPU move:")
        game.print_board()
        if game.game_end(best_col):
            print("Game finished! (COMPUTER won)")
            break
