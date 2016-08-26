from read_logs import read_log
from read_logs import make_dictionary
from kf import kalman_filter
from sets import Set
from matplotlib import pyplot as pp
import numpy as np
import os
import sys

test_log = read_log('logs/120816_103425')
pics_dir = 'pics/'
directory = pics_dir+test_log.filename+'/'
if not os.path.exists(directory):
    os.makedirs(directory)

def get_point_list(data):
	return sorted(list(set([elem[1] for elem in data[data.keys()[0]]])))

def get_point_data(data, points):
	ndata = {key: [elem for elem in data[key] if elem[1] in points] for key in data.keys()}
	return ndata
	#ndata = {elem:data[elem]

def get_key_data(data, keys):
	return {key: data[key] for key in data.keys() if key in keys}	

# calculate center point for gps data {elem:[(B|P, point, lo, la, hdop, time)]}
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

def convert_to_2d(data):
	return {key: [(elem[2],elem[3]) for elem in data[key]] for key in data.keys()}

def merge_data_by_time_2d(data):
	dataset = {key : Set([elem[5] for elem in data[key]]) for key in data.keys()}
	intersect = reduce((lambda x, y: x & dataset[y]), dataset, dataset[dataset.keys()[0]])
	#print intersect
	ndataset = {key : [[elem[2],elem[3]] for elem in data[key] if elem[5] in intersect] for key in data.keys()}
	return ndataset	

def merge_data_by_time(data):
	dataset = {key : Set([elem[5] for elem in data[key]]) for key in data.keys()}
	intersect = reduce((lambda x, y: x & dataset[y]), dataset, dataset[dataset.keys()[0]])
	#print intersect
	ndataset = {key : [elem for elem in data[key] if elem[5] in intersect] for key in data.keys()}
	return ndataset	

def merge_data_by_time_test():
	ndata = merge_data_by_time_2d(test_log.data)
	print ndata['BASE']

def shift_data_to_center_point(data):
	cp = center_point(data)
	return {key : [[v[0],v[1],v[2]-cp[0],v[3]-cp[1],v[4],v[5]] for v in data[key]] for key in data.keys()}

def shift_data_to_center_point_test():
	print shift_data_to_center_point(test_log.data)['BASE']

def prepare_data_2d(data):
	shift_data = shift_data_to_center_point(data)
	clear_data = merge_data_by_time_2d(shift_data)
	return clear_data

def prepare_data(data):
	shift_data = shift_data_to_center_point(data)
	clear_data = merge_data_by_time(shift_data)
	return clear_data

#input format {elem: [(x,y)]}
def plot_data_2d(data, logs_name, plot_name, mode = ('raw')):
	#print d1, d2
	legend = []
	for elem in sorted(data.keys()):
		#pp.plot(*zip(*data[elem]), label = elem)
		if 'raw' in mode:
			l, = pp.plot(*zip(*data[elem]), label = elem)
			legend.append(l) 
		if 'points' in mode:
			l, = pp.plot(*zip(*data[elem]), label = elem, ls = '', marker = 'o')
			legend.append(l) 		
	pp.xlabel('longitude, m')
	pp.ylabel('latitude, m')
	pp.legend(handles=legend)
	pp.title(logs_name + ' ' + plot_name)
	pp.savefig(pics_dir+logs_name+'/'+logs_name + '_' + plot_name + '.png')
	pp.clf()
	#pp.show()	

def plot_data(data, logs_name, plot_name, mode = ('raw')):
	#print d1, d2
	legend = []
	for key in sorted(data.keys()):
		print key
		#pp.plot(*zip(*data[elem]), label = elem)
		xy = [[elem[2], elem[3]] for elem in data[key]]
		if 'raw' in mode:
			l, = pp.plot(*zip(*xy), label = key)
			legend.append(l) 
		if 'points' in mode:
			l, = pp.plot(*zip(*xy), label = key, ls = '', marker = 'o')
			legend.append(l) 
		if 'std' in mode:
			points = get_point_list(data)
			print points
			for point in points:
				xy = [[elem[2], elem[3]] for elem in data[key] if elem[1] == point]
				mean = np.mean(xy, axis = 0)
				std = np.std(xy, axis = 0)
				pp.plot([mean[0]-std[0]/2, mean[0]+std[0]/2],[mean[1], mean[1]], color = 'b')
				pp.text(mean[0]+std[0]/2+3, mean[1]-2, str(round(std[0],2)))	
				pp.plot([mean[0], mean[0]],[mean[1]-std[1]/2, mean[1]+std[1]/2], color = 'b')
				pp.text(mean[0]-4, mean[1]+std[1]/2+3, str(round(std[1],2)))
				pp.text(mean[0]-6, mean[1]-5, 'P'+str(point))
	pp.xlabel('longitude, m')
	pp.ylabel('latitude, m')
	pp.legend(handles=legend)
	pp.title(logs_name + ' ' + plot_name)
	pp.savefig(pics_dir+logs_name+'/'+logs_name + '_' + plot_name + '.png')
	pp.clf()

def plot_data_test():
	plot_data_2d(prepare_data(test_log.data), test_log.filename, 'trajectories')

