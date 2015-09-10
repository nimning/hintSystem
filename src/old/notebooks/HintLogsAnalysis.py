
# In[56]:

import random, os
from numpy.linalg import lstsq
from scipy.stats.contingency import margins
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import pickle

pickle_dir=os.environ['WWAH_PICKLE']

f = pickle.load(open(pickle_dir+'/BehavioralStatistics.pkl','rb'))
df = f.values()[0]
df


# ### Remove Outliers ###
# * Remove users who have not attempted many parts, and parts not attempted by many users.  
# * Replace NaN in the sub-table with 0.  
user_cutoff_quantile = 0.2
#count the number of tries cells that are not nan row-wise (users)
# This is the number of attempted problem parts per user
#Plot a histogram of number of number of attempted problem parts, and show the cutoff 
# for determining which users are "inactive"
user_list=df.groupby('user')['tries'].count()
user_list.sort()
user_list.hist(bins=40, color='blue')
# Get the height of the histogram
hist_height = hist(user_list, bins=40, label='number of attempted parts per user')[0].max()
user_cutoff = user_list.quantile(user_cutoff_quantile)
vlines([user_cutoff],[0],[hist_height], color='red', label='cutoff at %.1f attempted parts'%user_cutoff)
legend()
# Show examples of active and inactive users
inactive_users = user_list[user_list <= user_cutoff]
active_users = user_list[user_list > user_cutoff]
print '### Sample Inactive Users:'
print random.sample(inactive_users.index, 10)
print '### Sample Active Users:'
print random.sample(active_users.index, 10)

part_cutoff_quantile = 0.42
#count the number of tries cells that are not nan column-wise (part)
# This is the number of users who attempted the part
#Plot a histogram of number of number of users who attempted parts, and show the cutoff
# for determining which users are "inactive"
part_list=df.groupby(['assignment','problem_no','part_no'])['tries'].count()
part_list.sort()
part_list.hist(bins=40, color='blue')
# Get the height of the histogram
hist_height = hist(part_list, bins=40, label='number of users who attempted part')[0].max()
part_cutoff = part_list.quantile(part_cutoff_quantile)
vlines([part_cutoff],[0],[hist_height], color='red', label='cutoff at %.1f users who attempted part'%part_cutoff)
legend()
junk_parts = part_list[part_list <= part_cutoff]
attempted_parts = part_list[part_list > part_cutoff]
print '### Sample Junk Parts:'
print junk_parts.ix[random.sample(junk_parts.index,5)]
print ''
print '### Sample Attempted Parts:'
print attempted_parts.ix[random.sample(attempted_parts.index,5)]
print ''

# remove junk_parts and inactive_users from the data frame.
dfr1=df[[(user in active_users) 
        for (user,assignment,problem_no,part_no) in df[['user','assignment','problem_no','part_no']].values]]
dfr2=df[[(user in active_users and (assignment, problem_no,part_no) in attempted_parts) 
        for (user,assignment,problem_no,part_no) in df[['user','assignment','problem_no','part_no']].values]]
print shape(df),shape(dfr1),shape(dfr2)
#reorganize as a table.
Table=dfr2.pivot_table(rows='user',cols=['assignment','problem_no','part_no'],values=['final_correct','tries','time'])
Table=Table.reorder_levels([1,2,3,0], axis=1)
Table=Table.sortlevel(axis=1,level=0)
print shape(Table)
Table.ix[0:10,0:20]


print 'Original table size, (#users,#parts)='+str(shape(Table))
#Table=Table.drop(inactive_users.index,axis=0)
print 'After dropping users, (#users,#parts)='+str(shape(Table))
Table=Table.drop(junk_parts.index,axis=1,level=3)
print 'After dropping parts, (#users,#parts)='+str(shape(Table))

s=shape(Table)
sz=s[0]*s[1]+0.0
count=Table.count().sum()
print s,sz,count,(0.0+sz-count)/sz
Tf=Table.unstack()
print Tf.mean(),Tf.var()
Tf.hist(bins=100)
print (Tf>20).sum()/sz, Table.unstack().max()

Table = Table.apply(log)
Tf=Table.unstack()
print Tf.mean(),Tf.var()
Tf.hist(bins=100)

Mean=Tf.mean()
Tf=Tf-Mean
print Tf.mean(),Tf.var()
Tf.hist(bins=100)
Table=Table-Mean


# Out[31]:

#     1.82775048738e-13 0.786529856119
# 

# image file:

# ### Perform Regression ###

# In[49]:

mean_per_part=pd.DataFrame(Table.mean(axis=0),columns=['mean_per_part']).reset_index()
mean_per_user=pd.DataFrame(Table.mean(axis=1),columns=['mean_per_user']).reset_index()
RTf=pd.DataFrame(Tf,columns=['Y']).reset_index()

RTf=pd.merge(RTf,mean_per_user,on=['user'])
RTf=pd.merge(RTf,mean_per_part,on=['assignment','problem_no','part_no'])
RTf=RTf.dropna();
RTf['product']=RTf['mean_per_part']*RTf['mean_per_user']
print RTf.head()


# Out[49]:

#                assignment  problem_no  part_no      user         Y  mean_per_user  \
#     0  Assignment10.11.13           1        1      a4to  1.095319       0.241453   
#     1  Assignment10.11.13           1        1  a5taylor -0.157444      -0.038938   
#     3  Assignment10.11.13           1        1   actsang -0.850591      -0.024419   
#     4  Assignment10.11.13           1        1  aferbrac -0.850591      -0.211147   
#     5  Assignment10.11.13           1        1      ahem -0.850591      -0.202087   
#     
#        mean_per_part   product  
#     0       0.806005  0.194612  
#     1       0.806005 -0.031384  
#     3       0.806005 -0.019681  
#     4       0.806005 -0.170185  
#     5       0.806005 -0.162883  
# 

