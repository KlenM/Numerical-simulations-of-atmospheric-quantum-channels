import json
from pathlib import Path

import pandas as pd
import ray

import config
import models


@ray.remote
def process_channel(channel_name, eta_bins=200, r0_iterations=100000,
                    transmittance_iterations=100000):
    print(f"Processing '{channel_name}' channel...")
    results_path = Path(config.RESULTS_PATH) / channel_name
    data_path = Path(config.DATA_PATH) / channel_name
    transmittance_path = data_path / "transmittance.csv"
    tracked_path = data_path / "tracked_transmittance.csv"
    beam_data_path = data_path / "beam.csv"
    shifted_aperture_path = data_path / "shifted_aperture"
    with open(data_path / "params.json", encoding="utf-8") as file:
        channel_parameters = json.load(file)

    # Define models
    numerical = models.NumericalModel(transmittance_path, beam_data_path,
                                      eta_bins=eta_bins)
    _models = {
        # Numerical models
        "numerical": numerical,
        "tracked_numerical": models.TrackedNumericalModel(
            tracked_path, beam_data_path, eta_bins=eta_bins),

        # Analytical models
        "lognormal": models.LognormalModel(numerical),
        "beam_wandering": models.BeamWanderingModel(numerical),
        "elliptical_beam": models.EllipticalBeamModel(numerical),
        "total_probability": models.TotalProbabilityModel(numerical),
        "beta": models.BetaModel(numerical),
        "beta_total_probability": models.BetaTotalProbabilityModel(numerical),

        # Semi-analytical models
        "num_total_probability": models.NumTotalProbabilityModel(
            shifted_aperture_path, numerical),
        "num_beta_total_probability": models.NumBetaTotalProbabilityModel(
            shifted_aperture_path, numerical),
        "num_elliptical_beam": models.NumEllipticalBeamModel(numerical),
    }

    # Some models require explicit calculations
    print("    Calculating 'elliptical_beam beam' model...")
    _models["elliptical_beam"].calculate_transmittance(
        W0=channel_parameters["source"]["W0"],
        iterations=transmittance_iterations
        )
    print("    Calculating 'num_elliptical_beam beam' model...")
    _models["num_elliptical_beam"].calculate_transmittance(
        iterations=transmittance_iterations, grid_resolution=512)
    print("    Calculating 'total probability' model...")
    _models["total_probability"].calculate_pdt(r0_iterations)
    print("    Calculating 'beta total probability' model...")
    _models["beta_total_probability"].calculate_pdt(r0_iterations)

    # Store PDT results
    for model_name, model in _models.items():
        model_path = results_path / model_name
        model_path.mkdir(parents=True, exist_ok=True)

        for aperture in model.aperture_radiuses:
            filename = f"{str(aperture).replace('.', '_')}.csv"
            print(channel_name, model_name, model.pdt.keys())
            pdt_df = pd.DataFrame(
                model.pdt[aperture],
                columns=['probability_density']
            )
            pdt_df.index = pd.Series(
                model.eta_axis[aperture],
                name='transmittance'
                )
            pdt_df.to_csv(model_path / filename, float_format='%.3e')

    # Store KS-values results
    ks_values = {
        model_name: model.ks_values
        for model_name, model in _models.items()
        if model_name not in ['numerical', 'tracked_numerical']
    }
    ks_df = pd.DataFrame(ks_values)
    ks_df.index.name = 'aperture_radius'
    ks_df.to_csv(results_path / 'ks_values.csv', float_format='%.3e')

    # Store beam params
    beam_data = pd.read_csv(beam_data_path)
    pd.DataFrame({
        "bw2": (beam_data.mean_x**2).mean(),
        "st2": 4 * (beam_data.mean_x2.mean() - (beam_data.mean_x**2).mean()),
        "lt2": 4 * beam_data.mean_x2.mean(),
    }, index=[0]).to_csv(results_path / 'beam_params.csv',
                         float_format='%.3e', index=False)

    print("Data has been stored.")


def run():
    channels = ['weak_inf', 'moderate_inf', 'strong_inf',
                'weak_zap', 'moderate_zap']

    processes = []
    for channel_name in channels:
        processes.append(process_channel.remote(
            channel_name,
            eta_bins=config.ETA_BINS,
            r0_iterations=config.R0_VALUES_COUNT,
            transmittance_iterations=config.TRANSMITTANCE_ITERATIONS,
            ))
    ray.get(processes)


if __name__ == "__main__":
    run()
