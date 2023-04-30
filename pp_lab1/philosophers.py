import mpi4py
import random
from time import sleep
from mpi4py import MPI
import sys

# tag 1 -> zahtjev, tag 2 -> odgovor


class Philospher:
    def __init__(self, rank):
        self._rank = rank
        # 0 nema vilicu, 1 ima prljavu, 2 ima čistu
        self._left_fork = 0
        self._right_fork = 0
        self._left_rank = None
        self._right_rank = None
        self._requests = {"L": 0, "R": 0}

    @property
    def left_fork(self):
        return self._left_fork

    @left_fork.setter
    def left_fork(self, value):
        self._left_fork = value

    @property
    def right_fork(self):
        return self._right_fork

    @right_fork.setter
    def right_fork(self, value):
        self._right_fork = value

    @property
    def left_rank(self):
        return self._left_rank

    @left_rank.setter
    def left_rank(self, value):
        self._left_rank = value

    @property
    def right_rank(self):
        return self._right_rank

    @right_rank.setter
    def right_rank(self, value):
        self._right_rank = value

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value

    @property
    def requests(self):
        return self._requests


def process(comm, phil: Philospher):
    think(comm, phil)
    request(comm, phil)
    eat(comm, phil)


def think(comm, phil):
    print_flush("mislim", phil.rank)
    sec = random.randint(3, 5)

    for i in range(sec):
        status = MPI.Status()
        # provjeri ima li zahtjeva i odgovori ako ima
        check_request(phil, rank="left_rank", status=status, index="L")
        check_request(phil, rank="right_rank", status=status, index="R")
        sleep(1)


def request(comm, phil):
    while phil.left_fork == 0 or phil.right_fork == 0:
        # zatrazi vilicu
        waiting = 1
        if phil.left_fork == 0:
            dest = phil.left_rank
            L_or_R = 1
            print_flush(f"trazim L", phil.rank)
        elif phil.right_fork == 0:
            dest = phil.right_rank
            L_or_R = 2
            print_flush(f"trazim R", phil.rank)

        comm.send(obj=L_or_R, dest=dest, tag=1)

        while waiting:
            status = MPI.Status()
            message = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            src = status.Get_source()

            if tag == 2:  # je li došla zatražena vilica
                if src == phil.left_rank and L_or_R == 1:
                    print_flush(f"dobio sam L", phil.rank)
                    phil.left_fork = message
                elif src == phil.right_rank and L_or_R == 2:
                    print_flush(f"dobio sam R", phil.rank)
                    phil.right_fork = message

                waiting = 0

            elif tag == 1:  # ili netko traži vilicu
                if src == phil.left_rank:
                    if phil.left_fork == 2:  # imam čistu vilicu, pa pamtim zahtjev
                        phil.requests["L"] = 1
                    # imam prljavu vilicu, pa ju šaljem
                    elif phil.left_fork == 1 and message == 2:
                        send_fork(phil, fork="left_fork", rank="left_rank", index="L")
                        phil.requests["L"] = 0
                    else:  # nemam vilicu, pa pamtim zahtjev
                        phil.requests["L"] = 1

                elif src == phil.right_rank:
                    if phil.right_fork == 2:
                        phil.requests["R"] = 1
                    elif phil.right_fork == 1 and message == 1:
                        send_fork(phil, fork="right_fork", rank="right_rank", index="R")
                        phil.requests["R"] = 0
                    else:
                        phil.requests["R"] = 1


def eat(comm, phil):
    print_flush("jedem", phil.rank)
    sleep(random.randint(3, 7))
    phil.left_fork = 1
    phil.right_fork = 1

    for neighbor, req in phil.requests.items():
        if req:
            fork = "left_fork" if neighbor == "L" else "right_fork"
            rank = "left_rank" if neighbor == "L" else "right_rank"
            send_fork(phil, fork=fork, rank=rank, index=neighbor)
        phil.requests[neighbor] = 0


def send_fork(phil, fork, rank, index, tag=2):
    setattr(phil, fork, 2)
    comm.send(obj=getattr(phil, fork), dest=getattr(phil, rank), tag=2)
    setattr(phil, fork, 0)


def check_request(phil, rank, status, index):
    if comm.Iprobe(source=getattr(phil, rank), tag=1, status=status):
        request = comm.recv(source=getattr(phil, rank), tag=1)
        fork = "left_fork" if request == 2 else "right_fork"
        rank = "left_rank" if request == 2 else "right_rank"
        send_fork(phil, fork=fork, rank=rank, index=index)


def print_flush(output, rank):
    print("\t" * 3 * rank + f"({rank}) {output}")
    sys.stdout.flush()


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    num = comm.size

    if num < 2:
        print("Moraju biti barem 2 filozofa.")
        exit()
    rank = comm.Get_rank()
    philosopher = Philospher(rank)

    # na pocetku nulti ima dvije vilice, zadnji 0, ostali po jednu, sve su prljave
    if rank == 0:
        philosopher.left_fork = 1
    if rank != num - 1:
        philosopher.right_fork = 1

    philosopher.left_rank = (rank - 1) % num
    philosopher.right_rank = (rank + 1) % num

    while True:
        process(comm, philosopher)
