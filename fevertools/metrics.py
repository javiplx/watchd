
import array
import math
import time

def recv( sock , buffsize=1024 ) :
    data = sock.recv(buffsize)
    while data.find(' ') < 0 :
        data += sock.recv(buffsize)
    size = data.split()[0]
    if size == '-1' :
      size = 0
    size = int(size) + 2 # Add header and trailing newline
    while len(data.split('\n')) < size :
        while data[-1] != "\n" :
            data += sock.recv(buffsize)
        if len(data.split('\n')) < size :
            data += sock.recv(buffsize)
    items = data.split('\n')
    items.pop() # Remove trailing endline
    response_size , status_line = items.pop(0).split(None, 1)
    if size == 2 :
        if response_size == '-1' :
            print "ERROR : %s" % status_line
        return status_line
    elif size == 3 :
        return items[0]
    return items

class cpu ( dict ) :

    busy = ('system', 'user', 'nice', 'wait', 'interrupt', 'softirq')
    types = ('system', 'user', 'nice', 'wait', 'idle', 'interrupt', 'softirq', 'steal')

    def __init__ ( self ) :
        dict.__init__( self )
        for attr in self.types :
            self[attr] = float('nan')

    def summary ( self ) :
        return sum([self[v] for v in self.busy]) , self['idle'] , self['steal']

    def dump ( self ) :
        return "%5.2f %5.2f %5.2f" % self.summary()

    def __str__ ( self ) :
        return " ".join( [ "%5.2f" % self[k] for k in self.types ] )

class aggregated_metric ( dict ) :

    def __init__ ( self , minsize=5 , length=10 ) :
        self.tstamp = None
        self.minsize = minsize
        self.length = length
        dict.__init__( self )

    def unshift ( self ) :
        keys = self.keys()
        keys.sort()
        keys.reverse()
        return dict.pop(self, keys.pop())

    def __setitem__ ( self , key , value ) :
        if not self.has_key(key) :
            dict.__setitem__( self , key , [] )
        self.tstamp = key
        self[self.tstamp].append( value )
        if len(self) > self.length :
            self.unshift()

    def full ( self ) :
        return len(self) > self.minsize

    def last ( self , interval=0 ) :
        if not interval :
            return array.array( 'f' , self[self.tstamp] )
        elif interval < 0 :
            return [ i for k in self.keys() for i in self[k] ]
        tstamp = time.time() - interval
        return array.array( 'f' , [ i for k in self.keys() for i in self[k] if k > tstamp ] )

    def mean ( self , interval=0 ) :
        data = self.last(interval)
        n = len(data)
        mean = sum(data) / n
        data2 = [ v*v for v in data ]
        sd  = math.sqrt( sum(data2) / n - mean*mean )
        return mean , sd

    def __str__ ( self ) :
        return "size: %d\n%s" % ( len(self) , "\n".join( [ "%s %s" % ( k , self[k] ) for k in self.keys() ] ) )

