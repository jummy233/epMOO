from moo.idfhandler import EPOutputReader
from typing import List
import os
from moo.utils import interval_to_list_idx

"""objective functions paras"""
SUMMER_LAMBDA = 0.415
WINTER_LAMBDA = 0.253
EP_TBL = "eplustbl.csv"
EP_OUT_CSV = "eplusout.csv"

"""economic specs"""
wall_and_roof_specs = [
    [14.2554, 20], [21.3831, 30], [28.5108, 40], [35.6385, 50],
    [42.7662, 60], [49.8939, 70], [57.0216, 80], [64.1493, 90]]
C_e_wall = 30
C_e_roof = 40

window_specs = [116.51, 266, 163.39]
C_e_win = 30
total_AC_area = 1174.6
wall_area = 792
roof_area = 484
# NOTE: Window area will change accroding to the winwallratio.


def f1_energy_consumption(*args) -> float:
    # Energy consumption.
    pid = str(os.getpid())
    ep_tbl_path = os.path.join(os.path.abspath("temp"), pid, EP_TBL)

    print("running f1 ... in {}".format(os.getpid()))
    cop = float(args[9])
    energy_consumption: float = 0
    summer_consumption: float = 0
    winter_consumption: float = 0

    with open(ep_tbl_path, "r") as f:
        data = f.readlines()
        for i, _ in enumerate(data):
            if "Utility Use Per Conditioned Floor Area" in data[i]:
                for line in data[i:]:
                    if "HVAC" in line:
                        s = line.split(",")
                        winter_consumption = float(s[5])
                        summer_consumption = float(s[6])
        energy_consumption = winter_consumption / cop + summer_consumption / cop

    return energy_consumption


def f2_aPMV(*args) -> float:
    pid = str(os.getpid())
    ep_out_csv_path = os.path.join(os.path.abspath("temp"), pid, EP_OUT_CSV)

    print("running f2 ... in {}".format(os.getpid()))

    # get aPMV
    apmv_avg: float = 0

    with EPOutputReader(ep_out_csv_path) as ep_table:
        pmv_list: List = []
        for row in ep_table.reader:
            if float(row["BEDROOM2.2:Zone Ideal Loads Zone Total Heating Energy [J](Hourly)"]) == 0 and \
               float(row["BEDROOM2.2:Zone Ideal Loads Zone Total Cooling Energy [J](Hourly)"]) == 0:
                pmv_list.append(row["BEDROOM2.2:Zone Thermal Comfort Fanger Model PMV [](Hourly) "])

        pmv_list = list(map(lambda x: float(x), pmv_list))
        pmv_list_summer = list(filter(lambda x: x >= 0, pmv_list))
        pmv_list_winter = list(filter(lambda x: x < 0, pmv_list))  # TODO: Pick out 0.

        apmv_list = list(map(lambda x: abs(x / 1 + SUMMER_LAMBDA * x), pmv_list_summer))
        apmv_list.extend(list(map(lambda x: abs(x / 1 - WINTER_LAMBDA * x), pmv_list_winter)))

        apmv_avg = sum(apmv_list) / len(apmv_list)
    return apmv_avg


def f3_economy(*args) -> float:
    pid = str(os.getpid())
    ep_tbl_path = os.path.join(os.path.abspath("temp"), pid, EP_TBL)

    print("running f3 ... in {}".format(os.getpid()))
    wall_id = interval_to_list_idx(args[0])
    roof_id = interval_to_list_idx(args[1])
    win_id = interval_to_list_idx(args[2])

    window_area: float = 0

    with open(ep_tbl_path, "r") as f:
        data = f.readlines()
        for i, _ in enumerate(data):
            if "Window-Wall Ratio" in data[i]:
                for line in data[i:]:
                    if "Window Opening Area [m2]" in line:
                        s = line.split(",")
                        window_area = float(s[2])

    C_i_wall = wall_and_roof_specs[wall_id][0]
    C_i_roof = wall_and_roof_specs[roof_id][0]
    C_i_win = window_specs[win_id]
    delta_wall = wall_and_roof_specs[wall_id][1]
    delta_roof = wall_and_roof_specs[roof_id][1]

    divident = (C_i_wall * delta_wall + C_e_wall) * wall_area + \
               (C_i_win + C_e_win) * window_area + \
               (C_i_roof * delta_roof + C_e_roof) * roof_area
    price = divident / total_AC_area

    return price
