from functools import partial
from typing import List, Optional, Tuple

import pandas as pd
import pyatmosphere as pyatm

ApertureShifts = List[Tuple[float, float]]


class ShiftedTrackedPDTResult(pyatm.simulations.Result):
    """Represents a simulation results of transmittance of ligth propagation
    through the `channel` throug the `aperture` that is placed with
    the `aperture_shifts` offsets relative to the beam centroid of the sample.
    """
    def __init__(self,
                 channel: pyatm.Channel,
                 aperture: Optional[pyatm.CirclePupil] = None,
                 aperture_shifts: Optional[ApertureShifts] = None,
                 **kwargs):
        self.aperture = aperture or None
        self.aperture_shifts = aperture_shifts or [(0, 0)]
        measures = [
            pyatm.simulations.Measure(
                channel, "atmosphere", pyatm.measures.mean_x),
            pyatm.simulations.Measure(
                channel, "atmosphere", pyatm.measures.mean_y),
            *[pyatm.simulations.Measure(channel, "atmosphere",
              partial(self._append_pupil, shift),
              pyatm.measures.eta,
              name=self._col_name(shift)
              )
              for shift in self.aperture_shifts]
            ]
        super().__init__(channel, measures, **kwargs)

    def _col_name(self, shift):
        return '_'.join([f'{n:.3e}' for n in shift])

    def _append_pupil(self, shift, channel, output):
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

    def load_output(self):
        for measures, data in zip(self.measures,
                                  pd.read_csv(self.save_path).T.values):
            measures.data = data.tolist()

    def plot_output(self):
        print(len(self.measures[0]))
