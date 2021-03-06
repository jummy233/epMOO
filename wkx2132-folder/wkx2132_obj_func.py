from moo.idfhandler import EPOutputReader
from typing import List, Dict
import os
from moo.utils import interval_to_list_idx
import re

"""objective functions paras"""
SUMMER_LAMBDA = 0.415
WINTER_LAMBDA = 0.253
EP_TBL = "eplustbl.csv"
EP_OUT_CSV = "eplusout.csv"

"""economic specs"""
wall_and_roof_specs = [  # NOTE: need change for new model.
    [7.1277, 10], [14.2554, 20], [21.3831, 30], [28.5108, 40],
    [35.6385, 50], [42.7662, 60], [49.8939, 70], [57.0216, 80],
    [64.1493, 90], [71.277, 100]]
C_e_wall = 30
C_e_roof = 40

window_specs = [116.51, 266, 163.39]
infiltration_specs = [1000, 900, 800, 700, 600, 500]
ac_specs = [200, 300, 500, 900]
C_e_win = 30
C_i_shading = 500

total_ac_area = 1584.33
surface_area = 1617.58  # wall_area = surface_area - window_area
roof_area = 402.83
# Window area will change accroding to the winwallratio.


def f1_energy_consumption(*args) -> float:
    # Energy consumption.
    pid = str(os.getpid())
    ep_tbl_path = os.path.join(os.path.abspath("temp"), pid, EP_TBL)

    print("running f1 ... in {}".format(os.getpid()))
    cop = (lambda l: lambda x: l[x])([2.0, 2.5, 3.0, 3.5])(
        interval_to_list_idx(int(args[9])))
    building_area: float = 0
    energy_consumption: float = 0
    summer_consumption: float = 0
    winter_consumption: float = 0

    with open(ep_tbl_path, "rb") as f:
        data = [d.decode('utf-8') for d in f.readlines()]

        break_word = False
        building_area_found = False

        for i, _ in enumerate(data):
            if break_word:
                break

            if re.match(r"^Building Area", data[i]) and not building_area_found:
                building_area_found = True
                for line in data[i:]:
                    if re.match(r",Net Conditioned Building Area", line):
                        s = line.split(",")
                        building_area = float(s[2])

            if re.match(r"^End Uses", data[i]):
                print("2 End Uses found: ", data[i])
                for line in data[i:i + 5]:
                    print("Under", line)
                    if re.match(r",Heating,\d+.*", line):
                        s = line.split(",")
                        winter_consumption = float(s[2])

                for line in data[i:i + 5]:
                    if re.match(r",Cooling,\d+.*", line):
                        s = line.split(",")
                        summer_consumption = float(s[2])
                        break_word = True

        energy_consumption = (winter_consumption / cop +
                              summer_consumption / cop) / building_area
    print("log: cop", cop)
    print("log: energy_consumption", energy_consumption)
    print("log: winter_consumption", winter_consumption, os.getpid())
    print("log: summer_consumption", winter_consumption, os.getpid())

    return energy_consumption


def f2_aPMV(*args) -> float:
    rows: Dict = {
        "HEATING": "THERMAL ZONE: SPACE 305 PTHP:Zone Packaged Terminal Heat Pump Total Heating Energy [J](Hourly)",
        "COOLING": "THERMAL ZONE: SPACE 305 PTHP:Zone Packaged Terminal Heat Pump Total Cooling Energy [J](Hourly) ",
        "PMV": "THERMAL ZONE: SPACE 201 PEOPLE:Zone Thermal Comfort Fanger Model PMV [](Hourly)"
    }
    pid = str(os.getpid())
    ep_out_csv_path = os.path.join(os.path.abspath("temp"), pid, EP_OUT_CSV)

    print("running f2 ... in {}".format(os.getpid()))

    # get aPMV
    apmv_avg: float = 0

    with EPOutputReader(ep_out_csv_path) as ep_table:
        pmv_list: List = []
        for row in ep_table.reader:
            if float(row[rows["HEATING"]]) == 0 and \
               float(row[rows["COOLING"]]) == 0:
                pmv_list.append(row[rows["PMV"]])

        pmv_list = list(map(lambda x: float(x), pmv_list))
        pmv_list_summer = list(filter(lambda x: x >= 0, pmv_list))
        # TODO: Pick out 0.
        pmv_list_winter = list(filter(lambda x: x < 0, pmv_list))

        apmv_list = list(
            map(lambda x: abs(x / 1 + SUMMER_LAMBDA * x), pmv_list_summer))
        apmv_list.extend(
            list(map(lambda x: abs(x / 1 - WINTER_LAMBDA * x), pmv_list_winter)))

        apmv_avg = sum(apmv_list) / len(apmv_list)
    return apmv_avg


def f3_economy(*args) -> float:
    pid = str(os.getpid())
    ep_tbl_path = os.path.join(os.path.abspath("temp"), pid, EP_TBL)

    print("running f3 ... in {}".format(os.getpid()))
    wall_id = interval_to_list_idx(args[0])
    roof_id = interval_to_list_idx(args[1]) + 1
    win_id = interval_to_list_idx(args[2])

    infiltration_id = interval_to_list_idx(args[14] - 4)
    cop_id = interval_to_list_idx(int(args[9]))

    local_electircity_fee = 0.53

    window_area: float = 0
    shading_win_area_with_direction: Dict = {
        "east_win_area": 0,
        "west_win_area": 0,
        "south_win_area": 0,
        "north_win_area": 0,
    }

    with open(ep_tbl_path, "r") as f:
        data = f.readlines()

        for i, _ in enumerate(data):
            if "Yes" in data[i] and "EASTWINDOW" in data[i]:
                shading_win_area_with_direction["east_win_area"] += float(
                    data[i].split(",")[3])
            if "Yes" in data[i] and "WESTWINDOW" in data[i]:
                shading_win_area_with_direction["west_win_area"] += float(
                    data[i].split(",")[3])
            if "Yes" in data[i] and "SOUTHWINDOW" in data[i]:
                shading_win_area_with_direction["south_win_area"] += float(
                    data[i].split(",")[3])
            if "Yes" in data[i] and "NORTHWINDOW" in data[i]:
                shading_win_area_with_direction["north_win_area"] += float(
                    data[i].split(",")[3])

            if "Window-Wall Ratio" in data[i]:
                for line in data[i:]:
                    if "Window Opening Area [m2]" in line:
                        s = line.split(",")
                        window_area = float(s[2])

    wall_area = surface_area - window_area

    C_i_wall = wall_and_roof_specs[wall_id][0]
    C_i_roof = wall_and_roof_specs[roof_id][0]  # NOTE economic
    C_i_win = window_specs[win_id]
    delta_wall = wall_and_roof_specs[wall_id][1]
    delta_roof = wall_and_roof_specs[roof_id][1]

    divident = sum([
        (C_i_wall * delta_wall + C_e_wall) * wall_area,
        (C_i_win + C_e_win) * window_area,
        (C_i_roof * delta_roof + C_e_roof) * roof_area,
        (lambda d: sum(d.values()) * C_i_shading)(shading_win_area_with_direction)
    ])

    C_in = divident / total_ac_area + \
        infiltration_specs[infiltration_id] + ac_specs[cop_id]
    C_o = f1_energy_consumption(
        *args) * local_electircity_fee * (1 - (1 + 0.049) ** -20) / 0.049
    LCC = C_in + C_o

    return LCC
