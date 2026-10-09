#!/usr/bin/env python3
import os
import pandas as pd
from multiprocessing import Process, Queue, current_process
import queue  # imported for using queue.Empty exception
import subprocess
import argparse

# Set False by default. For true execute script as: python3 multi_run_all_Talys.py --astro
ASTRO = False


# Currently formatted for Talys 2.2
def run_talys(i, ld, gsfE, gsfM, upbend, jlm, alpha, prot, talysDir):
    dir = f"{talysDir}/i_{i}"
    os.mkdir(dir)
    subprocess.run(["cp", "Input/input", f"{dir}/input"])
    subprocess.run(["cp", "Input/energies", f"{dir}/energies"])
    os.chdir(dir)
    with open("input", "a") as input:
        input.write(f"ldmodel {ld}\n")
        input.write(f"strength {gsfE}\n")
        input.write(f"strengthM1 {gsfM}\n")
        input.write(f"upbend {upbend}\n")
        input.write(f"jlmomp {jlm}\n")
        # input.write(f'legacy y\n')  # needs to be on for talys v 2.2; could be a choice of y or n, in which case the ranges for models below will most likely need to be expanded
        input.write(f"localomp {prot}\n")
        input.write(f"alphaomp {alpha}\n")
        if ASTRO:
            input.write(
                f"astro y\n"
            )  # this flag needs to be on for the astrorate files to generate
    subprocess.run(["talys"], stdin=open("input"), stdout=open("out", "w"))
    os.chdir("../..")


def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            """
            try to get task from the queue. get_nowait() function will
            raise queue.Empty exception if the queue is empty.
            queue(False) function would do the same task also.
            """
            task = tasks_to_accomplish.get_nowait()
            i, *_ = task
            print(f"Running task {i} at {current_process().name}")
            run_talys(*task)

        except queue.Empty:

            break
        else:
            """
            if no exception has been raised, add the task completion
            message to task_that_are_done queue
            """
            i, *_ = task
            tasks_that_are_done.put(
                "Task " + str(i) + " is done by " + current_process().name
            )
    return True


def main():
    number_of_processes = 12
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    fOut = "Input/combs_table.txt"
    with open(fOut, "w") as file:
        file.write("i\tLD\tE1\tM1\tup\tJLM\talphaOMP\tlocalOMP\n")
    print("i\tLD\tE1\tM1\tup\tJLM\talphaOMP\tlocalOMP")
    i = 0

    with open("./Input/input") as f:
        for line in f:
            if line.startswith("element"):
                el = line.split()[1]
            elif line.startswith("mass"):
                mass = int(line.split()[1])

    talysDir = f"all_talys_{mass}{el}_astro" if ASTRO else f"all_talys_{mass}{el}"
    if os.path.exists(talysDir):
        subprocess.run(["rm", "-rf", talysDir])
    os.mkdir(talysDir)

    # Modify loops below based on which talys parameters will be modified. Currently set up for TALYS2.2
    with open(fOut, "a") as file:
        # for ld in [1,2,5,7]:
        #     for alpha in [1,2,5,6,7,8]:
        #     	for prot in ['y','n']:
        #             for gsfE in [8,9,10,12,13]:
        #             	for gsfM in [3,8,10,12]:
        #                     for upbend in ['y','n']:
        #               	        for jlm in ['y','n']:
        for ld in [1, 2, 5, 7]:
            alpha = 1
            prot = "y"
            gsfE = 8
            gsfM = 3
            upbend = "y"
            jlm = "n"
            file.write(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}\t{alpha}\t{prot}\n")
            print(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}\t{alpha}\t{prot}")
            task_args = (i, ld, gsfE, gsfM, upbend, jlm, alpha, prot, talysDir)
            tasks_to_accomplish.put(task_args)
            i += 1

    for w in range(number_of_processes):
        p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--astro", action="store_true")
    ASTRO = parser.parse_args().astro
    main()
