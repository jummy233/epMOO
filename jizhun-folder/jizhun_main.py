""" the main program """
import time
from typing import List, Dict
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from moo.nsga2.problem import Problem
from moo.nsga2.evolution import Evolution

from jizhun_obj_func import f1_energy_consumption as f1
from jizhun_obj_func import f2_aPMV as f2
from jizhun_obj_func import f3_economy as f3
# from obj_func_preamble import preamble
from jizhun_preamble import JizhunPreamble

from moo.utils import init
from moo.utils import discrete_interval


def main():
    """parameter"""
    outerwall = discrete_interval((1, 8))  # yield 0-7
    roof = discrete_interval((1, 8))
    window = discrete_interval((1, 3))
    easterate = (0.05, 0.3)
    westrate = (0.05, 0.3)
    southrate = (0.05, 0.3)
    northrate = (0.05, 0.3)
    direction = (0, 359)
    airchange = (0, 39)
    cop = (2.0, 3.5)
    paras = [outerwall, roof, window, easterate, westrate, southrate,
             northrate, direction, airchange, cop]
    """Algorithm parameter"""
    hyperparameter = {
        "MUTATION_PARAM": 2,
        "NUM_OF_GENERATIONS": 3,
        "NUM_OF_INDIVIDUALS": 4,
        "NUM_OF_TOUR_PARTICIPS": 2,
        "CONCURRENCY": True,
        "MAX_PROC": 4
    }

    """other constants"""
    jizhun_constants: Dict = {
        "FLOOR_HEIGHT": 2.8,
        "WINDOW_HEIGHT": 1.5,
        "WINDOW_EDGT_HEIGHT": 1
    }

    """path constants"""
    jizhun_paths: Dict = {
        "WEATHER_FILE": "./WeatherData/CHN_Chongqing.Chongqing.Shapingba.575160_CSWD.epw",
        "IDF_FILE": "jizhun.idf",
        "OUTPUT_PATH": "temp/",
    }

    # main
    moo(paras, hyperparameter, jizhun_constants, jizhun_paths)


def moo(paras: List, hyperparameter: Dict, constants: Dict, paths: Dict):
    init()

    # define problem.
    problem = Problem(num_of_variables=len(paras), objectives=[f1, f2, f3],
                      variables_range=paras,
                      preamble=JizhunPreamble(constants=constants, paths=paths))

    evo = Evolution(
        problem,
        mutation_param=hyperparameter["MUTATION_PARAM"],
        num_of_generations=hyperparameter["NUM_OF_GENERATIONS"],
        num_of_individuals=hyperparameter["NUM_OF_INDIVIDUALS"],
        num_of_tour_particips=hyperparameter["NUM_OF_TOUR_PARTICIPS"],
        concurrency=hyperparameter["CONCURRENCY"],
        max_proc=hyperparameter["MAX_PROC"])

    # draw the last one with 3d box.
    func = [i.objectives for i in evo.evolve()]

    obj1 = [i[0] for i in func]
    obj2 = [i[1] for i in func]
    obj3 = [i[2] for i in func]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(obj1, obj2, obj3, c='r', marker='o')
    plt.draw()
    plt.savefig('results/epMOO_fig.png')
    plt.show()

    print("<Finished>{}".format(time.ctime()))


if __name__ == "__main__":
    main()
