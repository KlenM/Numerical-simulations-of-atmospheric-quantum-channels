import json
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pyatmosphere as pyatm

import config


def _simulate_bw(channel: pyatm.Channel, iterations: int) -> float:
    """Starts a simulation of the beam wandering value for the channel

    Args:
        channel: a channel to simulate
        iterationa: the number of iterations in the simulation

    Returns:
        float: a simulated beam wandering value for this channel in meters
    """
    beam_result = pyatm.simulations.BeamResult(channel, max_size=iterations)
    sim = pyatm.simulations.Simulation([beam_result])
    print("Preliminary simulation...")
    sim.run()
    print(f"Beam wandering value is {beam_result.bw[0]:.1e} m.")
    return beam_result.bw[0]


def load_aperture_radiuses(channel_name: str) -> Optional[List[float]]:
    "Load aperture radiuses from the transmittance data file if exists."
    try:
        path = Path(config.DATA_PATH) / channel_name / 'transmittance.csv'
        with open(path, "r", encoding='utf-8') as file:
            return [float(r) for r in file.readline().split(",")]
    except FileNotFoundError:
        return None


def load_aperture_shifts(channel_name) -> Optional[List[Tuple[float, float]]]:
    "Load aperture shifts for the numerical total probability models if exist."
    shited_aperture_paths = list((Path(config.DATA_PATH) / channel_name /
                                 "shifted_aperture").glob("transmittance_*.csv"))
    if not shited_aperture_paths:
        return None

    # Pick the first arbitrary file. The parameters must be the same.
    with open(shited_aperture_paths[0], "r", encoding='utf-8') as file:
        return [
            tuple(float(x) for x in c.split('_'))
            for c in file.readline().split(",")[2:]
            ]


def default_aperture_radiuses(channel_name) -> List[float]:
    "Take the default values from the config file"
    return config.CHANNELS[channel_name]['aperture_range']


def default_aperture_shifts(channel) -> List[Tuple[float, float]]:
    "Generate aperture shifts for the numerical total probability models."
    def e_round(value: float) -> float:
        "Round a float value to 3 significant digits"
        return float(f'{value:.3e}')

    bw_value = _simulate_bw(channel, config.PRELIMINARY_SIMULATION_ITERATIONS)
    shifts_x = np.random.normal(0, bw_value, config.R0_VALUES_COUNT)
    shifts_y = np.random.normal(0, bw_value, config.R0_VALUES_COUNT)
    return [(e_round(x), e_round(y)) for x, y in zip(shifts_x, shifts_y)]

def save_channel_parameters(channel_name, channel):
    results_path = Path(config.DATA_PATH) / channel_name
    results_path.mkdir(exist_ok=True)
    params = {
        "source": {"W0": channel.source.w0,
                   "wvl": channel.source.wvl,
                   "F0": channel.source.F0},
        "path": {"Cn2": channel.path.phase_screen.model.Cn2,
                 "l0": channel.path.phase_screen.model.l0,
                 "L0": channel.path.phase_screen.model.L0,
                 "length": channel.path.length},
        "aperture": {"radius": channel.pupil.radius},
    }
    with open(results_path / "params.json", "w", encoding="utf-8") as file:
        json.dump(params, file, indent=4)
