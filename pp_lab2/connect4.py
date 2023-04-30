import mpi4py
from mpi4py import MPI
from game import Game
from random import random
from collections import defaultdict
import sys
import copy
from time import time
import math

# tag = 0 -> worker salje prijavu
# tag = 1 -> worker salje rezultate
# tag = 2 -> master salje zadatak workeru
# tag = 3 -> master salje workerima da nema vise zad
# tag = 4 -> master salje stanje workeru
# tag = 5 -> master salje workerima kraj


def get_move(comm, game, depth):
    best = -1
    best_col = -1
    evals = defaultdict(list)
    # start = time()
    while best == -1 and depth > 0:
        tasks = get_tasks(game)
        if len(tasks) == 0:
            if comm.size > 0:
                for i in range(1, comm.size):
                    comm.send("end", dest=i, tag=5)
            return -2
            break

        if comm.size > 1:
            for i in range(1, comm.size):
                comm.send(copy.deepcopy(game), dest=i, tag=4)

            # primaj rezultate i salji zadatke dok ih ima
            recvd = len(tasks)
            while recvd > 0:
                status = MPI.Status()
                data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()
                dest = status.Get_source()
                if tag == 1:
                    parent_w, result_w = data
                    recvd -= 1
                    evals[parent_w].append(result_w)
                elif tag == 0:
                    task = get_next_item(tasks)
                    if task != None:
                        comm.send(obj=task, dest=dest)

            # nema vise zadataka
            for i in range(1, comm.size):
                comm.send(obj="end", dest=i, tag=3)

            best, best_col = max_eval_value(evals, best, best_col)
        else:
            for col1, col2 in tasks:
                game.move(col1, Game.CPU)
                if game.game_end(col1):
                    game.undo_move(col1)
                    return col1
                game.move(col2, Game.HUMAN)
                evals[col1].append(eval(game, Game.HUMAN, col2, depth, -1, 1))
                game.undo_move(col2)
                game.undo_move(col1)
            best, best_col = max_eval_value(evals, best, best_col)
    return best_col


def eval(game, player, col, depth, alpha, beta):
    if game.game_end(col):
        res = 1 if player == game.CPU else -1
        return res

    if depth == 0:
        return 0

    curr_player = game.HUMAN
    if player == game.HUMAN:
        curr_player = game.CPU

    moves_ct = 0
    evaluation = 0
    win_a = 1
    lose_a = 1
    if curr_player == Game.CPU:
        res = -1
        for i in range(1, game.cols + 1):
            if game.move_legal(i):
                game.move(i, curr_player)
                new_res = max(res, eval(game, curr_player, i, depth - 1, alpha, beta))
                game.undo_move(i)
                if new_res > res:
                    res = new_res
                    if new_res != 1:
                        win_a = 0
                    if new_res > -1:
                        lose_a = 0
                    evaluation += new_res
                    moves_ct += 1
                alpha = max(alpha, res)
                if alpha >= beta:
                    break

    else:
        res = 1
        for i in range(1, game.cols + 1):
            if game.move_legal(i):
                game.move(i, curr_player)
                new_res = min(res, eval(game, curr_player, i, depth - 1, alpha, beta))
                game.undo_move(i)
                if new_res < res:
                    res = new_res
                    if new_res != 1:
                        win_a = 0
                    if new_res > -1:
                        lose_a = 0
                    evaluation += new_res
                    moves_ct += 1
                beta = min(beta, res)
                if alpha >= beta:
                    break

    if win_a:
        return 1
    if lose_a:
        return -1

    evaluation /= moves_ct
    return evaluation


def get_next_item(items):
    if len(items) == 0:
        return None
    return items.pop()


def game_finished(comm, game, col, player):
    if game.game_end(col):
        print(f"Game finished! ({player} won)")
        if comm.size > 0:
            for i in range(1, comm.size):
                comm.send("end", dest=i, tag=5)
        return 1
    return 0


def get_tasks(game):
    tasks = []
    for col1 in range(1, game.cols + 1):
        for col2 in range(1, game.cols + 1):
            if game.move_legal(col1) and game.move_legal(col2):
                tasks.append((col1, col2))
    return tasks


def max_eval_value(evals, best, best_col):
    column_value = {}
    for c, r in evals.items():
        column_value[c] = sum(r) / len(r)
    res_col = max(column_value, key=column_value.get)
    res = column_value[res_col]
    if res > best or (best == res and random() > 0.5):
        best = res
        best_col = res_col
    return best, best_col


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    num = comm.size
    rank = comm.Get_rank()
    sys.stdout.flush()

    # master
    if rank == 0:
        game = Game()
        while 1:
            depth = 5  # jer master napravi prva dva koraka i kad je sam

            # racunalo na potezu
            start = time()
            best_col = get_move(comm, game, depth)
            if best_col == -2:
                break
            end = time()
            # with open("res.txt", "a+") as f:
            #    f.write(str(end - start) + "\n")
            game.move(best_col, Game.CPU)
            print("Board after CPU move:")
            game.print_board()
            if game_finished(comm, game, best_col, "CPU"):
                break

            # covjek na potezu
            while 1:
                try:
                    col = int(input("Enter column > "))
                    if game.move_legal(col):
                        break
                    raise ValueError()
                except ValueError:
                    print("Input must be a number in range [1, 7].")

            game.move(col, Game.HUMAN)
            print("\nBoard after HUMAN move:")
            game.print_board()
            if game_finished(comm, game, col, "HUMAN"):
                break

    # worker
    else:
        status = MPI.Status()
        while 1:
            depth = 5
            rec = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            if tag == 4:
                game_w = rec
            elif tag == 5:
                break
            while 1:
                comm.send(obj="req", dest=0, tag=0)
                data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()
                # vise nema zadataka
                if tag == 3:
                    break
                col1_w, col2_w = data
                game_w.move(col1_w, Game.CPU)

                if game_w.game_end(col1_w):
                    game_w.undo_move(col1_w)
                    comm.send(obj=(col1_w, 1), dest=0, tag=1)
                else:
                    game_w.move(col2_w, Game.HUMAN)
                    res_w = eval(game_w, Game.HUMAN, col2_w, depth, -1, 1)
                    game_w.undo_move(col2_w)
                    game_w.undo_move(col1_w)
                    comm.send(obj=(col1_w, res_w), dest=0, tag=1)
