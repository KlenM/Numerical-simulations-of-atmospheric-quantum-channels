from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

DATA_PATH = Path('../01-simulation/data')
RESULTS_PATH = Path('../02-analysis/results')
PLOTS_PATH = Path('./plots')

plt.rcParams['axes.axisbelow'] = True
plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams["font.serif"] = "STIX"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

CMAP_COLORS = [(0, (1, 1, 1)), (0.15, (0.737, 0.933, 1)), (0.7, (0, 0.729, 0.969)), (1, (0, 0.729, 0.969))]
CMAP = LinearSegmentedColormap.from_list("mkBlue", CMAP_COLORS, N=20)

SAVEFIG_KWARGS = {
    # "format": "pdf",
    "dpi": 300,
    "bbox_inches": "tight",
    "pad_inches": 0.005
    }
