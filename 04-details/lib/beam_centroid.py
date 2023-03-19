import numpy as np

from scipy.stats import norm, skew, kurtosis
from scipy.ndimage import gaussian_filter1d

from lib import data


def cumulants(channel_name):
    return {
        'skew': skew(data.x_0(channel_name)),
        'kurtosis': kurtosis(data.x_0(channel_name)),
    }


def beam_centroid_distribution_plot(ax, channel_name, smooth=0):
    numerical, hist_x_axis = np.histogram(data.x_0(channel_name), density=True, bins=200)
    x_axis = (hist_x_axis[1:] + hist_x_axis[:-1]) / 2
    analytical = norm(loc=0, scale=np.sqrt(data.bw2(channel_name)))

    if smooth:
        num_data = gaussian_filter1d(numerical, 2)
    else:
        num_data = numerical

    bar_width = (x_axis[1:] - x_axis[:-1]).mean()
    ax.bar(x_axis, num_data, width=bar_width, label='Simulated data', color='#00baf7')
    ax.plot(x_axis, analytical.pdf(x_axis), lw=2, ls=(4, (5, 3)), color='black',
            alpha=0.95, label=r'Normal distribution $N(0, W_{BW}^2$)')
    ax.set_xlabel(r"Beam-centroid coordinate $x_0$ (m)")
    ax.set_ylabel("Probability density")
    return ax
