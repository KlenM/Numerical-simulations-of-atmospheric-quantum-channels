import numpy as np
from pyatmosphere import (Channel, CirclePupil, GaussianSource,
                          IdenticalPhaseScreensPath, MVKModel,
                          RandLogPolarGrid, RectGrid, SSPhaseScreen)

strong_inf = Channel(
  grid=RectGrid(resolution=2**10, delta=0.0012),
  source=GaussianSource(
      wvl=808e-9,
      w0=0.0508,
      F0=np.inf
  ),
  path=IdenticalPhaseScreensPath(
    phase_screen=SSPhaseScreen(
      model=MVKModel(
        Cn2=5e-15,
        l0=1e-3,
        L0=80,
      ),
      f_grid=RandLogPolarGrid(
        points=2**10,
        f_min=1 / 80 / 15,
        f_max=1 / 1e-3 * 2
      )
    ),
    length=10.2e3,
    count=15
  ),
  pupil=CirclePupil(
    radius=0.15
  ),
)


strong_zap = Channel(
  grid=RectGrid(resolution=2**10, delta=0.0012),
  source=GaussianSource(
      wvl=808e-9,
      w0=0.0508,
      F0=10.2e3
  ),
  path=IdenticalPhaseScreensPath(
    phase_screen=SSPhaseScreen(
      model=MVKModel(
        Cn2=5e-15,
        l0=1e-3,
        L0=80,
      ),
      f_grid=RandLogPolarGrid(
        points=2**10,
        f_min=1 / 80 / 15,
        f_max=1 / 1e-3 * 2
      )
    ),
    length=10.2e3,
    count=15
  ),
  pupil=CirclePupil(
    radius=0.15
  ),
)
