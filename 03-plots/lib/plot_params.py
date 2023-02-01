from dataclasses import dataclass
from typing import Optional


@dataclass
class PlotParams:
    name: Optional[str] = None
    label: Optional[str] = None
    color: str = "k"
    linestyle: str = "-"
    clip_tails: float = 0.1
    smooth: float = 0
    ks_smooth: float = 0
    label_pos: int = 0
    label_dx: float = 0
    label_dy: float = 0
    zorder: int = 0


@dataclass
class NumericalPlotParams(PlotParams):
    name: str = "numerical"
    label: Optional[str] = "N"
    zorder: int = 8


@dataclass
class TrackedNumericalPlotParams(PlotParams):
    name: str = "tracked_numerical"
    label: Optional[str] = "R"
    color: str = "#555555"
    zorder: int = 7


@dataclass
class LognormalPlotParams(PlotParams):
    name: str = "lognormal"
    label: Optional[str] = "L"
    color: str = "#e53935"
    zorder: int = 4


@dataclass
class BeamWanderingPlotParams(PlotParams):
    name: str = "beam_wandering"
    label: Optional[str] = "W"
    color: str = "#fb8c00"
    zorder: int = 1


@dataclass
class EllipticalBeamPlotParams(PlotParams):
    name: str = "elliptical_beam"
    label: Optional[str] = "E"
    color: str = "#d81b60"
    zorder: int = 2


@dataclass
class TotalProbabilityPlotParams(PlotParams):
    name: str = "total_probability"
    label: Optional[str] = "$\\mathsf{T_L}$"
    color: str = "#00897b"
    zorder: int = 3

@dataclass
class BetaPlotParams(PlotParams):
    name: str = "beta"
    label: Optional[str] = "B"
    color: str = "#3949ab"
    zorder: int = 6

@dataclass
class BetaTotalProbabilityPlotParams(PlotParams):
    name: str = "beta_total_probability"
    label: Optional[str] = "$\\mathsf{T_B}$"
    color: str = "#e28544"
    zorder: int = 5


@dataclass
class NumTotalProbabilityPlotParams(PlotParams):
    name: str = "num_total_probability"
    label: Optional[str] = "$\\mathsf{T_L}$"
    color: str = "#00897b"
    linestyle: str = "--"
    zorder: int = 3

@dataclass
class NumBetaTotalProbabilityPlotParams(PlotParams):
    name: str = "num_beta_total_probability"
    label: Optional[str] = "$\\mathsf{T_B}$"
    color: str = "#e28544"
    linestyle: str = "--"
    zorder: int = 5

@dataclass
class NumEllipticalBeamPlotParams(PlotParams):
    name: str = "num_elliptical_beam"
    label: Optional[str] = "E"
    color: str = "#d81b60"
    linestyle: str = "--"
    zorder: int = 3
