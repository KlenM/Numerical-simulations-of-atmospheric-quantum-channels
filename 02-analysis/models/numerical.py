from typing import cast

import pandas as pd

from .model import NDArrayByAperture, NumericalModel


class TrackedNumericalModel(NumericalModel):
    @property
    def transmittance(self):
        if self._transmittance is not None:
            return self._transmittance

        transmittance = pd.read_csv(self.transmittance_path, dtype=float)
        transmittance.drop(columns=['mean_x', 'mean_y'], inplace=True)
        transmittance.columns = transmittance.columns.astype('float')
        self._transmittance = cast(NDArrayByAperture, transmittance.to_dict('list'))
        return self._transmittance
