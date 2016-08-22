import rospy
from std_msgs.msg import String
import GPSproc
import geodes_tr
import serial
import time
from getchar import getch
import sys
import os
from os.path import isfile, join

def write_com_to_log(com, file):
    out = com.read()
    file.write(out)
    return out

def write_com_to_log_2(com, file1, file2):
    out = com.read()
    file1.write(out)
    file2.write(out)
    return out

def timestamp():
    ct = time.localtime(time.time())
    return "{0:0>2}".format(ct[2]) + "{0:0>2}".format(ct[1]) + "{0:0>2}".format(ct[0] % 100) + '_' + "{0:0>2}".format(ct[3]) + "{0:0>2}".format(ct[4]) + "{0:0>2}".format(ct[5])

def print_info(i1, i2):
    sys.stdout.write('gps base char read: ' + str(i1) + '     gps portable char read: ' + str(
        i2) + '\r')
    sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.flush()

def get_gps_data(serial1, serial2, mode):
	rospy.init_node('process_gps', anonymous=True)
	pub = rospy.Publisher('gps_data', String, queue_size=10)
	rate = rospy.Rate(10) # 10hz
	pd1 = (0, 0, 0, 0, 0, 0)
	pd2 = (0, 0, 0, 0, 0, 0)
	proc1 = GPSproc.NMEA_GPS_processor()
	proc2 = GPSproc.NMEA_GPS_processor()
	while not rospy.is_shutdown():
		proc1.add_string(serial1.read())
		proc2.add_string(serial2.read())
		
		pub.publish()
		rate.sleep()

if __name__ == '__main__':
	com_gps_base = serial.Serial('COM9', 9600, timeout=0)
	com_gps_portable = serial.Serial('COM3', 9600, timeout=0)
	try:
		talker(com_gps_base, com_gps_portable, 'DIFF')
	except rospy.ROSInterruptException:
		pass




