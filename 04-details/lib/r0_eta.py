import numpy as np
from lib import data


def r0_eta_correlation(channel_name: str, is_tracked=False):
    eta = data.tracked_eta(channel_name) if is_tracked else data.eta(channel_name)
    apertures = eta.columns
    correlation = [np.corrcoef(data.r_0(channel_name), eta[aperture])[0, 1]
                   for aperture in apertures]
    normed_apertures = apertures / np.sqrt(data.lt2(channel_name))
    return normed_apertures, correlation

def r0_eta_correlation_plot(ax, channel_name: str, is_tracked=False):
    ax.plot(*r0_eta_correlation(channel_name, is_tracked), label=channel_name)
    ax.set_xlabel(r"Normed aperture radius $R_\mathrm{ap} / \sigma_\mathrm{LT}$")
    ax.set_ylabel("Pearson corr for $r_0$ and $\eta$")
    return ax