def filter_data_2d(data, key1, key2, mode = 'DIFF'):
	x1 = data[key1]
	x2 = data[key2]
	out = {}
	if 'DIFF'==mode:
		sigma_proc = 0.25
		sigma_meas = 30
		x = [map(lambda x,y: x-y, x1[i], x2[i]) for i in range(len(x1))]
		x0 = x[0]
		P0 = np.eye(2)*sigma_proc
		F = np.eye(2)
		Q = np.eye(2)*sigma_proc
		H = np.eye(2)
		R = np.eye(2)*sigma_meas
		kf = kalman_filter(F, Q, H, R, x0, P0)
		out['DIFF('+key1+','+key2+')'] = kf.Apply(x)
	elif 'DUAL'==mode:
		sigma_proc = 1
		sigma_meas = 20
		x = np.concatenate((x1,x2),axis=1)
		x0 = map(lambda x,y: (x+y)/2, x1[0], x2[0]) 
		P0 = np.eye(2)*sigma_proc 
		F = np.eye(2)
		Q = np.eye(2)*sigma_proc
		H = np.concatenate((np.eye(2), np.eye(2)),axis=0)
		R = np.eye(4)*sigma_meas
		kf = kalman_filter(F, Q, H, R, x0, P0)
		out['DUAL('+key1+','+key2+')'] = kf.Apply(x)
	return out

def filter_data_2d_test():
	pdata = convert_to_2d(prepare_data(test_log.data))
	#print filter_data_diff_mode(pdata, 'PRT1', 'BASE')
	plot_data_2d(filter_data_2d(pdata, 'PRT1', 'PRT2','DUAL'), test_log.filename, 'kalman_dual')

def filter_data(data, key1, key2, mode = ('DIFF')):
	filtered_array = filter_data_2d(convert_to_2d(data), key1, key2, mode)
	#plot_data_2d(filtered_array, test_log.filename, 'kalman_dual')
	out = {}
	out.update({mode+'('+key1+','+key2+')':[(data[key1][i][0], data[key1][i][1], filtered_array[mode+'('+key1+','+key2+')'][i][0], filtered_array[mode+'('+key1+','+key2+')'][i][1], data[key1][i][4], data[key1][i][5]) for i in range(len(data[key1]))]})
	return out

def filter_data_test():
	plot_data_2d(convert_to_2d(filter_data(prepare_data(test_log.data), 'BASE', 'PRT2')), test_log.filename, 'kalman_dual')

#merge_data_by_time_test()
#plot_trajectories_test()
#center_point_test()
#shift_data_to_center_point_test()
#filter_data_test()
#print get_point_list(get_point_data(test_log.data, (1,2,3)))
#plot_data(prepare_data(get_key_data(get_point_data(test_log.data, (1,2,3,4,5)),('BASE','PRT2'))), test_log.filename, 'points_std_prt2', ('std','points'))
#plot_data(get_key_data(filter_data(prepare_data(test_log.data), 'PRT2', 'BASE'),('DIFF(PRT2,BASE)')), test_log.filename, 'points_std_prt2_diff', ('std'))



#plot_data(prepare_data(test_log.data),test_log.filename,'GPS raw')
#plot_data(get_point_data(get_key_data(prepare_data(test_log.data), 'PRT1'),(1,2,3,4,5)),test_log.filename,'PRT1 std', 'std')
#plot_data(get_point_data(get_key_data(prepare_data(test_log.data), 'PRT2'),(1,2,3,4,5)),test_log.filename,'PRT2 std', 'std')
#plot_data(shift_data_to_center_point(get_point_data(filter_data(prepare_data(test_log.data), 'PRT1', 'BASE', 'DIFF'),(1,2,3,4,5))),test_log.filename,'DIFF(PRT1,BASE) std', 'std')
#plot_data(shift_data_to_center_point(get_point_data(filter_data(prepare_data(test_log.data), 'PRT2', 'BASE', 'DIFF'),(1,2,3,4,5))),test_log.filename,'DIFF(PRT2,BASE) std', 'std')
#plot_data(get_point_data(filter_data(prepare_data(test_log.data), 'PRT1', 'PRT2', 'DUAL'),(1,2,3,4,5)),test_log.filename,'DUAL(PRT1,PRT2) std', 'std')

#plot_data(prepare_data(test_log.data),test_log.filename,'GPS raw')
#plot_data(get_point_data(get_key_data(prepare_data(test_log.data), 'BASE'),(1,2,3,4,5)),test_log.filename,'BASE std', 'std')
#plot_data(get_point_data(get_key_data(prepare_data(test_log.data), 'PRT1'),(1,2,3,4,5)),test_log.filename,'PRT1 std', 'std')
#plot_data(get_point_data(get_key_data(prepare_data(test_log.data), 'PRT2'),(1,2,3,4,5)),test_log.filename,'PRT2 std', 'std')
#plot_data(get_point_data(filter_data(prepare_data(test_log.data), 'PRT2', 'BASE', 'DUAL'),(1,2,3,4,5)),test_log.filename,'DUAL(PRT2,BASE) std', 'std')
plot_data(get_point_data(filter_data(prepare_data(test_log.data), 'PRT1', 'PRT2', 'DUAL'),(1,2,3,4,5)),test_log.filename,'DUAL(PRT1,PRT2) std', 'std')