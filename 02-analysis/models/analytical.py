import numpy as np
from pyatmosphere.theory.pdt import (EllipticBeamAnalyticalPDT, bayesian_pdt,
                                     beam_wandering_pdt, beta_bayesian_pdt,
                                     beta_pdt, lognormal_pdt)

from .model import AnalyticalModel


class LognormalModel(AnalyticalModel):
    @property
    def pdt(self):
        if self._pdt is None:
            pdt = {}
            for aperture_radius in self.aperture_radiuses:
                transmittance = np.asarray(
                    self._numerical.transmittance[aperture_radius])
                eta_mean = transmittance.mean()
                eta2_mean = (transmittance**2).mean()
                pdt[aperture_radius] = lognormal_pdt(
                    self.eta_axis[aperture_radius],
                    eta_mean,
                    eta2_mean,
                    )
            self._pdt = pdt
        return self._pdt


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


class EllipticalBeamModel(AnalyticalModel):
    def calculate_transmittance(self, W0: float, iterations: int):
        transmittance = {}

        # To avoid recalculating the parameters, we precalculate it using a dummy model
        beam_data = self._numerical.beam_data
        dummy_eba_pdt = EllipticBeamAnalyticalPDT(W0=W0, a=None, size=None)
        dummy_eba_pdt.set_params_from_data(beam_data['mean_x'], beam_data['mean_x2'], beam_data['mean_y2'])
        bw = dummy_eba_pdt.bw
        theta_mean = dummy_eba_pdt.theta_mean
        theta_cov = dummy_eba_pdt.theta_cov

        for a in self.aperture_radiuses:
            eba_pdt = EllipticBeamAnalyticalPDT(W0=W0, a=a, size=iterations)
            eba_pdt.set_params(bw, theta_mean, theta_cov)
            transmittance[a] = eba_pdt.pdt()
        self._pdt = None
        self._cdt = None
        self._transmittance = transmittance

    @property
    def transmittance(self):
        if not self._transmittance:
            raise Exception(
                "Run EllipticalBeamAnalyticalModel().calculate_transmittance(...) "
                "to calculate transmittance"
                )
        return self._transmittance


class TotalProbabilityModel(AnalyticalModel):
    @property
    def pdt(self):
        if self._pdt is None:
            raise Exception("Run BayesianModel().calculate_pdt(...) "
                            "to calculate pdt")
        return self._pdt

    def calculate_pdt(self, r0_iterations: int):
        st2 = self._numerical.beam_params['st2']
        bw2 = self._numerical.beam_params['bw2']

        pdt = {}
        for aperture_radius in self.aperture_radiuses:
            transmittance = np.asarray(
                self._numerical.transmittance[aperture_radius])
            eta_mean = transmittance.mean()
            eta2_mean = (transmittance**2).mean()
            pdt[aperture_radius] = bayesian_pdt(
                self.eta_axis[aperture_radius], eta_mean, eta2_mean,
                aperture_radius, st2, bw2, r0_size=r0_iterations
            )
        self._cdt = None
        self._pdt = pdt


class BetaModel(AnalyticalModel):
    @property
    def pdt(self):
        if self._pdt is None:
            pdt = {}
            for aperture_radius in self.aperture_radiuses:
                transmittance = np.asarray(
                    self._numerical.transmittance[aperture_radius])
                eta_mean = transmittance.mean()
                eta2_mean = (transmittance**2).mean()
                pdt[aperture_radius] = beta_pdt(
                    self.eta_axis[aperture_radius],
                    eta_mean,
                    eta2_mean,
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
        st2 = self._numerical.beam_params['st2']
        bw2 = self._numerical.beam_params['bw2']
        pdt = {}
        for aperture_radius in self.aperture_radiuses:
            transmittance = np.asarray(
                self._numerical.transmittance[aperture_radius])
            eta_mean = transmittance.mean()
            eta2_mean = (transmittance**2).mean()
            pdt[aperture_radius] = beta_bayesian_pdt(
                self.eta_axis[aperture_radius], eta_mean, eta2_mean,
                aperture_radius, st2, bw2, r0_size=r0_iterations
            )
        self._pdt = pdt
