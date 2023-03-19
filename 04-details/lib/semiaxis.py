from typing import Optional, Tuple
import numpy as np
from matplotlib import patches
from matplotlib import transforms

from lib import data
import config


def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])

    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = patches.Ellipse((0, 0),
        width=ell_radius_x * 2,
        height=ell_radius_y * 2,
        facecolor=facecolor,
        **kwargs)

    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def W2_1_W2_2_plot(ax, channel_name, range: Optional[Tuple[float, float]] = None):
    hist_range = [range, range] if range else None
    ax.hist2d(
        data.W2_i(channel_name)['W2_1'],
        data.W2_i(channel_name)['W2_2'],
        range=hist_range, bins=200, density=True, cmap=config.CMAP)
    confidence_ellipse(
        data.W2_i(channel_name)['W2_1'],
        data.W2_i(channel_name)['W2_2'],
        ax, edgecolor='k', n_std=2.0, ls=(0, (14, 11)), zorder=10)
    ax.set_aspect('equal', 'datalim')
    ax.set_ylabel("Square of semiaxis $W^2_1$ (m)")
    ax.set_xlabel("Square of semiaxis $W^2_2$ (m)")

def theta_1_theta_2_plot(ax, channel_name, range: Optional[Tuple[float, float]] = None):
    hist_range = [range, range] if range else None
    ax.hist2d(
        data.theta_i(channel_name)['theta_1'],
        data.theta_i(channel_name)['theta_2'],
        range=hist_range, bins=200, density=True, cmap=config.CMAP)
    confidence_ellipse(
        data.theta_i(channel_name)['theta_1'],
        data.theta_i(channel_name)['theta_2'],
        ax, edgecolor='k', n_std=2.0, ls=(0, (14, 11)), zorder=10)
    ax.set_aspect('equal', 'datalim')
    ax.set_ylabel(r"??? $\theta_1$ (m)")
    ax.set_xlabel(r"Logarithm of squared semiaxis $\theta_2$ (m)")


def rotated_theta_1_theta_2_correlation(channel_name):
    theta_rot_1 = (data.theta_i(channel_name)['theta_1'] +
                   data.theta_i(channel_name)['theta_2']) / np.sqrt(2)
    theta_rot_2 = (data.theta_i(channel_name)['theta_1'] -
                   data.theta_i(channel_name)['theta_2']) / np.sqrt(2)
    return {
        '(t1 + t2) / sqrt(2)': {
            'mean': theta_rot_1.mean(),
            'var': theta_rot_1.var(),
            'skew': theta_rot_1.skew(),
            'kurt': theta_rot_1.kurt(),
        },
        '(t1 - t2) / sqrt(2)': {
            'mean': theta_rot_2.mean(),
            'var': theta_rot_2.var(),
            'skew': theta_rot_2.skew(),
            'kurt': theta_rot_2.kurt(),
        }
    }
