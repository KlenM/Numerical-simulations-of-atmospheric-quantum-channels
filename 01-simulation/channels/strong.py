import numpy as np
from pyatmosphere import (Channel, CirclePupil, GaussianSource,
                          IdenticalPhaseScreensPath, MVKModel,
                          RandLogPolarGrid, RectGrid, SSPhaseScreen)


strong_inf = Channel(
    grid=RectGrid(resolution=2**12, delta=0.001),
        source=GaussianSource(
        wvl=808e-9,
        w0=0.06,
        F0=50e3
        ),
    path=IdenticalPhaseScreensPath(
        phase_screen=SSPhaseScreen(
            model=MVKModel(
            Cn2=6e-16,
            l0=1e-3,
            L0=80,
            ),
        f_grid=RandLogPolarGrid(
            points=2**10,
            f_min=1 / 80 / 15,
            f_max=1 / 1e-3 * 2
            )
        ),
        length=50e3,
        count=30
        ),
    pupil=CirclePupil(
        radius=1.8
        ),
    )
