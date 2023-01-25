from typing import Dict, List, Optional, cast

import numpy as np
import numpy.typing as npt
import pandas as pd

NDArrayByAperture = Dict[float, npt.NDArray]

class Model:
    def __init__(self, aperture_radiuses: List[float], bin_edges: NDArrayByAperture):
        self.aperture_radiuses: List[float] = aperture_radiuses
        self.bin_edges: NDArrayByAperture = bin_edges
        self._eta_axis: Optional[NDArrayByAperture] = None
        self._transmittance: Optional[NDArrayByAperture] = None
        self._pdt: Optional[NDArrayByAperture] = None
        self._cdt: Optional[NDArrayByAperture] = None

    @property
    def eta_axis(self) -> NDArrayByAperture:
        if self._eta_axis is not None:
            return self._eta_axis
        self._eta_axis = {
            aperture_radius: (self.bin_edges[aperture_radius][1:] +
                              self.bin_edges[aperture_radius][:-1]) / 2
            for aperture_radius in self.aperture_radiuses
        }
        return self._eta_axis

    @property
    def transmittance(self) -> NDArrayByAperture:
        if self._transmittance is None:
            raise NotImplementedError
        return self._transmittance

    @property
    def pdt(self) -> NDArrayByAperture:
        if self._pdt is not None:
            return self._pdt

        pdt = {}
        for aperture in self.aperture_radiuses:
            transmittance = self.transmittance[aperture]
            bin_edges = self.bin_edges[aperture]
            pdt[aperture] = np.histogram(
                transmittance, bins=bin_edges, density=True)[0]
        self._pdt = pdt
        return self._pdt

    @property
    def cdt(self) -> NDArrayByAperture:
        if self._cdt is not None:
            return self._cdt

        self._cdt = {
            aperture: np.cumsum(
                self.pdt[aperture] * np.diff(self.bin_edges[aperture]))
            for aperture in self.aperture_radiuses
        }
        return self._cdt


class NumericalModel(Model):
    def __init__(self, transmittance_path, beam_data_path,
                 eta_bins=100, **kwargs):
        self.transmittance_path = transmittance_path
        self.beam_data_path = beam_data_path
        self.eta_bins = eta_bins
        self._transmittance = None
        self._beam_data = None

        aperture_radiuses = list(self.transmittance.keys())
        bin_edges = self._get_bin_edges(aperture_radiuses=aperture_radiuses,
                                        eta_bins=eta_bins)
        super().__init__(aperture_radiuses=aperture_radiuses,
                         bin_edges=bin_edges, **kwargs)

    @property
    def beam_data(self) -> pd.DataFrame:
        if self._beam_data is None:
            self._beam_data = pd.read_csv(self.beam_data_path, dtype=float)
        return self._beam_data

    @property
    def beam_params(self):
        return {
            "bw2": (self.beam_data.mean_x**2).mean(),
            "lt2": 4 * self.beam_data.mean_x2.mean(),
            "st2": 4 * (self.beam_data.mean_x2.mean() -
                        (self.beam_data.mean_x**2).mean())
        }

    @property
    def transmittance(self) -> NDArrayByAperture:
        if self._transmittance is not None:
            return self._transmittance

        transmittance = pd.read_csv(self.transmittance_path, dtype=float)
        transmittance.columns = transmittance.columns.astype('float')
        self._transmittance = cast(NDArrayByAperture, transmittance.to_dict('list'))
        return self._transmittance

    def _get_bin_edges(self, aperture_radiuses, eta_bins=100):
        bin_edges = {}
        for aperture_radius in aperture_radiuses:
            radiuses = np.asarray(self.transmittance[aperture_radius])
            left = radiuses.min() * 1 / 1.1
            right = radiuses.max() * 1.1
            if left < 0.1:
                left = 0
            if right > 0.9:
                right = 1
            bin_edges[aperture_radius] = np.linspace(left, right, eta_bins + 1)
        return bin_edges


class AnalyticalModel(Model):
    def __init__(self, numerical_model: NumericalModel):
        self._numerical = numerical_model
        super().__init__(numerical_model.aperture_radiuses,
                         numerical_model.bin_edges)

    @property
    def ks_values(self) -> NDArrayByAperture:
        return {
            aperture: abs(self.cdt[aperture] -
                          self._numerical.cdt[aperture]).max()
            for aperture in self.aperture_radiuses
        }
