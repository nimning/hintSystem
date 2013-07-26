import json,re
name='parts0_7'
file=open(name+'.json','r')
Objects=json.load(file)
out=open(name+'.org','w')
for part in sorted(Objects.keys()):
    Object=Objects[part]
    if u'is_clue' in Object.keys():
        # [u'answer', u'text', u'is_clue']
        print >>out,'** Hint',part
        print >>out,'** Hint Text:', Object[u'text']
        print >>out,'** Correct Answer:',Object[u'answer']
    else:
        # [u'answer', u'clusters', u'dependencies', u'centroids', u'text']
        print >>out,'* Part',part
        print >>out,'** Question:', Object[u'text']
        print >>out,'** Correct Answer:',Object[u'answer']
        # It seems that dependencies are currently empty
        print >>out,'** Dependencies:',Object[u'dependencies']
        print >>out,'** Clusters:'
        clusters = Object[u'clusters']
        for c in sorted(clusters.keys()):
            print >>out,'*** ',c,':',clusters[c]
        print >>out,'** Centroids:'
        centroids=Object[u'centroids']
        # the clusters, centroids and clues should have a common key 
        # so that the cluster is reprensented by centroid(s) 
        # and the clue is the appropriate one for those examples
        for c in centroids.keys():  
            print >>out,'*** ',centroids[c],':',c
