import os
import pandas as pd
from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception

def run_talys(i,ld,gsfE,gsfM,upbend,jlm):
    dir=f'all_talys/i_{i}'
    os.mkdir(dir)
    os.system(f'cp Input/input {dir}/input')
    os.system(f'cp Input/energies {dir}/energies')
    os.chdir(dir)
    with open('input','a') as input:
        input.write(f'ldmodel {ld}\n')
        input.write(f'strength {gsfE}\n')
        input.write(f'strengthM1 {gsfM}\n')
        input.write(f'upbend {upbend}\n')
        input.write(f'jlmomp {jlm}\n')
    os.system('talys <input> out')
    os.chdir('../..')
    

def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            i,ld,gsfE,gsfM,upbend,jlm = task
            print(f'Running task {i} at {current_process().name}')
            run_talys(*task)

        except queue.Empty:

            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            i,ld,gsfE,gsfM,upbend,jlm = task
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
        file.write("i\tLD\tE1\tM1\tup\tJLM\n")
    print("i\tLD\tE1\tM1\tup\tJLM")
    i=0
    
    if os.path.exists('all_talys'):
        os.system('rm -rf all_talys')
    os.mkdir('all_talys')

    # Modify loops below based on which talys parameters will be modified. Current setup was using talys 1.96
    with open(fOut, 'a') as file:
        for ld in [1,2,5,6]:  
            for gsfE in [8,9]:
                for gsfM in range(1,4):
                    for upbend in ['y','n']:
                        # for jlm in ['y','n']:
                        jlm = 'n'
                        file.write(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}\n")
                        print(f"{i}\t{ld}\t{gsfE}\t{gsfM}\t{upbend}\t{jlm}")
                        task_args=(i,ld,gsfE,gsfM,upbend,jlm) 
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