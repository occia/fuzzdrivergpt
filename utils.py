# -*- coding: utf-8 -*-
import sys
import time
import random

import pathos.multiprocessing
from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import Queue, Manager, Lock

# python 2 use Q
#import Queue as Q
# for python 3 use q
import queue as Q
import datetime

import tblib.pickling_support
tblib.pickling_support.install()

idxQs = []
argQs = []

def naive_interpret_func(task_idx, args):
    return 'idx: %s, args: %s' % (task_idx, args)

class ExceptionWrapper(object):
    def __init__(self, ee, info):
        self.info = info
        self.ee = ee
        __, __, self.tb = sys.exc_info()

    def re_raise(self):
        print('The error thread info: %s' % (self.info))
        print('The stack %s' % (self.ee))
        # for Python 2 use this
        #raise self.ee, None, self.tb
        # for Python 3 replace the previous line by:
        raise self.ee.with_traceback(self.tb)

#
# multiprocessing
#

def cpunum():
    return pathos.multiprocessing.cpu_count()

# debug use
def do_in_serial_with_idx(do_func, all_args, rslt_handle, share_rslt):
    task_num = len(all_args)
    if task_num == 0:
        return

    rslt_list = []

    for args in all_args:
        if share_rslt:
            do_func(0, args, Lock(), rslt_list)
        else:
            rslt_list.append(do_func(0, Lock(), args))

    rslt_handle(rslt_list)

def loop_wrapper_with_idx(wrapper_args):
    global idxQs, argQs

    lock, iQid, aQid, share_rslt, interpret_xargs_func = wrapper_args
    idxQ, argQ = idxQs[iQid], argQs[aQid]

    idx = idxQ.get()

    several_rslts = []

    print('=== worker %s starts ===' % (idx))

    start = datetime.datetime.now()

    try:
        while True:
            try:
                do_func, args = argQ.get_nowait()
                if share_rslt:
                    do_func(idx, lock, args, several_rslts)
                else:
                    several_rslts.append(do_func(idx, lock, args))
            except Q.Empty: 
                break
    except Exception as e:
        return [ ExceptionWrapper(e, interpret_xargs_func(idx, args)) ]

    end = datetime.datetime.now()
    #print("process %d handled %d tasks, exec time is %.4f s" % (idx, len(several_rslts), (end - start).total_seconds()))
    return several_rslts

def do_in_parallel_with_idx(do_func, all_args, rslt_handle, debug = False, para = None, sema = None, share_rslt=False, interpret_xargs_func=naive_interpret_func):
    task_num = len(all_args)
    if task_num == 0:
        return

    if debug:
        do_in_serial_with_idx(do_func, all_args, rslt_handle, share_rslt)
        return

    # do tasks in parallel
    cpuno = cpunum()
    if para == None:
        para = cpuno
    if task_num < para:
        para = task_num
    if para > cpuno:
        para = cpuno
    
    if sema == None:
        sema = para

    idxQ = Queue()
    for idx in range(0, para):
        idxQ.put(idx)
    idxQs.append(idxQ)
    iQid = idxQs.index(idxQ)

    # prepare wrapper args
    argQ = Queue()
    for args in all_args:
        argQ.put((do_func, args))
    argQs.append(argQ)
    aQid = argQs.index(argQ)

    # run in parallel
    manager = Manager()
    lock = manager.BoundedSemaphore(sema)
    pool = Pool(para)
    rslt_list = []

    chunk_rslt_list = pool.uimap(loop_wrapper_with_idx, para * [ (lock, iQid, aQid, share_rslt, interpret_xargs_func) ])
    for chunk_rslt in chunk_rslt_list:
        if (len(chunk_rslt) == 1) and isinstance(chunk_rslt[0], ExceptionWrapper):
            chunk_rslt[0].re_raise()
        rslt_list.extend(chunk_rslt)

    rslt_handle(rslt_list)

    pool.close()
    pool.join()
    pool.clear()

    idxQs.remove(idxQ)
    argQs.remove(argQ)

def test_do_func_with_idx(idx, args):
    if idx == 0:
        time.sleep(5)
    print("idx %d args is %s" % (idx, args))

def test_rslt_handle(rslt_list):
    return

def test():
    do_in_parallel_with_idx(test_do_func_with_idx, ['a', 'b', 'c', 'd', 'e', 'f', 'g'], test_rslt_handle, debug=False, para=2)

if __name__ == '__main__':
    test()
