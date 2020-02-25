import csv
import argparse
from math import degrees, atan2
import re


# argparser = argparse.ArgumentParser('bearings')
# argparser.add_argument('--input', required=True)
# argparser.add_argument('--images')

# print(argparser)


def calculate_bearing(x, y, center_x, center_y):
    angle = degrees(atan2(y - center_y, x - center_x))
    bearing2 = (90 - angle) % 360
    return bearing2

def get_number(instr):
    return re.search(r'\d+', instr).group()


infile = r'\\Ag-server\aguk\Work\Projects\3302_01 - Flimby Flood Modelling\SURVEY\N4CE\PENY01.csv'

ids_done = []

with open(infile, newline='') as infile_open_1:
    reader = csv.reader(infile_open_1)
    

    for ph_id, code1, e1, n1, h1, dim11, dim21, dim31, dim41, rem1 in reader:
        if ph_id in ids_done:
            continue
        # Loop again to find the second point
        with open(infile, newline='') as infile_open_2:
            reader2 = csv.reader(infile_open_2)
            for ph_id2, code2, e2, n2, h2, dim12, dim22, dim32, dim42, rem2 in reader2:
                if ph_id == ph_id2 and code1 != code2:
                    if get_number(code2) > get_number(code2):
                        x, y, centre_x, centre_y = float(e1), float(n1), float(e2), float(n2)
                    else:
                        x, y, centre_x, centre_y = float(e2), float(n2), float(e1), float(n1)
                    bearing = calculate_bearing(x, y, centre_x, centre_y)
                    print(ph_id, bearing)
        ids_done.append(ph_id)













