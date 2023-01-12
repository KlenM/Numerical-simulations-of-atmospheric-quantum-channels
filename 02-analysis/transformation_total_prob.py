from pathlib import Path

import numpy as np
import pandas as pd

from pyatmosphere.theory.pdt import lognormal_pdt, bayesian_pdt, beta_pdt

from transformation import Model, NumericalModel, AnalyticalModel


class NumTotalProbabilityModel(AnalyticalModel):
    tracked_model = lambda _, *args, **kwargs: lognormal_pdt(*args, **kwargs)

    def __init__(self, totprob_path, *args, **kwargs):
        self.totprob_path = totprob_path
        super().__init__(*args, **kwargs)

    @property
    def pdt(self):
        if self._pdt is not None:
            return self._pdt

        transmittance = {}
        for aperture_path in self.totprob_path.glob('totpr_*.csv'):
            aperture = float(aperture_path.name[6:-4])
            transmittance[aperture] = pd.read_csv(aperture_path).drop(['mean_x', 'mean_y'], axis=1)

        pdt = {}
        for aperture_path in self.totprob_path.glob('totpr_*.csv'):
            aperture_radius = float(aperture_path.name[6:-4])
            pdt[aperture_radius] = np.asarray([
                self.tracked_model(self.eta_axis[aperture_radius], shift_data.mean(), (shift_data**2).mean())
                for shift_data in transmittance[aperture_radius].values.T
            ]).mean(axis=0)

        self._cdt = None
        self._pdt = pdt
        return self.pdt


class NumBetaTotalProbabilityModel(NumTotalProbabilityModel):
    tracked_model = lambda _, *args, **kwargs: beta_pdt(*args, **kwargs)


def process_channel(channel_name, eta_bins=200):
    print(f"Processing '{channel_name}' channel...")
    transmittance_path = Path("../data") / channel_name / "transmittance.csv"
    beam_data_path = Path("../data") / channel_name / "beam.csv"
    totprob_path = Path("../analyse/data") / channel_name
    channel_path = Path("../analyse/results") / channel_name

    # Define models
    numerical = NumericalModel(transmittance_path, beam_data_path,
                               eta_bins=eta_bins)
    models = {
        "num_total_probability": NumTotalProbabilityModel(totprob_path, numerical),
        "num_beta_total_probability": NumBetaTotalProbabilityModel(totprob_path, numerical)
    }

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

    print("Data has been stored.")


def run():
    channels = ['weak_inf', 'weak_zap',
                'moderate_inf', 'moderate_zap',
                'strong_inf', 'strong_zap']

    for channel_name in channels:
        process_channel(channel_name)


if __name__ == "__main__":
    run()
