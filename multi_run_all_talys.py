#!/usr/bin/env python3
import os
import pandas as pd
from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception

### CURRENTLY FORMATTED FOR RUNNING TALYS2.2!
# I have multiple different folders for different TALYS versions on my space, so they need to be interchanged directly with the filepath below
os.environ["TALYS_DIR"] = "/users/cjones38/TALYS2.2/talys" # replace with your path to the TALYS2.2 executable
ROOT_DIR = os.getcwd()

def run_talys(i,ld,gsfE,gsfM,upbend,jlm,alpha,prot):
    dir = os.path.join(ROOT_DIR, f"all_talys/i_{i}")#f"all_talys__astro/i_{i}")
    os.makedirs(dir, exist_ok=True)
    #dir=f'all_talys/i_{i}'
    #os.mkdir(dir)
    os.system(f'cp {ROOT_DIR}/Input/input {dir}/input')
    os.system(f'cp {ROOT_DIR}/Input/energies {dir}/energies')
    os.chdir(dir)
    with open('input','a') as input:
        input.write(f'ldmodel {ld}\n')
        input.write(f'strength {gsfE}\n')
        input.write(f'strengthM1 {gsfM}\n')
        input.write(f'upbend {upbend}\n')
        input.write(f'jlmomp {jlm}\n')
        input.write(f'legacy y\n')  # needs to be on for talys v 2.2; could be a choice of y or n, in which case the ranges for models below will most likely need to be expanded
        input.write(f'localomp {prot}\n')
        input.write(f'alphaomp {alpha}\n')
        #input.write(f'astro y\n')  # this flag needs to be on for the astrorate files to generate
#    os.system('talys <input> out') 
#    os.chdir('../..')
# referencing TALYS v2.2 executable via its relative path defined above to the new directory, all_talys
    #os.system("export TALYS_DIR=/users/cjones38/TALYS2.2/talys; " "/users/cjones38/TALYS2.2/talys/bin/talys < input > out")
    os.system(f'"{os.environ["TALYS_DIR"]}/bin/talys" < input > out')
    os.chdir(ROOT_DIR)

def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            i,ld,gsfE,gsfM,upbend,jlm,alpha,prot = task
            print(f'Running task {i} at {current_process().name}')
            run_talys(*task)

        except queue.Empty:

            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            i,ld,gsfE,gsfM,upbend,jlm,alpha,prot = task
            tasks_that_are_done.put('Task '+str(i) + ' is done by ' + current_process().name)
            # time.sleep(.5)
    return True

def main():
    # number_of_task = 7
    number_of_processes = 12
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    fOut='Input/combs_table.txt'
    with open(fOut, 'w') as file:
        file.write("i\tLD\tE1\tM1\tup\tJLM\talphaOMP\tlocalOMP\n")
    print("i\tLD\tE1\tM1\tup\tJLM\talphaOMP\tlocalOMP")
    i=0
    
    if os.path.exists('all_talys'):#_astro'):
        os.system('rm -rf all_talys')#_astro')
    os.mkdir('all_talys')#_astro')

    # Modify loops below based on which talys parameters will be modified. Currently set up for TALYS2.2
    with open(fOut, 'a') as file:
        for ld in [1,2,5,7]:#[1,2,4,5,6] for TALYS1.96
            for alpha in [1,2,5,6,7,8]:#[3,4,5,6] for TALYS 1.96
            	for prot in ['y','n']:
                    for gsfE in [8,9]:
                    	for gsfM in range(1,4):
                            for upbend in ['y','n']:
                      	        for jlm in ['y','n']:#was previously hardcoded as 'n' for TALYS1.96
                            	    file.write(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}\t{alpha}\t{prot}\n")
                            	    print(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}\t{alpha}\t{prot}")
                            	    task_args=(i,ld,gsfE,gsfM,upbend,jlm,alpha,prot) 
                            	    tasks_to_accomplish.put(task_args)
                            	    i+=1

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

if __name__ == '__main__':
    main()
