from read_logs import read_log
from read_logs import make_dictionary
from kf import kalman_filter
from sets import Set
from matplotlib import pyplot as pp

def _merge_data_by_time(data1, data2):
	set1 = Set([elem[5] for elem in data1])
	set2 = Set([elem[5] for elem in data2])
	intersect = set1&set2
	ndata1 = [elem for elem in data1 if elem[5] in intersect]
	ndata2 = [elem for elem in data2 if elem[5] in intersect]
	#output format ((la1,lo1),(la2,lo2))
	return ([(elem[2],elem[3]) for elem in ndata1],[(elem[2],elem[3]) for elem in ndata2])

def merge_data_by_time(data):
	dataset = {elem : Set([v[5] for v in data[elem]]) for elem in data.keys()}
	intersect = reduce((lambda x, y: x & dataset[y]), dataset, dataset[dataset.keys()[0]])
	print intersect
	ndataset = {elem : data[elem] for elem in data.keys if data[elem][5] in intersect}
	

def merge_data_by_time_test():
	data = read_log('logs/120816_101621')
	#data1 = data1[:4]
	#data2 = data2[:4]
	#print data1, data2
	merge_data_by_time(data)
	#print d1, d2
	#pp.plot(*zip(*d1))
	#pp.plot(*zip(*d2))
	#pp.show()

def plot_simple(data1, data2):
	d1,d2 = merge_data_by_time(data1, data2)
	#print d1, d2
	pp.plot(*zip(*d1))
	pp.plot(*zip(*d2))
	pp.show()	

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

merge_data_by_time_test()




