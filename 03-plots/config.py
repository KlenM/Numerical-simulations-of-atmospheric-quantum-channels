from pathlib import Path

from matplotlib import pyplot as plt

RESULTS_PATH = Path('../02-analysis/results')
PLOTS_PATH = Path('./plots')

plt.rcParams['axes.axisbelow'] = True
plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams["font.serif"] = "STIX"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

SAVEFIG_KWARGS = {
    "format": "pdf",
    "dpi": 300,
    "bbox_inches": "tight",
    "pad_inches": 0.005
    }
