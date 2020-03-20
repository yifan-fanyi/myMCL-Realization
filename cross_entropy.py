# v2020.03.19
#
# class Cross_Entropy()
#   Compute cross entropy across each feature for feature selection
#
# three methods included
#   compute:
#         Manimaran A, Ramanathan T, You S, et al. Visualization, Discriminability and Applications of Interpretable Saak Features[J]. 2019.
#   KMeans_Cross_Entropy
#   ML_Cross_Entropy

import numpy as np 
import math
import sklearn
from sklearn.cluster import KMeans

from mylearner import myLearner
class Cross_Entropy():
    def __init__(self, num_class, num_bin=10):
        self.num_class = (int)(num_class)
        self.num_bin = (int)(num_bin)

    def bin_process(self, x ,y):
        if np.max(x) ==  np.min(x):
            return -1*np.ones(self.num_bin)
        x = ((x - np.min(x)) / (np.max(x) - np.min(x))) * (self.num_bin)
        mybin = np.zeros((self.num_bin, self.num_class))
        b = x.astype('int64')
        b[b == self.num_bin] -= 1
        mybin[b,y] += 1.
        for l in range(0,self.num_class):
            p = np.array(y[ y==l ]).shape[0]
            mybin[:,l] /= (float)(p)
        return np.argmax(mybin, axis=1)
    
    def kmeans_process(self, x, y):
        kmeans = KMeans(n_clusters=self.num_bin, random_state=0).fit(x.reshape(1,-1))
        mybin = np.zeros((self.num_bin, self.num_class))
        b = kmeans.labels_.astype('int64')
        b[b == self.num_bin] -= 1
        mybin[b,y] += 1.
        for l in range(0,self.num_class):
            p = np.array(y[ y==l ]).shape[0]
            mybin[:,l] /= (float)(p)
        return np.argmax(mybin, axis=1)

    def compute_prob(self, x, y):
        prob = np.zeros((self.num_class, x.shape[1]))
        for k in range(0, x.shape[1]):
            mybin = self.bin_process(x[:,k], y[:,0])
            #mybin = self.kmeans_process(x[:,k], y[:,0])
            for l in range(0, self.num_class):
                p = mybin[mybin == l]
                p = np.array(p).shape[0]
                prob[l,k] = p / (float)(self.num_bin)
        return prob

    def compute(self, x, y, class_weight=None):
        x = x.astype('float64')
        y = y.astype('int64')
        prob = self.compute_prob(x, y)
        prob = -1 * np.log10(prob + 1e-5) / np.log10(self.num_class)
        y = np.moveaxis(y, 0, 1)
        H = np.zeros((self.num_class, x.shape[1]))
        for c in range(0, self.num_class):
            yy = y == c
            p = prob[c].reshape(prob.shape[1], 1)
            p = p.repeat(yy.shape[1], axis=1)
            H[c] += np.mean(yy * p, axis=1)
        if class_weight != None:
            class_weight = np.array(class_weight)
            H *= class_weight.reshape(class_weight.shape[0],1) * self.num_class
        return np.sum(H, axis=0)

    # new cross entropy
    def KMeans_Cross_Entropy(self, X, Y):
        if np.unique(Y).shape[0] == 1: #alread pure
            return 0
        if X.shape[0] < self.num_bin:
            return -1
        kmeans = KMeans(n_clusters=self.num_bin, random_state=0).fit(X)
        prob = np.zeros((self.num_bin, self.num_class))
        for i in range(self.num_bin):
            idx = (kmeans.labels_ == i)
            tmp = Y[idx]
            for j in range(self.num_class):
                prob[i, j] = (float)(tmp[tmp == j].shape[0]) / ((float)(Y[Y==j].shape[0]) + 1e-5)
        prob = (prob)/(np.sum(prob, axis=1).reshape(-1,1) + 1e-5)
        y = np.zeros((Y.shape[0], self.num_class))
        y[np.arange(Y.size), Y] = 1
        probab = prob[kmeans.labels_]
        return sklearn.metrics.log_loss(y, probab)/math.log(self.num_class)

    # new machine learning based cross entropy
    def ML_Cross_Entropy(self, X, Y, learner):
        X, XX, Y, YY = sklearn.model_selection.train_test_split(X, Y, train_size=0.8, random_state=42, stratify=Y)
        reg = myLearner(learner, self.num_class)
        reg.fit(X, Y)
        pred = reg.predict_proba(XX)        
        y = np.zeros((YY.shape[0], self.num_class))
        y[np.arange(YY.size), YY] = 1
        return sklearn.metrics.log_loss(y, pred)/math.log(self.num_class)

if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import datasets
    from sklearn.model_selection import train_test_split
    
    print(" \n> This is a test enample: ")
    digits = datasets.load_digits()
    X = digits.images.reshape((len(digits.images), -1))
    print(" input feature shape: %s"%str(X.shape))
    X_train, X_test, y_train, y_test = train_test_split(X, digits.target, test_size=0.2,  stratify=digits.target)
    
    ce = Cross_Entropy(num_class=10, num_bin=10)
    print(" --> KMeans ce: %s"%str(ce.KMeans_Cross_Entropy(X_train, y_train)))
    print(" --> ML ce: %s"%str(ce.ML_Cross_Entropy(X_train, y_train, learner=RandomForestClassifier())))
    print("------- DONE -------\n")