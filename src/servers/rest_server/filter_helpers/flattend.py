def flatten(L):
    #print 'flattening ',L,type(L),
    #if type(L)==list:
        #print 'len(L)=',len(L),'type(L[0])=',type(L[0]),
    if type(L)!=list:
        #print 'not list'
        return None
    elif len(L)==1 and type(L[0])==float:
        #print 'list of one number'
        return [{'val':L[0]}]
    elif len(L)==3 and type(L[0])==unicode:
        #print 'list of one clause'
        return [{'val':L[1],'location':L[2]}]
    else:
        #print 'general list'
        answer=[]
        for item in L:
            answer = answer+flatten(item)
        return answer
        
        
        