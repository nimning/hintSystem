import pandas as pd
import pickle 
import matplotlib.pyplot as plt
import os
import shutil

def analysis(df):
    try:
        shutil.rmtree('analysis')
    except os.error:
        pass
    
    
    temp = df.groupby(['assignment','problem_no','user'],as_index=False).sum()
    tries_overall = temp.groupby(['assignment','problem_no'])['tries'].median()

    temp = df.groupby(['assignment','problem_no','user'],as_index=False).sum()
    time_overall = temp.groupby(['assignment','problem_no'])['time'].median()
    
    nr = df.groupby(['assignment','problem_no'])['final_correct'].sum()
    dr = df.groupby(['assignment','problem_no'])['final_correct'].size()
    prop_solved_overall = nr*1.0/dr
    

    users = df['user'].unique()
    for usr in users:
        os.makedirs('analysis/'+usr)

        student_data = df[df['user'] == usr]
        tries = student_data.groupby(['assignment','problem_no'])['tries'].sum()
        
        plt.clf()
        tries.hist(bins = 40,label='student')
        tries_overall.hist(bins = 40,label='class')
        plt.ylabel('Count')
        plt.xlabel('Tries')
        plt.legend(loc='best')
        plt.savefig('analysis/'+str(usr)+'/'+str(usr)+'_tries.jpg')
            
        time = student_data.groupby(['assignment','problem_no'])['time'].sum()
        
        plt.clf()       
        time.hist(bins = 40,label='student')
        time_overall.hist(bins = 40,label='class')
        plt.ylabel('Count')
        plt.xlabel('Time')    
        plt.legend(loc='best')
        plt.savefig('analysis/'+str(usr)+'/'+str(usr)+'_time.jpg')
        
        nr = student_data.groupby(['assignment','problem_no'])['final_correct'].sum()
        dr = student_data.groupby(['assignment','problem_no'])['final_correct'].size()
    
        plt.clf()
        prop_solved = nr*1.0/dr
        prop_solved.hist(bins = 40,label='student')
        prop_solved_overall.hist(bins = 40,label='class')
        plt.ylabel('Count')
        plt.xlabel('Proportion_Correct')
        plt.legend(loc='best')    
        plt.savefig('analysis/'+str(usr)+'/'+str(usr)+'_prop.jpg')
    

if __name__ == "__main__":
    f = pickle.load(open('BehavioralStatistics.pkl','r'))
    df = f.values()[0]
    analysis(df)
    

    
