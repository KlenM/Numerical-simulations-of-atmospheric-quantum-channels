
from pyatmosphere.theory.pdt import (
    lognormal_pdt,
    elliptic_beam_numerical_transmission,
    beam_wandering_pdt,
    bayesian_pdt,
    beta_pdt,
    beta_bayesian_pdt
    )


class Model:
    def __init__(self, aperture_radiuses, bin_edges):
        self.aperture_radiuses = aperture_radiuses
        self.bin_edges = bin_edges
        self._eta_axis = None
        self._transmittance = None
        self._pdt = None
        self._cdt = None

    @property
    def transmittance(self):
        if self._transmittance is None:
            raise NotImplementedError
        return self._transmittance

    @property
    def pdt(self):
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
    def cdt(self):
        if self._cdt is not None:
            return self._cdt

        self._cdt = {
            aperture: np.cumsum(
                self.pdt[aperture] * np.diff(self.bin_edges[aperture]))
            for aperture in self.aperture_radiuses
        }
        return self._cdt

    @property
    def eta_axis(self):
        if self._eta_axis is not None:
            return self._eta_axis
        self._eta_axis = {
            aperture_radius: (self.bin_edges[aperture_radius][1:] +
                              self.bin_edges[aperture_radius][:-1]) / 2
            for aperture_radius in self.aperture_radiuses
        }
        return self._eta_axis


class NumericalModel(Model):

    def __init__(self, transmittance_path, beam_data_path,
                 eta_bins=100, **kwargs):
        self.transmittance_path = transmittance_path
        self.beam_data_path = beam_data_path
        self.eta_bins = eta_bins
        self._beam_data = None
        self._transmittance = None

        aperture_radiuses = list(self.transmittance.columns)
        bin_edges = self._get_bin_edges(aperture_radiuses=aperture_radiuses,
                                        eta_bins=eta_bins)
        super().__init__(aperture_radiuses=aperture_radiuses,
                         bin_edges=bin_edges, **kwargs)

    @property
    def beam_data(self):
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
    def transmittance(self):
        if self._transmittance is not None:
            return self._transmittance

        transmittance = pd.read_csv(self.transmittance_path, dtype=float)
        transmittance.columns = transmittance.columns.astype('float')
        self._transmittance = transmittance
        return self._transmittance

    def _get_bin_edges(self, aperture_radiuses, eta_bins=100):
        bin_edges = {}
        for aperture_radius in aperture_radiuses:
            left = self.transmittance[aperture_radius].min() * 1 / 1.1
            right = self.transmittance[aperture_radius].max() * 1.1
            if left < 0.1:
                left = 0
            if right > 0.9:
                right = 1
            bin_edges[aperture_radius] = np.linspace(left, right, eta_bins + 1)
        return bin_edges


class TrackedNumericalModel(NumericalModel):

    @property
    def transmittance(self):
        if self._transmittance is not None:
            return self._transmittance

        transmittance = pd.read_csv(self.transmittance_path, dtype=float)
        transmittance.drop(columns=['mean_x', 'mean_y'], inplace=True)
        transmittance.columns = transmittance.columns.astype('float')
        self._transmittance = transmittance
        return self._transmittance


class AnalyticalModel(Model):

    def __init__(self, numerical_model: NumericalModel):
        self._numerical = numerical_model
        super().__init__(numerical_model.aperture_radiuses,
                         numerical_model.bin_edges)

    @property
    def ks_values(self):
        return {
            aperture: abs(self.cdt[aperture] -
                          self._numerical.cdt[aperture]).max()
            for aperture in self.aperture_radiuses
        }


class EllipticalBeamModel(AnalyticalModel):
    def calculate_transmittance(self, iterations: int, grid_resolution: int):
        transmittance = elliptic_beam_numerical_transmission(
            self._numerical.beam_data.sample(iterations),
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


class BeamWanderingModel(AnalyticalModel):

    @property
    def pdt(self):
        if self._pdt is not None:
            return self._pdt

        pdt = {}
        st2 = self._numerical.beam_params['st2']
        bw2 = self._numerical.beam_params['bw2']
        for aperture_radius in self.aperture_radiuses:
            eta_axis = self.eta_axis[aperture_radius]
            pdt[aperture_radius] = beam_wandering_pdt(
                eta_axis, aperture_radius, st2, bw2)
        self._pdt = pdt
        return self._pdt


class LognormalModel(AnalyticalModel):

    @property
    def pdt(self):
        if self._pdt is None:
            eta_mean = self._numerical.transmittance.mean()
            eta2_mean = (self._numerical.transmittance**2).mean()
            pdt = {}
            for aperture_radius in self.aperture_radiuses:
                pdt[aperture_radius] = lognormal_pdt(
                    self.eta_axis[aperture_radius],
                    eta_mean[aperture_radius],
                    eta2_mean[aperture_radius]
                    )
            self._pdt = pdt
        return self._pdt


class TotalProbabilityModel(AnalyticalModel):

    @property
    def pdt(self):
        if self._pdt is None:
            raise Exception("Run BayesianModel().calculate_pdt(...) "
                            "to calculate pdt")
        return self._pdt

    def calculate_pdt(self, r0_iterations: int):
        eta_mean = self._numerical.transmittance.mean()
        eta2_mean = (self._numerical.transmittance**2).mean()
        st2 = self._numerical.beam_params['st2']
        bw2 = self._numerical.beam_params['bw2']

        pdt = {}
        for aperture_radius in self.aperture_radiuses:
            pdt[aperture_radius] = bayesian_pdt(
                self.eta_axis[aperture_radius], eta_mean[aperture_radius],
                eta2_mean[aperture_radius], aperture_radius,
                st2, bw2, r0_size=r0_iterations
            )
        self._cdt = None
        self._pdt = pdt


class BetaModel(AnalyticalModel):

    @property
    def pdt(self):
        if self._pdt is None:
            eta_mean = self._numerical.transmittance.mean()
            eta2_mean = (self._numerical.transmittance**2).mean()
            pdt = {}
            for aperture_radius in self.aperture_radiuses:
                pdt[aperture_radius] = beta_pdt(
                    self.eta_axis[aperture_radius],
                    eta_mean[aperture_radius],
                    eta2_mean[aperture_radius]
                    )
            self._pdt = pdt
        return self._pdt


class BetaTotalProbabilityModel(AnalyticalModel):

    @property
    def pdt(self):
        if not self._pdt:
            raise Exception("Run BetaBayesianModel().calculate_pdt(...) "
                            "to calculate pdt")
        return self._pdt

    def calculate_pdt(self, r0_iterations: int):
        eta_mean = self._numerical.transmittance.mean()
        eta2_mean = (self._numerical.transmittance**2).mean()
        st2 = self._numerical.beam_params['st2']
        bw2 = self._numerical.beam_params['bw2']
        pdt = {}
        for aperture_radius in self.aperture_radiuses:
            pdt[aperture_radius] = beta_bayesian_pdt(
                self.eta_axis[aperture_radius], eta_mean[aperture_radius],
                eta2_mean[aperture_radius], aperture_radius,
                st2, bw2, r0_size=r0_iterations
            )
        self._pdt = pdt
