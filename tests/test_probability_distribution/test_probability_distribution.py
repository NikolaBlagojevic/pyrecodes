import math
import numpy as np
from pyrecodes.probability_distribution.probability_distribution import Deterministic, Lognormal

class TestProbabilityDistribution:

    def test_deterministic_sampling(self):
        parameters = {'Value': 5}
        dist = Deterministic(parameters)
        assert dist.sample() == 5

    def test_lognormal_median(self):
        num_samples = 100000
        parameters_list = [{'Median': 1, 'Dispersion': 0}, {'Median': 1, 'Dispersion': 1},
                           {'Median': 0.1, 'Dispersion': 1}, {'Median': 5, 'Dispersion': 0.5}]
        target_medians = [1, 1, 0.1, 5]

        for target_median, parameters in zip(target_medians, parameters_list):
            dist = Lognormal(parameters)
            samples = [dist.sample() for _ in range(num_samples)]
            assert math.isclose(target_median, np.median(samples), abs_tol=0.03)

    def test_lognormal_dispersion(self):
        num_samples = 100000
        parameters_list = [{'Median': 1, 'Dispersion': 0}, {'Median': 1, 'Dispersion': 1},
                           {'Median': 0.1, 'Dispersion': 1}, {'Median': 5, 'Dispersion': 0.5}]
        target_dispersions = [0, 1, 1, 0.5]

        for target_dispersion, parameters in zip(target_dispersions, parameters_list):
            dist = Lognormal(parameters)
            samples = [dist.sample() for _ in range(num_samples)]
            assert math.isclose(target_dispersion, np.std(np.log(samples)), abs_tol=0.03)

