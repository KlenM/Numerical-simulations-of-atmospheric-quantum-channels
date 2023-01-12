from typing import Optional, List, Sequence, Tuple, Union
from pathlib import Path
from functools import partial

import numpy as np
import pandas as pd
from pyatmosphere import Channel, CirclePupil, simulations, measures, gpu

from channels.weak import weak_zap, weak_inf
from channels.moderate import moderate_zap, moderate_inf
from channels.strong import strong_zap, strong_inf


gpu.config['use_gpu'] = True


DATA_PATH = Path('../analyse/data')
R0_ITERATIONS = 1000
CHANNELS = {
    'weak_zap': {
        'channel': weak_zap,
        'iterations': 1000,
        'aperture_range': [round(x, 5) for x in np.linspace(0.00075, 0.03, 40)]
    },
    'weak_inf': {
        'channel': weak_inf,
        'iterations': 1000,
        'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.04, 40)]
    },
#     'moderate_zap': {
#         'channel': moderate_zap,
#         'iterations': 1000,
#         'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.055, 55)]
#     },
#     'moderate_inf': {
#         'channel': moderate_inf,
#         'iterations': 1000,
#         'aperture_range': [round(x, 3) for x in np.linspace(0.001, 0.065, 65)]
#     },
    'strong_zap': {
        'channel': strong_zap,
        'iterations': 1000,
        'aperture_range': [round(x, 2) for x in np.linspace(0.01, 0.50, 50)]
    },
    'strong_inf': {
        'channel': strong_inf,
        'iterations': 1000,
        'aperture_range': [round(x, 2) for x in np.linspace(0.01, 0.50, 50)]
    },
}

ApertureRadiusesList = List[float]
ShiftsList = List[Tuple[float, float]]
SimDataInfo = Tuple[ApertureRadiusesList, ShiftsList]


class ShiftedTrackedPDTResult(simulations.Result):
    def __init__(self, channel, aperture_shift: Optional[list] = None,
                 aperture_radius: Optional[float] = None, **kwargs):
        self.aperture_shift = aperture_shift or [(0, 0)]
        if aperture_radius:
            self.aperture = CirclePupil(aperture_radius)
        else:
            self.aperture = None
        beam_measures = [
            simulations.Measure(channel, "atmosphere", measures.mean_x),
            simulations.Measure(channel, "atmosphere", measures.mean_y)
            ]
        eta_measures = [
            simulations.Measure(channel, "atmosphere",
                                partial(self.append_pupil, shift),
                                measures.eta,
                                name=self._col_name(shift))
            for shift in self.aperture_shift
            ]
        super().__init__(channel, beam_measures + eta_measures, **kwargs)

    def _col_name(self, shift):
        return '_'.join(['{:.3e}'.format(n) for n in shift])

    def load_output(self):
        for measures, data in zip(self.measures,
                                  pd.read_csv(self.save_path).T.values):
            measures.data = data.tolist()

    def append_pupil(self, shift, channel, output):
        init_pupil = channel.pupil
        if self.aperture:
            channel.pupil = self.aperture
        beam_x = self.measures[0].iteration_data
        beam_y = self.measures[1].iteration_data
        output = channel.pupil.output(
            output, shift=(beam_x + shift[0], beam_y + shift[1]))
        if self.aperture:
            channel.pupil = init_pupil
        return output

    def plot_output(self):
        print(len(self.measures[0]))


def get_channel_bw(channel_name: str) -> float:
    beam_data = pd.read_csv(Path("../data") / channel_name / 'beam.csv',
                            dtype=float)
    return np.sqrt((beam_data.mean_x**2).mean())


def create_results(
        channel_name: str,
        channel: Channel,
        aperture_radiuses: List[float],
        shifts: List,
        iterations: int
        ) -> List[simulations.Result]:
    """Declare the required results for a simultaion.

    Args:
        channel_name: the name of the folder where the results will be stored
        channel: pyatmosphere.Channel which will be simulated
        aperture_radiuses: list of aperture radiuses
        iterations: the required number of simulation iterations

    Returns:
        SimulationResults: a dictionary of targes pyatmosphere results
    """
    results_path = DATA_PATH / channel_name
    results_path.mkdir(exist_ok=True)
    return [ShiftedTrackedPDTResult(
        channel, aperture_shift=shifts, aperture_radius=radius,
        save_path=results_path / f"totpr_{str(radius).replace(',', '_')}.csv",
        max_size=iterations
        )
        for radius in aperture_radiuses]


def load_sim_data_info(channel_name: str) -> Optional[SimDataInfo]:
    try:
        transm_path = Path('../data') / channel_name / 'transmittance.csv'
        with open(transm_path, "r") as f:
            aperture_radiuses = [float(r) for r in f.readline().split(",")]

        r = aperture_radiuses[0]
        total_prob_path = (DATA_PATH / channel_name /
                           f"totpr_{str(r).replace(',', '_')}.csv")
        with open(total_prob_path, "r") as f:
            shifts = [
                tuple(float(x) for x in c.split('_'))
                for c in f.readline().split(",")[2:]]
    except FileNotFoundError:
        return None
    return aperture_radiuses, shifts


def default_sim_data_info(channel_name: str, channel_data) -> SimDataInfo:
    aperture_radiuses = channel_data['aperture_range']

    def e_round(value: float) -> float:
        "Round a float value to 3 significant digits"
        return float('{:.3e}'.format(value))

    bw = get_channel_bw(channel_name)
    shifts_x = np.random.normal(0, bw, R0_ITERATIONS)
    shifts_y = np.random.normal(0, bw, R0_ITERATIONS)
    shifts = [(e_round(x), e_round(y)) for x, y in zip(shifts_x, shifts_y)]
    return aperture_radiuses, shifts


def run():
    np.random.seed(2511)
    DATA_PATH.mkdir(exist_ok=True, parents=True)
    for channel_name, channel_data in CHANNELS.items():
        radiuses, shifts = (load_sim_data_info(channel_name) or
                            default_sim_data_info(channel_name, channel_data))
        results = create_results(channel_name, channel_data['channel'],
                                 radiuses, shifts,
                                 channel_data['iterations'])
        sim = simulations.Simulation(results)
        while True:
            print(f"Runnig '{channel_name}' channel simulation...")
            sim.run(save_step=200)
            if sim.is_measures_done():
                break
            else:
                # if Simulation.run() has returned due to the KeyboartInterrupt
                for res in sim.results_list:
                    res.plot_output()
                if input("\nAbort simulation? (y/N) ").lower().startswith('y'):
                    print("Aborting...")
                    return


if __name__ == "__main__":
    run()
