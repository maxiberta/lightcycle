# encoding=utf-8

from multiprocessing import Process, Queue, current_process
from Queue import Empty


class RemoteInstance(object):

    class Timeout(Exception): pass

    class InvalidOutput(Exception): pass

    def __init__(self, klass, timeout=.1, *args, **kwargs):
        self.timeout = timeout
        self.qin = Queue()
        self.qout = Queue()
        self.proc = Process(target=self.worker(klass, self.qout, self.qin) )
        self.proc.start()

    def __getattr__(self, name):
        def caller(*args, **kwargs):
            try:
                try:
                    #print current_process(), 'Calling %s(...)' % name
                    self.qout.put([name, args, kwargs])
                    result = self.qin.get(timeout=self.timeout)
                    #print current_process(),'RECEIVED:',result
                    return result
                except Empty:
                    # Translate Queue.Emtpy into our own exception
                    raise self.Timeout()
            except:
                self.proc.terminate()
                raise
        return caller

    @staticmethod
    def worker(klass, input, output):
        def runner():
            print current_process(), 'Instancing %s' % klass
            instance = klass()
            for method, args, kwargs in iter(input.get, 'STOP'):
                #print current_process(), 'Calling %s(...)' % method
                result = getattr(instance, method)(*args, **kwargs)
                #print current_process(), 'Result:',result
                output.put(result)
        return runner

    def terminate(self):
        self.proc.terminate()
