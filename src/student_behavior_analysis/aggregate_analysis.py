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
from sklearn.cluster import KMeans
from collections import defaultdict
import matplotlib.cm as cm

def k_outlier_space(k,outliers,series):
    return k*(series.shape[1]) + outliers*(series.shape[0])

def remove_outliers(model, X, max_outliers=10):
    ''' Given a kmeans model, remove <max_outliers> column outliers per row
        Return the X with outliers replace with interpolated values '''
    X = np.copy(X)
    for i in range(X.shape[0]):
        prediction = model.cluster_centers_[model.labels_[i],:]
        if max_outliers > 0:
            for j in np.argsort((prediction - X[i,:])**2)[-1*max_outliers:]:
                X[i,j] = prediction[j]
    return X

def compute_kmeans_err(model, series, max_outliers=10):
    err = 0
    for i in range(series.shape[0]):
        prediction = model.cluster_centers_[model.labels_[i],:]
        sorted_sq_errs = np.sort((prediction - series[i,:])**2)
        if max_outliers == 0:
            err += sum(sorted_sq_errs)
        else:
            err += sum(sorted_sq_errs[:-1*max_outliers])
    return err

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
    if 'WWAH_PICKLE' not in os.environ:
        filename = os.path.join(os.environ['WWAH_PICKLE'], 
            'BehavioralStatistics.pkl')
    else:
        print 'Please run source setup.sh, WWAH_PICKLE is not defined'
        sys.exit(0)
    f = pickle.load(open(filename,'r'))
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
    user_part_times = np.zeros(shape=(len(parts), len(users)))
    for i,part in enumerate(parts):
        g = G.get_group(part)
        for _,row in g.iterrows():
            if not row['user'] in user_set:
               continue
            user_part_times[i,user_hash[row['user']]] = row['tries']
    X = user_part_times

X = X.T

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

######### KMeans
run_kmeans = False
if run_kmeans:
    space_errs = []
    ks = [1,2,3,4,5,10,25,50]
    outliers = [0,1,2,3,4,5,10,25,50,100]
    for k in ks:
        model = KMeans(n_clusters=k)
        for outlier in outliers:
            model.fit(X)
            X2 = remove_outliers(model, X, max_outliers=outlier)
            model.fit(X2)
            err = compute_kmeans_err(model, X2, max_outliers=0)
            space = k_outlier_space(k,outlier,X2)
            space_errs.append((k,outlier,space,err))
    
    S = pd.DataFrame(space_errs, columns=['k','outlier','space','err'])
    
    color=0
    for k,S_k in S.groupby('k'):
        print len(S_k)
        print cm.winter(int(color))
        plt.scatter(S_k['space'], S_k['err'], label="k="+str(k), color=cm.rainbow(color/float(len(ks))))
        color += 1
    plt.xlabel('space (uncompressed space is %d)'%(X.shape[0]*X.shape[1]))
    plt.ylabel('err')
    plt.legend()
    
G = df.groupby('user', as_index=False)[['time','tries']].sum()
