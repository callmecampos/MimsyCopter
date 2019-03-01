import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
import numpy as np

from math import pi, sin, cos, tan

class Pulse:
    def __init__(self, begin, prev_time, post_time, curr_time, angle):
        self.begin = begin
        self.prev = prev_time
        self.post = post_time
        self.time = curr_time
        self.angle = angle

    def __repr__(self):
        return "(curr: {}, angle: {})".format(self.time - self.begin, self.angle)

def get_pulses(filename):
    file = open(filename, "r", errors = "replace")

    pulses = []
    time = []
    orientation = []
    lh_orientation = []
    lines = [line for line in file]

    begin = int(lines[0].split(" ")[3].split(",")[0]) / 32768.0

    for i, line in enumerate(lines):
        if line.split(" ")[0] == "Orientation:" and "?" not in line:
            prev_line, post_line = lines[i-1], lines[i+1]
            t1 = int(prev_line.split(" ")[3].split(",")[0]) / 32768.0
            t2 = int(post_line.split(" ")[3].split(",")[0]) / 32768.0

            t = int(line.split(" ")[1].split(",")[0])/32768.0
            angle = int(line.split(" ")[2]) / 1000.0	# divide by 1000 to convert to radians

            pulses.append(Pulse(begin, t1, t2, t, angle))

    return pulses

# print(matched_angles)

def compute_distance(t_b, t_f, phi=.314164, d=1.3843):
    theta_f = t_f - phi
    theta_b = pi - (t_b - phi)
    theta_L = t_b - t_f

    law = d / sin(theta_L)
    dist_B = law * sin(theta_f)
    dist_F = law * sin(theta_b)

    xb = dist_B * cos(theta_b)
    xf = d - dist_F * cos(theta_f)
    yb = dist_B * sin(theta_b)
    yf = dist_F * sin(theta_f)

    # print("d / sin(theta_L) = {} \n\n dist_B = {} \t (x {} y {}) \n dist_F = {} \t (x {} y {})\n".format(law, dist_B, xb, yb, dist_F, xf, yf))

    assert xb - xf < 0.00001 and yb - yf < 0.00001
    return xb, yb

def plot_files(d=1.3843, brian = "drone_spin_b.txt", felipe = "drone_spin_f.txt", baseline=None, phi=.314164):
    pulse_b = get_pulses(brian)
    pulse_f = get_pulses(felipe)

    heading = phi
    if baseline:
        file = open(baseline, "r", errors = "replace")

        heading, count = 0, 0
        for line in file:
            heading += int(line.split(" ")[4]) / 1000.0
            count += 1

        heading /= float(count)

    poses, valid_pulses = [], []
    for i, b in enumerate(pulse_b):
        for j, f in enumerate(pulse_f):
            # match pulses
            if abs(b.time - f.time) < 1:
                pulse_b[i].begin = pulse_f[j].begin
                poses.append(compute_distance(b.angle, f.angle, phi=heading, d=d))
                valid_pulses.append((b, f))
                break

    return poses, heading, pulse_b, pulse_f, valid_pulses
