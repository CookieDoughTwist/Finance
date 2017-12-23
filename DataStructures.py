#import pandas
import sys
import numpy



class CircularQueue:

    i_0 = 0
    k = 0
    
    def __init__(self,n=4,default=0):        
        self.n = n
        self.arr = [default]*n    
        
    def push(self,value):
        cur_end = (self.i_0+self.k)%self.n
        self.arr[cur_end] = value
        if self.k < self.n:
            self.k += 1
        elif cur_end is self.i_0:
            self.i_0 = (self.i_0+1)%self.n
        
    def get(self,idx):
        return self.arr[(self.i_0+idx)%self.n]
    
    def mean(self):        
        return numpy.sum(self.arr)/float(self.k)        
    
    def first(self):
        return self.arr[self.i_0]
    
    def last(self):
        return self.arr[(self.i_0+self.k-1)%self.n]
    
    def __str__(self):
        out = "n=%d: [" % self.n        
        for i in range(self.k):                     
            out += "%f, " % self.get(i)            
        out += "\b\b]"
        return out
    
        
def main():
    sys.stdout.write("Testing DataStructures\n")
    sys.stdout.flush()
    dm = CircularQueue()
    dm.push(1)
    print dm.mean()
    dm.push(2)
    print dm.mean()
    dm.push(3)
    print dm.mean()
    dm.push(4)
    print dm.mean()
    dm.push(5)
    print dm.mean()
    dm.push(6)
    print dm.mean()
    print dm
    print dm.first()
    print dm.last()

    

if __name__ == "__main__":
    main()