'''
ThreadPool Implementation

@author: Morten Holdflod Moeller - morten@holdflod.dk
@license: LGPL v3 

(A buggy line commented out by Kalman Tarnay...
see: http://code.google.com/p/pythonthreadpool/issues/detail?id=4 )
'''

from __future__ import with_statement
from threading import Thread, RLock
from time import sleep
from Queue import Queue, Empty
import logging

class ThreadPoolMixIn:
    """Mix-in class to handle each request in a new thread from the ThreadPool."""

    def __init__(self, threadpool=None):
        if (threadpool == None):
            threadpool = ThreadPool()
            self.__private_threadpool = True
        else:
            self.__private_threadpool = False
        
        self.__threadpool = threadpool

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.

        """
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address) #IGNORE:W0702
            self.close_request(request)

    def process_request(self, request, client_address):
        self.__threadpool.add_job(self.process_request_thread, [request, client_address])      

    def shutdown(self):
        if (self.__private_threadpool): self.__threadpool.shutdown()
        

class AddJobException(Exception):
    '''
    Exceptoion raised when a Job could not be added
    to the queue
    '''
    def __init__(self, msg):
        Exception.__init__(self, msg)
    

class ThreadPool:
    '''
    The class implementing the ThreadPool.
    
    Instantiate and add jobs using add_job(func, args_list) 
    '''

    class Job: #IGNORE:R0903
        '''
        Class encapsulating a job to be handled
        by ThreadPool workers 
        '''
        def __init__(self, function, args, return_callback=None):
            self.callable = function
            self.arguments = args
            self.return_callback = return_callback
            
        def execute(self):
            '''
            Called to execute the function
            '''
            try:
                return_value = self.callable(*self.arguments) #IGNORE:W0142
            except Exception, excep: #IGNORE:W0703
                logger = logging.getLogger("threadpool.worker")
                logger.warning("A job in the ThreadPool raised an exception: " + excep)
                #else do nothing cause we don't know what to do...
                return 
                    
            try:
                if (self.return_callback != None):
                    self.return_callback(return_value)
            except Exception, _: #IGNORE:W0703 everything could go wrong... 
                logger = logging.getLogger('threadpool')
                logger.warning('Error while delivering return value to callback function')

    class Worker(Thread):
        '''
        A worker thread handling jobs in the thread pool 
        job queue
        '''
        
        def __init__(self, pool):
            Thread.__init__(self)
            
            if (not isinstance(pool, ThreadPool)):
                raise TypeError("pool is not a ThreadPool instance")
            
            self.pool = pool
            
            self.alive = True
            self.start()
                
        def run(self):
            '''
            The workers main-loop getting jobs from queue 
            and executing them
            '''
            while self.alive:
                job = self.pool.get_job()
                if (job != None):
                    job.execute()
                else:
                    self.alive = False
                
            self.pool.punch_out()
                       
    def __init__(self, max_workers = 5, kill_workers_after = 3):
        if (not isinstance(max_workers, int)):
            raise TypeError("max_workers is not an int")
        if (max_workers < 1):
            raise ValueError('max_workers must be >= 1')
        
        if (not isinstance(kill_workers_after, int)):
            raise TypeError("kill_workers_after is not an int")
        
        self.__max_workers = max_workers
        self.__kill_workers_after = kill_workers_after
        
        # This Queue is assumed Thread Safe
        self.__jobs = Queue()
                      
        self.__active_workers_lock = RLock() 
        self.__active_workers = 0
        
        self.__shutting_down = False
        logger = logging.getLogger('threadpool')
        logger.info('started')
    
    def shutdown(self,  wait_for_workers_period = 1, clean_shutdown_reties = 5):
        if (not isinstance(clean_shutdown_reties, int)):
            raise TypeError("clean_shutdown_reties is not an int")
        if (not clean_shutdown_reties >= 0):
            raise ValueError('clean_shutdown_reties must be >= 0')
        
        if (not isinstance(wait_for_workers_period, int)):
            raise TypeError("wait_for_workers_period is not an int")
        if (not wait_for_workers_period >= 0):
            raise ValueError('wait_for_workers_period must be >= 0')
        
        logger = logging.getLogger("threadpool")
        logger.info("shutting down")
        
        with self.__active_workers_lock:
            self.__shutting_down = True
            self.__max_workers = 0
            self.__kill_workers_after = 0
        
        retries_left = clean_shutdown_reties
        while (retries_left > 0):
            
            with self.__active_workers_lock:
                logger.info("waiting for workers to shut down (%i), %i workers left"%(retries_left, self.__active_workers))
                if (self.__active_workers > 0):
                    retries_left -= 1
                else:
                    retries_left = 0
                    
                sleep(wait_for_workers_period)
        
        
        with self.__active_workers_lock:
            if (self.__active_workers > 0):
                logger.warning("shutdown stopped waiting. Still %i active workers"%self.__active_workers)
                clean_shutdown = False
            else:
                clean_shutdown = True
            
        logger.info("shutdown complete")
        
        return clean_shutdown
    
    def punch_out(self):
        '''
        Called by worker to update worker count 
        when the worker is shutting down
        '''
        with self.__active_workers_lock:
            self.__active_workers -= 1
        
    def __new_worker(self):
        '''
        Adding a new worker thread to the thread pool
        '''
        with self.__active_workers_lock:
            ThreadPool.Worker(self)
            self.__active_workers += 1
        
    def add_job(self, function, args = None, return_callback=None):
        '''
        Put new job into queue
        '''
        
        if (not callable(function)):
            raise TypeError("function is not a callable")
        if (not ( args == None or isinstance(args, list))):
            raise TypeError("args is not a list")
        if (not (return_callback == None or callable(return_callback))):
            raise TypeError("return_callback is not a callable")
                
        if (args == None):
            args = []
        
        job = ThreadPool.Job(function, args, return_callback)
        
        with self.__active_workers_lock:
            if (self.__shutting_down):
                raise AddJobException("ThreadPool is shutting down")

            try:
                start_new_worker = False
                if (self.__active_workers < self.__max_workers):
                    #DIY fixed.... FIXME
                    #http://code.google.com/p/pythonthreadpool/issues/detail?id=4
                    #if (self.__active_workers == 0 or not self.__jobs.empty()):                    
                        start_new_worker = True
                        
                self.__jobs.put(job)
                
                if (start_new_worker): 
                    self.__new_worker()
                    
            except Exception:
                raise AddJobException("Could not add job")
        
    
    def get_job(self):
        '''
        Retrieve next job from queue 
        workers die (and should) when 
        returning None  
        '''
        
        job = None
        try:
            if (self.__kill_workers_after < 0):
                job = self.__jobs.get(True)
            elif (self.__kill_workers_after == 0):
                job = self.__jobs.get(False)
            else:
                job = self.__jobs.get(True, self.__kill_workers_after)
        except Empty:
            job = None
        
        return job
