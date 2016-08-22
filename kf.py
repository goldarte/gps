import numpy as np
import matplotlib.pyplot as mp

# calculate one step of Kalman filter by parameters of model;
# model is: x = Fx + w(Q), y = Hx + v(R)
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
	G = Pe*H.T*(H*Pe*H.T + R).I
	x = xe + G*(y - H*xe)
	P = (np.eye(x0.shape[0]) - G*H)*Pe
	return (x, P)

class kalman_filter:
	def __init__(self, F, Q, H, R, x, P):
		self.F = np.matrix(F)
		self.Q = np.matrix(Q)
		self.H = np.matrix(H)
		self.R = np.matrix(R)
		self.x = np.matrix(x).T
		self.P = np.matrix(P)
		assert(self.F.shape[0]==self.F.shape[1])
		assert(self.Q.shape[0]==self.Q.shape[1])
		assert(self.R.shape[0]==self.R.shape[1])
	def Apply(self, y):
		out = []
		for elem in y:
			self.x, self.P = kf_step(self.x, self.P, np.matrix(elem).T, self.F, self.Q, self.H, self.R)
			#print (self.x, self.P)
			out.append(self.x.A1)
		return out
	def Apply_step(self, y):
		out = kf_step(self.x, self.P, np.matrix(y[1]).T, self.F, self.Q, self.H, self.R)
		return out

def test():
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
	kf = kalman_filter(F, Q, H, R, 0, 0)
	xf = kf.Apply(y)
	mp.plot(t, x)
	mp.plot(t, y)
	mp.plot(t, xf)
	mp.show()

