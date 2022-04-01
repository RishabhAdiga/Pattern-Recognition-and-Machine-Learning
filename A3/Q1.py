from random import gauss
import numpy as np
import os

dir_list = os.listdir('Features//coast//train')
data_coast = []
for file in dir_list:
    data_coast.extend(np.loadtxt('Features/coast/train/'+file))
data_coast = np.array(data_coast)

dir_list = os.listdir('Features//forest//train')
data_forest = []
for file in dir_list:
    data_forest.extend(np.loadtxt('Features/forest/train/'+file))
data_forest = np.array(data_forest)

dir_list = os.listdir('Features//highway//train')
data_highway = []
for file in dir_list:
    data_highway.extend(np.loadtxt('Features/highway/train/'+file))
data_highway = np.array(data_highway)

dir_list = os.listdir('Features//mountain//train')
data_mountain = []
for file in dir_list:
    data_mountain.extend(np.loadtxt('Features/mountain/train/'+file))
data_mountain = np.array(data_mountain)

dir_list = os.listdir('Features//opencountry//train')
data_opencountry = []
for file in dir_list:
    data_opencountry.extend(np.loadtxt('Features/opencountry/train/'+file))
data_opencountry = np.array(data_opencountry)

def Euclidean_Distance(v1,v2):
    d = np.sqrt(sum((v1-v2)**2))
    return(d)

def Random_Means_Initialization(k,data):
    means = []
    for i in np.random.randint(0, len(data),k):
        means.append(data[i])

    return means

def Assign_Cluster(k,data,means):
    cluster_nums = [0]*len(data)

    for n in range(len(data)):
        min_dist = float("inf")
        data_n = data[n]
        for K in range(k):
            if Euclidean_Distance(data_n,means[K]) < min_dist :
                min_dist = Euclidean_Distance(data_n,means[K])
                cluster_nums[n] = K+1

    return cluster_nums

def Update_Mean(k,cluster_nums,data):  #TO DO : Make this more efficient 
    means = [[0 for j in range(len(data[0]))] for i in range(k)]
    count = [0]*k
    for n in range(len(data)):
        means[cluster_nums[n]-1] += data[n]
        count[cluster_nums[n]-1] += 1

    return [[x/count[i] for x in means[i]] if count[i]!=0 else [0]*len(data[0]) for i in range(k)]

def Find_Centroids(k,data,num_iterations):
    means = Random_Means_Initialization(k,data)
    old_cluster_nums = [0]*len(data)

    for i in range(num_iterations):
        cluster_nums = Assign_Cluster(k,data,means)
        if i==0:
            # print(cluster_nums)
            pass
        if cluster_nums == old_cluster_nums:
            # print(cluster_nums)
            # print(old_cluster_nums)
            # print(i)
            break
        means = Update_Mean(k,cluster_nums,data)
        old_cluster_nums = cluster_nums

    cov=[]
    pi_k=[]

    for j in range(k):
        indexes = np.where(np.array(cluster_nums)==j+1)
        cov.append(covariance(data[indexes],means[j],flag=0))
        pi_k.append(len(indexes[0])/len(data)) 
    return np.array(means),np.array(cov),np.array(pi_k)

def covariance(x,u,flag=1,r_k=[],N_k=[]):
    if flag==0:
        r_k = np.ones(len(x))
        N_k = len(x)-1
    out = np.zeros((len(x[0]),len(x[0])))
    for i,v in enumerate(x):
        vec = (v-u)
        vec = vec.reshape((len(vec),1))
        out += r_k[i] * np.dot((vec),vec.T)
    return (1/N_k) * out

def Normal_distribution(x,u,E):     #TO DO : Make this more efficient
    E_inv = np.linalg.pinv(E)
    x_m = x-u
    x_m = x_m.reshape((len(x_m),1))
    exp_arg = -1/2 * np.dot(np.dot(x_m.T,E_inv),x_m)[0][0]
    cond = np.linalg.cond(E)
    v1 = pow(2*np.pi,len(x)/2)
    v2 = np.sqrt(np.linalg.det(E))
    v3 = np.exp(exp_arg)
    gaus = 1/pow(2*np.pi,len(x)/2)/np.sqrt(np.linalg.det(E)) * np.exp(exp_arg)
    return gaus

def gmm(data,k,pi_k,mean,cov,no_of_iterations=10):
    for ite in range(no_of_iterations):
        #Expectation
        r_nk = np.zeros((len(data),k))
        for i,x in enumerate(data):
            numerators = np.array([pi_k[j] * Normal_distribution(x,mean[j],cov[j]) for j in range(k)])
            denominators = sum(numerators)
            r_nk[i,:] = numerators/denominators
        #Maximisation
        new_mean = mean.copy()
        N = len(data)
        for j in range(k):
            N_k = sum(r_nk[:,j])
            pi_k[j] = N_k/N
            new_mean[j] = sum((data.T*r_nk[:,j]).T)/N_k
            # new_mean[k] = 1/N_k*np.dot(r_nk[:,j].T,data)
            cov[j] = covariance(data,mean[j],1,r_nk[:,j],N_k)
        mean = new_mean
        print(pi_k)
    return mean,cov,pi_k

def find_probabiltity(x,mean_k,cov_k,pi_k,k):
    prob = 0 
    for feature in x:
        val = [pi_k[j] * Normal_distribution(feature,mean_k[j],cov_k[j]) for j in range(k)]
        prob+=np.log10(sum(val))
    return prob
    

def classification(x,means,covs,pi,k):
    P_max = 0
    classify = -1
    for i in range(len(means)):
        P_x = find_probabiltity(x,means[i],covs[i],pi[i],k)
        print(P_x)
        if P_x > P_max:
            P_max = P_x
            classify = i
    return classify

means,covs,pi = [],[],[]
k=2
mean,cov,pi_k = Find_Centroids(k,data_coast,10)
# print(means,pi_k)
print(pi_k)
new_mean,new_cov,new_pi_k=gmm(data_coast,k,pi_k,mean,cov,2)
# print(means)
means.append(new_mean)
covs.append(new_cov)
pi.append(new_pi_k)
print("trained")

# mean,cov,pi_k = Find_Centroids(k,data_forest,10)
# new_mean,new_cov,new_pi_k=gmm(data_forest,k,pi_k,mean,cov)
# means.append(new_mean)
# covs.append(new_cov)
# pi.append(new_pi_k)
# print("trained")

# mean,cov,pi_k = Find_Centroids(k,data_highway,10)
# new_mean,new_cov,new_pi_k=gmm(data_highway,k,pi_k,mean,cov)
# means.append(new_mean)
# covs.append(new_cov)
# pi.append(new_pi_k)
# print("trained")

# mean,cov,pi_k = Find_Centroids(k,data_mountain,10)
# new_mean,new_cov,new_pi_k=gmm(data_mountain,k,pi_k,mean,cov)
# means.append(new_mean)
# covs.append(new_cov)
# pi.append(new_pi_k)
# print("trained")

# mean,cov,pi_k = Find_Centroids(k,data_opencountry,10)
# new_mean,new_cov,new_pi_k=gmm(data_opencountry,k,pi_k,mean,cov)
# means.append(new_mean)
# covs.append(new_cov)
# pi.append(new_pi_k)
# print("trained")

dir_list = os.listdir('Features//coast//dev')
data_test_coast = []
for file in [dir_list[0]]:
    data_test_coast.extend(np.loadtxt('Features/coast/dev/'+file))
data_test_coast = np.array(data_test_coast)

print(classification(data_test_coast,means,covs,pi,k))