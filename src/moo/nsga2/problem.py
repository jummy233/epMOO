from moo.nsga2.individual import Individual
import random
import copy


class Problem:

    def __init__(self, objectives, num_of_variables, variables_range, expand=True, same_range=False, preamble=None):
        self.num_of_objectives = len(objectives)
        self.num_of_variables = num_of_variables
        self.objectives = objectives
        self.expand = expand
        self.variables_range = []
        self.preamble = preamble
        if same_range:
            for _ in range(num_of_variables):
                self.variables_range.append(variables_range[0])
        else:
            self.variables_range = variables_range

    def generate_individual(self):
        individual = Individual()
        individual.features = [random.uniform(*x) for x in self.variables_range]
        return individual

    def calculate_objectives(self, individual):
        if self.preamble:       # run preamble function.
            self.preamble(*individual.features)
        if self.expand:
            individual.objectives = [f(*individual.features) for f in self.objectives]
        else:
            individual.objectives = [f(individual.features) for f in self.objectives]
        return copy.deepcopy(individual)

