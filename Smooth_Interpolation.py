# 2020.04.24
# use DCT and IDCT for interpolation 
# input for Smooth_Interpolation: (?, initN, initN, 1)
# return for Smooth_Interpolation: (?, targetN, targetN, 1)
import numpy as np
from scipy.fftpack import dct, idct
from skimage.util import view_as_windows

class DCT():
    def __init__(self, N=8, P=8):
        self.N = N
        self.P = P
    
    def transform(self, a):
        S = list(a.shape)
        a = a.reshape(-1, self.N, self.P, 1)
        a = dct(dct(a, axis=1, norm='ortho'), axis=2, norm='ortho')
        return a.reshape(S)

    def inverse_transform(self, a):
        S = list(a.shape)
        a = a.reshape(-1, self.N, self.P, 1)
        a = idct(idct(a, axis=1, norm='ortho'), axis=2, norm='ortho')
        return a.reshape(S)
        
class ZigZag():
    def __init__(self, N=8):
        self.N = N
        self.idx = self.zig_zag_getIdx(N).astype('int32')
        
    def zig_zag(self, i, j, n):
        if i + j >= n:
            return n * n - 1 - self.zig_zag(n - 1 - i, n - 1 - j, n)
        k = (i + j) * (i + j + 1) // 2
        return k + i if (i + j) & 1 else k + j

    def zig_zag_getIdx(self, N):
        idx = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                idx[i, j] = self.zig_zag(i, j, N)
        return idx.reshape(-1)
    
    def transform(self, X):
        S = list(X.shape)
        X = X.reshape(X.shape[0], -1)
        return X[:, np.argsort(self.idx)].reshape(S)
    
    def inverse_transform(self, X):
        S = list(X.shape)
        X = X.reshape(X.shape[0], -1)
        return X[:, self.idx].reshape(S)

class Smooth_Interpolation():
    def __init__(self, initN=8, targetN=16):
        self.initN = initN
        self.targetN = targetN
        self.dct1 = DCT(N=initN, P=initN)
        self.zigzag1 = ZigZag(N=initN)
        self.dct2 = DCT(N=targetN, P=targetN)
        self.zigzag2 = ZigZag(N=targetN)
    
    def transform(self, X):
        assert (X.shape[1] == self.initN and X.shape[2] == self.initN), "<Error> Input shape not match!"
        X = self.dct1.transform(X)
        X = self.zigzag1.transform(X).reshape(X.shape[0], -1)
        X = np.concatenate((X, np.zeros((X.shape[0], self.targetN**2 - self.initN**2))), axis=1)
        X = self.zigzag2.inverse_transform(X).reshape(X.shape[0], self.targetN, self.targetN, 1)
        X = self.dct2.inverse_transform(X)
        return X.reshape(X.shape[0], self.targetN, self.targetN, 1)

if __name__ == "__main__":
    from sklearn import datasets
    print(" > This is a test example for Smooth_Interpolation.")
    digits = datasets.load_digits()
    X = digits.images.reshape((len(digits.images), 8, 8, 1))[:10]
    si = Smooth_Interpolation(initN=8, targetN=16)

    Y = si.transform(X)

    import matplotlib.pyplot as plt 
    ax1 = plt.subplot(1, 2, 1)
    plt.imshow(X[0,:,:,0])
    plt.title('Before interpolation')
    ax2 = plt.subplot(1, 2, 2)
    plt.imshow(Y[0,:,:,0])
    plt.title('After interpolation')

    plt.show()
