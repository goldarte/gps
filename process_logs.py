from read_logs import read_log
from read_logs import make_dictionary
from kf import kalman_filter
from sets import Set
from matplotlib import pyplot as pp
import os
import sys

test_log = read_log('logs/120816_101621')
pics_dir = 'pics/'
directory = pics_dir+test_log.filename+'/'
if not os.path.exists(directory):
    os.makedirs(directory)

def center_point(data):
	x = []
	y = []
	for key in data.keys():
		for elem in data[key]:
			x.append(elem[2])
			y.append(elem[3])
	x_avg = (max(x)+min(x))/2
	y_avg = (max(y)+min(y))/2
	return [x_avg,y_avg]

def center_point_test():
	print center_point(test_log.data)

def merge_data_by_time(data):
	dataset = {elem : Set([v[5] for v in data[elem]]) for elem in data.keys()}
	intersect = reduce((lambda x, y: x & dataset[y]), dataset, dataset[dataset.keys()[0]])
	#print intersect
	ndataset = {elem : [[v[2],v[3]] for v in data[elem] if v[5] in intersect] for elem in data.keys()}
	return ndataset	

def merge_data_by_time_test():
	ndata = merge_data_by_time(data)
	print ndata['BASE']

def shift_data_to_center_point(data):
	cp = center_point(data)
	return {key : [[v[0],v[1],v[2]-cp[0],v[3]-cp[1],v[4],v[5]] for v in data[key]] for key in data.keys()}

def shift_data_to_center_point_test():
	print shift_data_to_center_point(test_log.data)['BASE']

def plot_trajectories(data, filename):
	#print d1, d2
	legend = []
	for elem in sorted(data.keys()):
		#pp.plot(*zip(*data[elem]), label = elem)
		l, = pp.plot(*zip(*data[elem]), label = elem)
		legend.append(l) 
	pp.xlabel('longitude, m')
	pp.ylabel('latitude, m')
	pp.legend(handles=legend)
	pp.title(filename + ' trajectories')
	pp.savefig(pics_dir+filename+'/'+filename + '_trajectories.png')
	pp.clf()
	#pp.show()	

def plot_trajectories_test():
	sd = shift_data_to_center_point(test_log.data)
	ndata = merge_data_by_time(sd)
	plot_trajectories(ndata, test_log.filename)

def filter_data_diff_mode(data, key1, key2):
	sigma_proc = 0.25
	sigma_meas = 30
	x1 = data[key1]
	x2 = data[key2]
	x = [x1[i]-x2[i] for i in range(len(x1))]
	x0 = x[0]
	P0 = np.eye(2)*sigma_proc
	F = np.eye(2)
	Q = np.eye(2)*sigma_proc
	H = np.eye(2)
	R = np.eye(2)*sigma_meas
	kf = kalman_filter(F, Q, H, R, x0, P0)
	out = kf.Apply(x)
	return {'filtered',out}	

def filter_data_diff_mode_test():
	pass

def prepare_diff_mode(data1,data2):
	sigma_proc = 0.25
	sigma_meas = 30
	
	#x0 = (data_port(1,3:4)-base_pos)
	#P0 = eye(2)*sigma_proc; 
	#F = eye(2);
	#Q = eye(2)*sigma_proc;
	#H = eye(2);
	#R = eye(2)*sigma_meas;
	#y = data_port(:,3:4)-base_pos;

#merge_data_by_time_test()
plot_trajectories_test()
#center_point_test()
#shift_data_to_center_point_test()




