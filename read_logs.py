#!/user/bin/python

# read logs from the directory specified and save coordinates in csv file
import re
import os
import sys
import itertools
import GPSproc
import geodes_tr
from collections import namedtuple

re_fname = re.compile('^GPS_([A-Z0-9]{4})(_P[0-9]+)?')
def get_ftype(fname):
    fn_match = re.search(re_fname, fname)
    if fn_match is None:
        return (False, '', '')
    else:
        pp = None
        if not fn_match.group(2) is None:
            pp = int(fn_match.group(2)[2:])
        return (True, fn_match.group(1), pp)

def key_i5(item):
    return item[5]

# from: http://www.peterbe.com/plog/uniqifiers-benchmark
def f7_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def remove_time_duplicates(time_list):
    res_list = []
    for k,v in itertools.groupby(time_list, key=lambda item: item[5]):
        vl = list(v)
        max_point = max(f7_unique([item[1] for item in vl]))
        mean_la = sum([item[2] for item in vl])/float(len(vl))
        mean_lo = sum([item[3] for item in vl])/float(len(vl))
        mean_gdop = sum([item[4] for item in vl])/float(len(vl))
        res_list.append((vl[0][0], max_point, mean_la, mean_lo, mean_gdop, k))
    return res_list

def merge_data_to_file(data, fname):
    lst_beg = []
    for ks in data.keys():
        lst_beg.extend(data[ks])
    lst_beg.sort(key = key_i5)
    lst_beg = remove_time_duplicates(lst_beg)
    with open(fname,'w') as f:
        for elem in lst_beg:
            td = elem[5].strftime("%H;%M;%S")
            res_str = ';'.join([elem[0], str(elem[1]), 
                                str(elem[2]), str(elem[3]),
                                str(elem[4]), td]) + '\n'
            f.write(res_str)

def prepare_log_data(data):
    lst_beg = []
    for ks in data.keys():
        lst_beg.extend(data[ks])
    lst_beg.sort(key = key_i5)
    lst_beg = remove_time_duplicates(lst_beg)
    return lst_beg
    # lst_beg :: [(B|P, point, lo, la, hdop, time)]

def make_dictionary(data):
    res = {}
    for k in f7_unique([elem[1] for elem in data]):
      res[k] = [e for e in data if e[1]==k]
    return res

def read_log(dirname):
    if not os.path.isdir(dirname):
        print ('Directory "' + dirname + '" not found')
        return {}
    data_points = {}
    re_dirname = re.compile('/([0-9]+)_([0-9]+)')
    dn_match = re.search(re_dirname, dirname)
    if dn_match is None:
        print('Date and time data not found in directory name\n')
        return {}
    date_str = dn_match.group(1)
    time_str = dn_match.group(2)
    for fname in os.listdir(dirname):
        (succ, source, pos) = get_ftype(fname)
        if succ:
            if pos==None:
                pos = -1
            full_name = os.path.join(dirname, fname)
            with open(full_name) as f:
                lines = [l.strip('\n\r') for l in f.readlines()]
                proc = GPSproc.NMEA_GPS_processor()
                results = []
                for ln in lines:
                    proc.add_string(ln + '\r\n')
                    (sc, la, lo, hd, td, te) = proc.get_data()
                    if sc:
                        la_rad = GPSproc.transform_degrees_str_to_rad(la)
                        lo_rad = GPSproc.transform_degrees_str_to_rad(lo)
                        (x,y) = geodes_tr.convert_GPS_to_GKS(la_rad, lo_rad, 158)
                        results.append((source, 
                                        pos, 
                                        y, 
                                        x,
                                        float(hd),
                                        td,
                                        te))
                # save results to structures
                if source not in data_points.keys():
                    data_points[source] = {}
                data_points[source][pos] = results
    filename = date_str+'_'+time_str
    out = None
    out = namedtuple("out", "filename data")
    out.filename = filename
    out.data = {elem:prepare_log_data(data_points[elem]) for elem in data_points.keys()}
    return out
    
