import numpy as np
import matplotlib.pyplot as mp

def kf_step(x0, P0, y, F, Q, H, R):
	assert(type(x0).__name__=='matrix')
	assert(type(P0).__name__=='matrix')
	assert(type(y).__name__=='matrix')
	assert(type(F).__name__=='matrix')
	assert(type(Q).__name__=='matrix')
	assert(type(H).__name__=='matrix')
	assert(type(R).__name__=='matrix')
	assert(x0.shape[0]==F.shape[1])
	assert(x0.shape[1]==1)
	assert(F.shape[0]==F.shape[1])
	assert(Q.shape[0]==Q.shape[1])
	assert(F.shape[0]==Q.shape[1])
	assert(y.shape[0]==H.shape[0])
	assert(y.shape[1]==1)
	assert(H.shape[1]==x0.shape[0])
	assert(R.shape[0]==R.shape[1])
	assert(R.shape[0]==y.shape[0])
	xe = F*x0
	Pe = F*P0*F.T + Q
	G = Pe*H.T*(H*Pe*H.T + R)
	x = xe + G*(y - H*xe)
	P = (np.eye(x0.shape[0]) - G*H)*Pe
	return (x, P)

class kalman_filter:
	def __init__(self, F, Q, H, R, x = 0, P = 0):
		self.F = np.matrix(F)
		self.Q = np.matrix(Q)
		self.H = np.matrix(H)
		self.R = np.matrix(R)
		self.x = np.matrix(x)
		self.P = np.matrix(P)
		assert(self.F.shape[0]==self.F.shape[1])
		assert(self.Q.shape[0]==self.Q.shape[1])
		assert(self.R.shape[0]==self.R.shape[1])
	def SetState(self, state, covariance):
		self.x = state
		self.P = covariance
	def Apply(self, y):
		out = np.zeros(len(y))
		for i in range(0,len(y)):
			self.x, self.P = kf_step(self.x, self.P, np.matrix(y[i]), self.F, self.Q, self.H, self.R)
			out[i] = self.x
		return out

#simulation
num = 1000
t = np.linspace(0, 1, num)
x = np.sin(2*np.pi*t)
sigma_proc = 0.1
sigma_meas = 0.1
y = x + np.random.randn(1, num)[0]*sigma_meas
F = 1
Q = sigma_proc
H = 1
R = sigma_meas
kf = kalman_filter(F, Q, H, R)
xf = kf.Apply(y)
mp.plot(t, x)
mp.plot(t, y)
mp.plot(t, xf)
mp.show()

