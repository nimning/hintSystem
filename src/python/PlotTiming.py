#!/usr/bin/env python

import pandas, sys
import numpy as np
import pickle
import matplotlib.pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages

class PlotTiming:
    def __init__(self,filename):
        print 'starting to load',filename
        Dict=pickle.load(open(filename,'rb'))
        self.__dict__=Dict
        print 'finished loading, loaded',self.__dict__.keys()

    def plot(self,user='',assignment='',filename='plots.pdf',legend=2):
        """
        create a plot file of a subset of the (user,assignment) pairs.
        user= restrict to plots for this user (default='' corresponds to no restriction)
        assignment= restrict to plots for this assignment (default='' corresponds to no restriction)
        filename = the name of the pdf file in which the plots are stored.
        legend = location of the legend (0=none, 1=upper right, 2=(default) upper left, 3=lower left, 4=lower right)
        """
        self.G=self.GroupedDataFrame

        keyList=sorted(self.G.keys())
        if user != '':
            keyList=[g for g in keyList if g[0]==user]
        if assignment != '':
            keyList=[g for g in keyList if g[1]==assignment]

        count=0
        pp=PdfPages(filename)

        for key in keyList:
            print 'plotting',key
            sys.stdout.flush()
            
            block=self.G[key]
            last_answer={}

            t=block['time'].values
            locs=block['break'].values
            steps=np.cumsum(np.array([(self.time_gap_threshold if l>0 else 0) for l in locs]))
            t_s=t+steps

            counter=block['counter'].values
            correct=block['correct'].values
            answer=block['answer'].values

            # index each trial into one of 6 categories: correct/incorrect, empty/same/different (than previous)
            # according to classification append element into one of 4 lists in a dictionary:
            # "correct/same","correct/different","incorrect/same","incorrect/different"

            Corr=["incorrect","correct"]
            Diff=["=","!=",""]
            _marker={'=':'_','!=':'o','':None}    # define the markers corresponding to same/different/empty
            _color ={'correct':'g','incorrect':'r'}  # define the colors corresponding to correct/incorrect

            # prepare time and part arrays for each of the 4 combinations
            time={}; part={}
            for c in Corr: 
                for d in Diff:
                    time[(c,d)]=[]; part[(c,d)]=[]

            d=block['answer_state'].values
            c=[Corr[int(correct[i])] for i in range(len(correct))]

            for i in range(len(block.index)):
                time[(c[i],d[i])].append(t_s[i])
                part[(c[i],d[i])].append(counter[i])

            # create the scatter plot
            fig=pl.figure(figsize=[15,10])
            max_counter=max(counter)
            pl.ylim((0,max_counter+1))
            center=counter[-1]/2
            minutes = int(t_s[-1]/60)
            pl.xlim((-60,minutes*60+60)) 
            # Put a minute-marking every minutes_delta minutes
            minutes_delta = 10
            pl.xticks(range(0,minutes*60,minutes_delta*60),\
                      range(0,minutes,minutes_delta))
            pl.xlabel('minutes')
            pl.ylabel('part number')
            for c in Corr: 
                for d in Diff:
                    if len(time[(c,d)])>0:
                        pl.scatter(time[(c,d)], part[(c,d)],color=_color[c]\
                                   ,marker=_marker[d],label=c+'/'+d)

            #place vertical lines where a time gap has been detected and subtracted.
            for i in range(len(t)-1):
                if locs[i+1]>0:
                    # print 'plot at x=',t_s[i]/60,' locs=',locs[i+1]/60
                    pl.axvline( x=t_s[i+1],color='b')
                    pl.axvline( x=t_s[i]+60,color='r')
                    # write the number of minutes elapsed between the two lines.
                    pl.text((t_s[i+1]+t_s[i]+5)/2, max_counter/2,\
                             ('rest of %4d minutes' % (locs[i+1]/60)),\
                             rotation='vertical',\
                             horizontalalignment = 'center',\
                             verticalalignment   = 'top',\
                             multialignment      = 'center')

            if legend>0: pl.legend(loc=legend)
            pl.title('Attempt times for %s / %s'% key)
            pp.savefig(fig)

        pp.close()


if __name__=='__main__':
    if 'WWAH_LOGS' in os.environ.keys() and 'WWAH_OUTPUT' in os.environ.keys():
        pickle_dir=os.environ['WWAH_LOGS']
        output_dir=os.environ['WWAH_OUTPUT']
        P=PlotTiming(pickle_dir+'/ProcessedLogs.pkl')
        P.plot(user='', assignment='',filename=output_dir+'/All.pdf')
    else:
        print 'source setup.sh first'
