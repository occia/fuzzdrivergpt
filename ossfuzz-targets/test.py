import multiprocessing
def task():
    from time import sleep
    print("hahahaha")
    sleep(100)
p = multiprocessing.Process(target=task)
p.start()
print(1)
p.join()
