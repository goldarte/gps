import pynmea2


class NMEA_GPS_processor:

    """ Parser for NMEA protocol strings"""

    def __init__(self):
        self.data_initialized = False
        self.error_initialized = False
        self.longitude = 0
        self.latitude = 0
        self.hdop = 1
        self.time_data = 0
        self.time_error = 0
        self.reader = pynmea2.NMEAStreamReader()

    def get_data(self):
        if self.data_initialized and self.error_initialized:
            return (True, self.latitude, self.longitude,
                    self.hdop, self.time_data, self.time_error)
        else:
            return(False, 0, 0, 0, 0, 0)

    def add_string(self, message_str):
        try:
            msg_list = self.reader.next(message_str)
            for msg in msg_list:
                if type(msg) == pynmea2.types.talker.GGA:
                    # get coordinates and error data
                    if (msg.lat == '' or msg.lat_dir == ''
                        or msg.lon == '' or msg.lon_dir == ''
                            or msg.horizontal_dil == ''):
                        raise ValueError
                    self.time_data = msg.timestamp
                    self.time_error = msg.timestamp
                    self.latitude = msg.lat + msg.lat_dir
                    self.longitude = msg.lon + msg.lon_dir
                    self.hdop = msg.horizontal_dil
                    self.data_initialized = True
                    self.error_initialized = True
                elif (type(msg) == pynmea2.types.talker.GLL
                      and msg.status == 'A'):
                    # get coordinates only
                    if (msg.lat == '' or msg.lat_dir == ''
                            or msg.lon == '' or msg.lon_dir == ''):
                        raise ValueError
                    self.latitude = msg.lat + msg.lat_dir
                    self.longitude = msg.lon + msg.lon_dir
                    self.time_data = msg.timestamp
                    self.data_initialized = True
                elif (type(msg) == pynmea2.types.talker.RMC
                      and msg.status == 'A'):
                    # get coordinates only (minimal package)
                    if (msg.lat == '' or msg.lat_dir == ''
                            or msg.lon == '' or msg.lon_dir == ''):
                        raise ValueError
                    self.latitude = msg.lat + msg.lat_dir
                    self.longitude = msg.lon + msg.lon_dir
                    self.time_data = msg.timestamp
                    self.data_initialized = True
                elif type(msg) == pynmea2.types.talker.GSA:
                    # get DOP only (without time!) =>
                    # initialization is not completed
                    if msg.hdop == '':
                        raise ValueError
                    self.hdop = msg.hdop
        except pynmea2.nmea.ChecksumError as e:
            print('Checksum error "' + str(e) + '" while processing string '
                  + message_str + '\n')
        except pynmea2.nmea.ParseError as e:
            print('Parce error "' + str(e) +
                  '" while processing string ' + message_str)
        except pynmea2.nmea.SentenceTypeError as e:
            print('Sentence type error "' + str(e) +
                  '" while processing string ' + message_str)
        except ValueError:
            print('Wrong value while processing string ' + message_str)

import re
import math

re_degrees = re.compile('([0-9]{2,3})([0-9]{2})\.([0-9]{2})([0-9]+)([NWSE])')


def transform_degrees_str_to_rad(deg_string):
    """ transform [D]DDMM.SSSSS to radians """
    match_res = re.match(re_degrees, deg_string)
    if match_res is None:
        return None
    else:
        full_deg = int(match_res.group(1))
        minutes = int(match_res.group(2))
        full_sec = int(match_res.group(3))
        frac_sec = float('0.' + match_res.group(4))
        value = full_deg + minutes / 60.0 + (full_sec + frac_sec) / 3600.0
        if match_res.group(5) == 'S' or match_res.group(5) == 'W':
            value = -value
        return value * math.pi / 180.0

assert(math.fabs(transform_degrees_str_to_rad('5548.11233N')
                 - (55 + 48 / 60.0 + 11.233 / 3600.0) * math.pi / 180) < 1e-3)
assert(math.fabs(transform_degrees_str_to_rad('03728.43364E')
                 - (37 + 28 / 60.0 + 43.364 / 3600.0) * math.pi / 180) < 1e-3)
assert(math.fabs(transform_degrees_str_to_rad('12709.49122W')
                 + (127 + 9 / 60.0 + 49.122 / 3600.0) * math.pi / 180) < 1e-3)
assert(transform_degrees_str_to_rad('abW') is None)
assert(transform_degrees_str_to_rad('12709.49122K') is None)
assert(transform_degrees_str_to_rad('12709.49122') is None)
assert(transform_degrees_str_to_rad('12709.49E') is None)


if __name__ == "__main__":
    proc = NMEA_GPS_processor()
    print(proc.get_data())
    proc.add_string('$GPGGA,122539.00,5548.11233,N,03728.43364,E,'
                    + '1,07,1.13,160.6,M,13.4,M,,*57\r\n')
    print(proc.get_data())
    proc.add_string(
        '$GPGGA,122539.00,5548.11233,N,03728.43364,E,'
        + '1,07,1.13,160.6,M,13.4,M,,*58\r\n')
    print(proc.get_data())
    proc.add_string(
        '$GPRMC,122540.00,A,5548.11279,N,03728.43347,E,'
        + '2.104,,020816,,,A*73\r\n')
    print(proc.get_data())
    proc.add_string('$GPGLL,5548.11352,N,03728.43333,E,122541.00,A,A*6A\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,rastrstastrst\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,1225\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,1225,\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,122539.00,\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,122539.00,5548.11233,N,\r\n')
    print(proc.get_data())
    proc.add_string('$GPGGA,122539.00,5548.11233,N,03728.433\r\n')
    print(proc.get_data())
    proc.add_string('$GPGSA,A,3,21,20,26,29,16,18,05,,,,,,'
                    + '2.52,1.13,2.25*04\r\n')
    print(proc.get_data())
    proc.add_string('rstaaiht\r\n')
    proc.add_string('$GPGGA,122539.00,5548.11233,N,03728.43364,E,')
    proc.add_string('1,07,1.13,160.6,M,13.4,M,,*57\r\n')
    print(proc.get_data())
