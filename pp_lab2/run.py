import os
from time import sleep

for p in range(1, 9):
    with open("res.txt", "a+") as f:
        f.write(str(p) + "\n")

    for _ in range(3):
        c = f"mpiexec -n {p} python connect4.py"
        os.system(command=c)

    with open("res.txt", "a+") as f:
        f.write("\n")
