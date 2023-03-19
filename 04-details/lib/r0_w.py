import numpy as np

from lib import data


def r0_w2r_correlation(channel_name: str):
    return np.corrcoef(
        data.r_0(channel_name),
        data.W2_r(channel_name),
        )[0, 1]


def r0_w2r_correlation_plot(ax, channel_name: str):
    ax.hist2d(
        data.r_0(channel_name),
        data.W2_r(channel_name),
        bins=100)
    return ax


def x0_w2i_correlation(channel_name: str):
    W2_1_corr = np.corrcoef(
        data.x_0(channel_name),
        data.W2_i(channel_name)['W2_1']
        )[0, 1]
    W2_2_corr = np.corrcoef(
        data.x_0(channel_name),
        data.W2_i(channel_name)['W2_2']
        )[0, 1]
    return (W2_1_corr, W2_2_corr)
