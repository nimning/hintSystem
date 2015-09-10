import pandas as pd
import pickle 
import matplotlib.pyplot as plt
import os
import shutil
import numpy as np
from scipy.linalg import svd
from sklearn.decomposition import pca
from numpy.linalg import norm
from scipy.stats.mstats import mquantiles

def compute_grouped_stats(df):
    G = df.groupby(['assignment','problem_no'],as_index=False)
    df2 = G['tries'].median()
    df2['time'] = G['time'].median()['time']
    df2['n_correct'] = G['final_correct'].sum()['final_correct']
    return df2

def list_to_hash(l):
    return dict((value,i) for i,value in enumerate(l))   

lower_final_correct_threshold=200
middle_final_correct_threshold=270
time_upper_threshold = 2000
tries_upper_threshold = 1600
user_attempts_lower_threshold = 130
part_attempts_lower_threshold = 60

generate_plots = False

if __name__ == "__main__":
    f = pickle.load(open('BehavioralStatistics.pkl','r'))
    df = f.values()[0]
    G = df.groupby(['assignment', 'problem_no', 'part_no']) 
   
    if generate_plots: 
        s = df.groupby('user', as_index=False).sum()
    
        plt.clf()
        s[['time','final_correct','tries']].hist(bins=40)
        plt.title('All Students')
        plt.savefig('overall.svg')
        
        struggling = s[s['final_correct'] < lower_final_correct_threshold]
        plt.clf()
        struggling[['time','final_correct','tries']].hist(bins=40)
        plt.title('Struggling Students')
        plt.savefig('struggling.svg')
        print 'Struggling users:'
        print struggling['user'].values
        
        middle = s[(s['final_correct'] > lower_final_correct_threshold) 
            & (s['final_correct'] < middle_final_correct_threshold)]
        plt.clf()
        middle[['time','final_correct','tries']].hist(bins=40)
        plt.title('Middle Students by final_correct')
        plt.savefig('middle.svg')
        print 'Middle users who spent a lot of time:'
        print middle[middle['time'] > time_upper_threshold]['user'].values
    
        print 'Middle users who made a lot of attempts:'
        print middle[middle['tries'] > time_upper_threshold]['user'].values
    
        plt.clf()
        plt.scatter(s['time'], s['tries'])
        plt.xlabel('time')
        plt.ylabel('tries')
        plt.title('Tries vs. Time')
        plt.savefig('tries_vs_time.svg')
    
        plt.clf()
        plt.scatter(s['time'], s['final_correct'])
        plt.xlabel('time')
        plt.ylabel('final_correct')
        plt.title('Correct vs. Time')
        plt.savefig('correct_vs_time.svg')
        
        plt.clf()
        plt.scatter(s['tries'], s['final_correct'])
        plt.xlabel('tries')
        plt.ylabel('final_correct')
        plt.title('Correct vs. Tries')
        plt.savefig('correct_vs_tries.svg')
    
        plt.clf()
        plt.hist(G.size().values, bins=40)
        plt.title('Number of attempts by part')
        plt.xlabel('Number of attempts')
        plt.ylabel('Number of parts in bin')
        plt.savefig('part_attempts.svg')
        plt.clf()
        plt.hist(df.groupby('user').size().values, bins=40)
        plt.title('Number of attempts by user')
        plt.xlabel('Number of attempts')
        plt.ylabel('Number of users in bin')
        plt.savefig('user_attempts.svg')
    
    # Reduce the dimensionality of the time/tries/final_correct user/part
    #      matrices through an SVD
    # We can't filter a groupby due to a pandas error :(
    #       https://github.com/pydata/pandas/issues/4447

    users = [user for user,count in 
        df.groupby('user').size().iteritems() if count > user_attempts_lower_threshold]
    user_hash = list_to_hash(users)
    user_set = set(users)
    parts = [part for part,count in 
        G.size().iteritems() if count > part_attempts_lower_threshold]
    part_hash = list_to_hash(parts)
    # user_part_times is a 0/1 logical array identifying the entries 
    # that are legit.
    user_part_times = np.zeros(shape=(len(parts), len(users)))
    for i,part in enumerate(parts):
        g = G.get_group(part)
        for _,row in g.iterrows():
            if not row['user'] in user_set:
               continue
            user_part_times[i,user_hash[row['user']]] = row['final_correct']
    X = user_part_times

X = X.T

exit(1)

# Remove top 10% of times- these are outliers
X_flattened = np.hstack(X)
q = mquantiles(X_flattened, 0.9)
X[X > q] = q

######### PCA
(m,n) = X.shape
M = X.mean(axis=0)*np.ones(shape=(1,n))
X2 = X - M
(U,S,V) = svd(X2)
print sum(S[:3])/sum(S)

#S[20:] = 0
#S_diag = np.zeros(m,n)
#for i,s in S:
#    S_diag[i,i] = s
#S_diag = np.concatenate([np.diag(S), np.zeros(shape=(n-m,n))],axis=0)
#print norm(X2 - np.dot(np.dot(U,S_diag), V))

######### PCA using scikit-learn
#model = pca.PCA(n_components=20)
#T = model.fit_transform(X)
#M = np.reshape(model.mean_, (1,n))
#print norm(X - (T.dot(model.components_) + np.ones(shape=(m,1)).dot(M) ) )

G = df.groupby('user', as_index=False)[['time','tries']].sum()