#     //anaconda/python.app/Contents/lib/python2.7/site-packages/pandas/core/config.py:570: DeprecationWarning: height has been deprecated.
#     
#       warnings.warn(d.msg, DeprecationWarning)
#     //anaconda/python.app/Contents/lib/python2.7/site-packages/pandas/core/config.py:570: DeprecationWarning: height has been deprecated.
#     
#       warnings.warn(d.msg, DeprecationWarning)
# 

# In[50]:

X=RTf[['mean_per_user','mean_per_part','product']].values
Y=RTf[['Y']]
x, residuals, rank, s = lstsq(X,Y)
print shape(X),shape(Y)


# Out[50]:

#     (36686, 3) (36686, 1)
# 

# In[51]:

print residuals[0]/len(Y),x,s


# Out[51]:

#     0.455575948993 [[ 0.99637913]
#      [ 0.99890417]
#      [ 0.91284913]] [ 102.31315836   36.87559719   19.71663866]
# 

# In[52]:

print 'Parameters of least-square fit: '
print '<user/part tries> = %.3f user, %.3f part, %.3f product, base rate: %.3f'% tuple(x.tolist())
print 'Proportion reduction in variance: %.3f'%(residuals / (L[:,2]**2).sum())


# Out[52]:


    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)

    <ipython-input-52-eae6381ec44e> in <module>()
          1 print 'Parameters of least-square fit: '
    ----> 2 print '<user/part tries> = %.3f user, %.3f part, %.3f product, base rate: %.3f'% tuple(x.tolist())
          3 print 'Proportion reduction in variance: %.3f'%(residuals / (L[:,2]**2).sum())


    TypeError: float argument required, not list


#     Parameters of least-square fit: 
# 

# In[21]:

R = (Y - X.dot(x))
Residuals = R.reshape(Table.shape)


# In[22]:

# Learn and score PCA/KMeans
ks = np.array([1,2,3,4,5,10,20,25])
kmeans_scores = []
pca_scores = []
U,S,V = svd(Residuals)
for k in ks:
    model = KMeans(n_clusters=k)
    score = (model.fit_transform(Residuals).min(axis=1)**2).sum()
    kmeans_scores.append(score)
    S2 = S.copy()
    S2[k:] = 0
    D = np.concatenate([np.diag(S2), np.zeros(shape=(164,349-164))], axis=1)
    Pred = np.dot(np.dot(U,D),V)
    pca_scores.append(   ((Pred - Residuals)**2).sum().sum()   )

kmeans_scores = np.array(kmeans_scores)
print kmeans_scores
pca_scores = np.array(pca_scores)

total_residual_variance = (Residuals**2).sum().sum()
normalized_ks = ks/float(Residuals.shape[0])

# Compute variance ratio for KMeans
kmeans_scores = 1 - (kmeans_scores / total_residual_variance)
# Compute variance ratio for PCA
pca_scores = 1 - (pca_scores / total_residual_variance)
# Plot proportion of variance reduction vs. space compression
plot(normalized_ks, kmeans_scores, label='kmeans')
plot(normalized_ks,pca_scores, label='pca')
plot(normalized_ks,(np.cumsum(S**2))[ks]/((S**2).sum()), label='pca singular values')
#plot(normalized_ks, pca_scores)
xlabel('Compression ratio')
ylabel('Proportion of Variance Explained')
legend()


# Out[22]:


    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)

    <ipython-input-22-cad193e3de67> in <module>()
         11     S2[k:] = 0
         12     D = np.concatenate([np.diag(S2), np.zeros(shape=(164,349-164))], axis=1)
    ---> 13     Pred = np.dot(np.dot(U,D),V)
         14     pca_scores.append(   ((Pred - Residuals)**2).sum().sum()   )
         15 


    ValueError: matrices are not aligned


# In[498]:

print sorted(Table.index[np.argsort(U[:,0])[-10:]])
print sorted(Table.columns[np.argsort(U[0,:])[-10:]])


# Out[498]:

#     ['clemon', 'dcchou', 'hshaikle', 'jagustin', 'jpw007', 'khchong', 'mabid', 'ppbalist', 'rtien', 'suliu']
#     [('Assignment10.11.13', 3L, 3L), ('Assignment10.11.13', 4L, 2L), ('Assignment10.11.13', 5L, 2L), ('Assignment10.14.13', 2L, 2L), ('Assignment10.14.13', 4L, 2L), ('Assignment10.14.13', 5L, 10L), ('Assignment10.14.13', 5L, 12L), ('Assignment10.14.13', 7L, 2L), ('Assignment10.16.13', 4L, 1L), ('Assignment10.18.13', 1L, 2L)]
# 

# In[499]:

print sorted(Table.index[np.argsort(U[:,1])[-10:]])
print sorted(Table.columns[np.argsort(U[1,:])[-10:]])


# Out[499]:

#     ['clemon', 'e6hwang', 'esnover', 'jagustin', 'jchin', 'jogong', 'jpw007', 'rtien', 'suliu', 'xil039']
#     [('Assignment10.14.13', 1L, 4L), ('Assignment10.14.13', 4L, 1L), ('Assignment10.14.13', 7L, 3L), ('Assignment10.18.13', 1L, 1L), ('Assignment10.18.13', 2L, 1L), ('Assignment10.18.13', 2L, 6L), ('Assignment10.18.13', 4L, 2L), ('Assignment10.23.13', 1L, 2L), ('Assignment10.23.13', 2L, 1L), ('Assignment10.23.13', 3L, 1L)]
# 

# In[ ]:

get_ipython().system(u'pwd')

