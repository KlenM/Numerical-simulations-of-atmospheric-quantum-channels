import numpy as np
from channels.moderate import moderate_inf, moderate_zap
from channels.strong import strong_inf
from channels.weak import weak_inf, weak_zap
from pyatmosphere import gpu

gpu.config['use_gpu'] = True

DATA_PATH = './data'
SIMULATION_SAVE_STEP = 500
CHANNELS = {
    'weak_zap': {
        'channel': weak_zap,
        'iterations': 100000,
        'aperture_range': [round(x, 5) for x in np.linspace(0.00075, 0.03, 40)]
    },
    'weak_inf': {
        'channel': weak_inf,
        'iterations': 100000,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.04, 40)]
    },
    'moderate_zap': {
        'channel': moderate_zap,
        'iterations': 100000,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.055, 55)]
    },
    'moderate_inf': {
        'channel': moderate_inf,
        'iterations': 100000,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.065, 65)]
    },
    'strong_inf': {
        'channel': strong_inf,
        'iterations': 100000,
        'aperture_range': [round(x, 2) for x in np.linspace(0.05, 1.5, 30)]
    },
}

SEMIANALYTICAL_ITERATIONS = 5000

# to determine the beam wandering value
PRELIMINARY_SIMULATION_ITERATIONS = 1000

# for the numerical total probability models
R0_VALUES_COUNT = 1000
