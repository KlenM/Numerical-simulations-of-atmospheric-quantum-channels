"Data simulation for channels of different turbulent scintillations."

from typing import List, Optional

from pyatmosphere import Channel, CirclePupil, simulations

from . import config


def load_aperture_radiuses(channel_name: str) -> Optional[List[float]]:
    "Load aperture radiuses from the transmittance file if exists."
    try:
        with open(config.DATA_PATH / channel_name / 'transmittance.csv', "r") as f:
            return [float(r) for r in f.readline().split(",")]
    except FileNotFoundError:
        return None


def create_results(
        channel_name: str,
        channel: Channel,
        aperture_radiuses: List[float],
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
    results_path = config.DATA_PATH / channel_name
    results_path.mkdir(exist_ok=True)
    return [
        simulations.BeamResult(
            channel, save_path=(results_path / 'beam.csv'), max_size=iterations
        ),
        simulations.PDTResult(
            channel,
            pupils=[CirclePupil(radius=r) for r in aperture_radiuses],
            save_path=(results_path / 'transmittance.csv'), max_size=iterations
        ),
        simulations.TrackedPDTResult(
            channel,
            pupils=[CirclePupil(radius=r) for r in aperture_radiuses],
            save_path=(results_path / 'tracked_transmittance.csv'),
            max_size=iterations
        )
    ]


def run():
    "Start a new or continue data simulation"
    config.DATA_PATH.mkdir(exist_ok=True)
    for channel_name, channel_data in config.CHANNELS.items():
        channel = channel_data['channel']
        aperture_radiuses = (load_aperture_radiuses(channel_name) or
                             channel_data['aperture_range'])
        results = create_results(channel_name, channel, aperture_radiuses,
                                 channel_data['iterations'])
        sim = simulations.Simulation(results)
        while True:
            print(f"Runnig '{channel_name}' channel simulation...")
            sim.run(save_step=10)
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
