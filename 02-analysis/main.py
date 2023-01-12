from pathlib import Path

import ray
import numpy as np
import pandas as pd


@ray.remote
def process_channel(channel_name, eta_bins=200, r0_iterations=100000,
                    transmittance_iterations=100000):
    print(f"Processing '{channel_name}' channel...")
    transmittance_path = Path("../data") / channel_name / "transmittance.csv"
    tracked_path = Path("../data") / channel_name / "tracked_transmittance.csv"
    beam_data_path = Path("../data") / channel_name / "beam.csv"
    channel_path = Path("../results") / channel_name

    # Define models
    numerical = NumericalModel(transmittance_path, beam_data_path,
                               eta_bins=eta_bins)
    models = {
        "numerical": numerical,
        "tracked_numerical": TrackedNumericalModel(
            tracked_path, beam_data_path, eta_bins=eta_bins),
        "elliptical_beam": EllipticalBeamModel(numerical),
        "beam_wandering": BeamWanderingModel(numerical),
        "lognormal": LognormalModel(numerical),
        "total_probability": TotalProbabilityModel(numerical),
        "beta": BetaModel(numerical),
        "beta_total_probability": BetaTotalProbabilityModel(numerical)
    }

    # Some models require explicit calculations
    print("    Calculating 'elliptical beam' model...")
    models["elliptical_beam"].calculate_transmittance(
        iterations=transmittance_iterations, grid_resolution=512)
    print("    Calculating 'total probability' model...")
    models["total_probability"].calculate_pdt(r0_iterations)
    print("    Calculating 'beta total probability' model...")
    models["beta_total_probability"].calculate_pdt(r0_iterations)

    # Store PDT results
    for model_name, model in models.items():
        model_path = channel_path / model_name
        model_path.mkdir(parents=True, exist_ok=True)

        for aperture in model.aperture_radiuses:
            filename = f"{str(aperture).replace('.', '_')}.csv"

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
        for model_name, model in models.items()
        if model_name not in ['numerical', 'tracked_numerical']
    }
    ks_df = pd.DataFrame(ks_values)
    ks_df.index.name = 'aperture_radius'
    ks_df.to_csv(channel_path / 'ks_values.csv', float_format='%.3e')

    # Store beam params
    beam_data = pd.read_csv(beam_data_path)
    pd.DataFrame({
        "bw2": (beam_data.mean_x**2).mean(),
        "st2": 4 * (beam_data.mean_x2.mean() - (beam_data.mean_x**2).mean()),
        "lt2": 4 * beam_data.mean_x2.mean().mean(),
    }, index=[0]).to_csv(channel_path / 'beam_params.csv',
                         float_format='%.3e', index=False)

    print("Data has been stored.")


def run():
    channels = ['weak_inf', 'weak_zap',
                'moderate_inf', 'moderate_zap',
                'strong_inf', 'strong_zap']

    processes = []
    for channel_name in channels:
        processes.append(process_channel.remote(channel_name))
    ray.get(processes)


if __name__ == "__main__":
    run()
