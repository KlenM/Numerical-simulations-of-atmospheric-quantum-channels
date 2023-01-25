"Data simulation for channels of different turbulent scintillations."

from pathlib import Path
from typing import List

from lib.parameters import (default_aperture_radiuses, default_aperture_shifts,
                            load_aperture_radiuses, load_aperture_shifts,
                            save_channel_parameters)
from lib.shifted_aperture import ApertureShifts, ShiftedTrackedPDTResult
from pyatmosphere import Channel, CirclePupil, simulations

import config


def create_results(
        channel_name: str,
        channel: Channel,
        aperture_radiuses: List[float],
        aperture_shifts: ApertureShifts,
        iterations: int
        ) -> List[simulations.Result]:
    """Declare the required results for a simultaion.

    Args:
        channel_name: the name of the folder where the results will be stored
        channel: pyatmosphere.Channel which will be simulated
        aperture_radiuses: list of aperture radiuses
        aperture_shifts: list of r_0 values for
                         the numerical total probability PDT models
        iterations: the required number of simulation iterations

    Returns:
        a list of pyatmosphere simulation results
    """
    results_path = Path(config.DATA_PATH) / channel_name
    results_path.mkdir(exist_ok=True)
    (results_path / 'shifted_aperture').mkdir(exist_ok=True)

    apertures = [CirclePupil(radius=r) for r in aperture_radiuses]
    return [
        simulations.BeamResult(
            channel, save_path=(results_path / 'beam.csv'), max_size=iterations
        ),
        simulations.PDTResult(
            channel,
            pupils=apertures,
            save_path=(results_path / 'transmittance.csv'), max_size=iterations
        ),
        simulations.TrackedPDTResult(
            channel,
            pupils=apertures,
            save_path=(results_path / 'tracked_transmittance.csv'),
            max_size=iterations
        ),
        *[ShiftedTrackedPDTResult(
            channel,
            aperture=aperture,
            aperture_shifts=aperture_shifts,
            save_path=(results_path / 'shifted_aperture' /
                       f"transmittance_{aperture.radius}.csv"),
            max_size=iterations
            )
            for aperture in apertures]
    ]


def run():
    "Start a new or continue data simulation"
    Path(config.DATA_PATH).mkdir(exist_ok=True)
    for channel_name, channel_config in config.CHANNELS.items():
        aperture_radiuses = (
            load_aperture_radiuses(channel_name) or
            default_aperture_radiuses(channel_name)
            )
        tracked_shifts = (
            load_aperture_shifts(channel_name) or
            default_aperture_shifts(channel_config['channel'])
            )

        save_channel_parameters(channel_name, channel_config['channel'])
        results = create_results(channel_name, channel_config['channel'],
                                 aperture_radiuses, tracked_shifts,
                                 channel_config['iterations'])
        sim = simulations.Simulation(results)

        # A loop for the ability to get an intermediate output plot with
        # the key combiation "Ctrl + C".
        while True:
            print(f"Runnig '{channel_name}' channel simulation...")
            sim.run(save_step=config.SIMULATION_SAVE_STEP)  # main sim loop

            if sim.is_measures_done():
                break

            for res in sim.results_list:
                res.plot_output()
            if input("\nAbort simulation? (y/N) ").lower().startswith('y'):
                print("Aborting...")
                return


if __name__ == "__main__":
    run()
