import numpy as np
import pandas as pd
from pyatmosphere.theory.pdt import (beta_pdt,
                                     elliptic_beam_numerical_transmission,
                                     lognormal_pdt)

from .model import AnalyticalModel


class NumEllipticalBeamModel(AnalyticalModel):
    def calculate_transmittance(self, iterations: int, grid_resolution: int):
        transmittance = elliptic_beam_numerical_transmission(
            self._numerical.beam_data.sample(iterations), # type: ignore
            self.aperture_radiuses,
            grid_resolution, is_tracked=False
        )
        self._pdt = None
        self._cdt = None
        self._transmittance = dict(zip(self.aperture_radiuses, transmittance))

    @property
    def transmittance(self):
        if not self._transmittance:
            raise Exception(
                "Run EllipticBeamModel().calculate_transmittance(...) "
                "to calculate transmittance"
                )
        return self._transmittance


class NumTotalProbabilityModel(AnalyticalModel):
    def __init__(self, totprob_path, *args, **kwargs):
        self.totprob_path = totprob_path
        super().__init__(*args, **kwargs)

    def tracked_model(self, *args, **kwargs):
        return lognormal_pdt(*args, **kwargs)

    @property
    def pdt(self):
        if self._pdt is not None:
            print("return pdt")
            return self._pdt

        print("calc pdt")
        transmittance = {}
        for aperture_path in self.totprob_path.glob('transmittance_*.csv'):
            aperture = float(
                '.'.join(aperture_path.name.split('_')[1].split('.')[:-1]))
            transmittance[aperture] = pd.read_csv(aperture_path).drop(['mean_x', 'mean_y'], axis=1)

        pdt = {}
        for aperture_path in self.totprob_path.glob('transmittance_*.csv'):
            aperture = float(
                '.'.join(aperture_path.name.split('_')[1].split('.')[:-1]))
            pdt[aperture] = np.asarray([
                self.tracked_model(self.eta_axis[aperture], shift_data.mean(), (shift_data**2).mean())
                for shift_data in transmittance[aperture].values.T
            ]).mean(axis=0)

        self._cdt = None
        self._pdt = pdt
        return self.pdt


class NumBetaTotalProbabilityModel(NumTotalProbabilityModel):
    def tracked_model(self, *args, **kwargs):
        return beta_pdt(*args, **kwargs)
