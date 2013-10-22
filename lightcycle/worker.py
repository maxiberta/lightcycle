# encoding=utf-8

from multiprocessing import Process, Queue, current_process
from Queue import Empty
import inspect


class RemoteInstance(object):

    class Timeout(Exception): pass

    class InvalidOutput(Exception): pass

    def __init__(self, klass, timeout=.1, namespace=None, *args, **kwargs):
        self.timeout = timeout
        self.qin = Queue()
        self.qout = Queue()
        self.proc = Process(target=self.worker, args=(klass, self.qout, self.qin, namespace))
        self.proc.start()

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
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
        return wrapper

    @staticmethod
    def worker(klass, input, output, namespace=None):
            if isinstance(klass, basestring):  # Received a string of code
                namespace = namespace or {}
                exec klass in namespace
                # Find the first class declared in our custom namespace
                klass = [var for var in namespace.values() if inspect.isclass(var)][0]
            print current_process(), 'Instancing %s' % klass
            instance = klass()
            for method, args, kwargs in iter(input.get, 'STOP'):
                #print current_process(), 'Calling %s(...)' % method
                result = getattr(instance, method)(*args, **kwargs)
                #print current_process(), 'Result:',result
                output.put(result)

    def terminate(self):
        self.proc.terminate()
