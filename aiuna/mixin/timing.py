#import os
#import signal
#from contextlib import contextmanager

#import time


#class withTiming:
    #@staticmethod
    #def cpu():
        #"""CPU time.

        #Returns
        #-------
            #Sum of all SO times except wall time.
        #"""
        ##  return time.process_time()  # Does not include children processes.
        #t = os.times()
        #return t[0] + t[1] + t[2] + t[3]

    #@staticmethod
    #@contextmanager
    #def time():
        #start = withTiming.cpu()
        #yield
        #end = withTiming.cpu()
        #return end - start

    #@staticmethod
    #def clock():
        #"""Wall clock time.

        #Returns
        #-------
            #Ellapsed time.
        #"""
        #return time.monotonic()

    #@staticmethod
    #@contextmanager
    #def time_limit(seconds=None):
        #if seconds is None:
            #yield
        #else:
            #def signal_handler(signum, frame):
                #raise TimeoutException("Timed out!")

            #signal.signal(signal.SIGALRM, signal_handler)
            #signal.alarm(seconds)
            #try:
                #yield
            #finally:
                #signal.alarm(0)


#class TimeoutException(Exception):
    #pass
