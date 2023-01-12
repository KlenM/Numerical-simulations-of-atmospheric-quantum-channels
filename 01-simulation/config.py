from pathlib import Path

import numpy as np
from pyatmosphere import gpu

from channels.moderate import moderate_inf, moderate_zap
from channels.strong import strong_inf, strong_zap
from channels.weak import weak_inf, weak_zap

gpu.config['use_gpu'] = True

DATA_PATH = Path('./01-simulation/data')
CHANNELS = {
    'weak_zap': {
        'channel': weak_zap,
        'iterations': 15,
        'aperture_range': [round(x, 5) for x in np.linspace(0.00075, 0.03, 40)]
    },
    'weak_inf': {
        'channel': weak_inf,
        'iterations': 15,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.04, 40)]
    },
    'moderate_zap': {
        'channel': moderate_zap,
        'iterations': 15,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.055, 55)]
    },
    'moderate_inf': {
        'channel': moderate_inf,
        'iterations': 15,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.065, 65)]
    },
    'strong_zap': {
        'channel': strong_zap,
        'iterations': 15,
        'aperture_range': [round(x, 2) for x in np.linspace(0.01, 0.50, 50)]
    },
    'strong_inf': {
        'channel': strong_inf,
        'iterations': 15,
        'aperture_range': [round(x, 2) for x in np.linspace(0.01, 0.50, 50)]
    },
}