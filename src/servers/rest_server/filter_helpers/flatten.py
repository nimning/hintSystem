from numbers import Number
def flatten(L):
    if type(L)!=list:
        #print 'not list'
        return None
    elif len(L)==1 and isinstance(L[0],Number):
        #print 'list of one number'
        return [{'val':L[0]}]
    elif len(L)==3 and type(L[0])==unicode:
        if not isinstance(L[1],Number):
            print "expected number, but got %s, in %s"%(str(L[1]),str(L))
            return None
        if type(L[2])==list:
            if len(L[2])==2:
                if type(L[2][0])==int and type(L[2][1])==int:
                    return [{'val':L[1],'location':L[2]}]
        print "expected a tuple of the form (operation,value,[start,end])"
        print "instead got "+str(L)
        return None
    else:
        #print 'general list'
        answer=[]
        for item in L:
            fitem=flatten(item)
            if fitem==None:
                return None
            answer = answer+fitem
        return answer