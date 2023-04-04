import json

import fjson
from matplotlib import pyplot as plt

from lib import beam_centroid, r0_w, r0_eta, semiaxis
import config


CHANNELS = ['weak_inf', 'weak_zap', 'moderate_inf', 'moderate_zap', 'strong_inf', 'strong_zap']


def print_beam_centroid_cumulants():
    print("Beam-centroid cumulants:")
    res = {channel_name: beam_centroid.cumulants(channel_name)
           for channel_name in CHANNELS}
    print(json.dumps(res, indent=4))


def plot_beam_centroids_distribution():
    for channel_name in CHANNELS:
        _, ax = plt.subplots(1, 1, figsize=(4, 3))
        beam_centroid.beam_centroid_distribution_plot(ax, channel_name)
        plt.savefig(config.PLOTS_PATH / ('bw_' + channel_name + '.pdf'),
                    **config.SAVEFIG_KWARGS)


def print_r0_W2r_correlation():
    print("r_0 - W2_r correlation:")
    res = {channel_name: r0_w.r0_w2r_correlation(channel_name)
           for channel_name in CHANNELS}
    print(json.dumps(res, indent=4))


def plot_r0_W2r_correlation():
    for channel_name in CHANNELS:
        _, ax = plt.subplots(1, 1, figsize=(4, 3))
        r0_w.r0_w2r_correlation_plot(ax, channel_name)
        plt.savefig(config.PLOTS_PATH / ('r_0_w2_r_' + channel_name + '.pdf'),
                    **config.SAVEFIG_KWARGS)


def print_x0_W2i_correlation():
    print("x_0 - W2_i correlation:")
    res = {channel_name: r0_w.x0_w2i_correlation(channel_name)
           for channel_name in CHANNELS}
    print(json.dumps(res, indent=4))


def plot_r0_eta_correlation(annotations=None):
    KWARGS = {
        'weak_inf': {'ls': '-', 'c': '#e53935'}, 'weak_zap': {'ls': '--', 'c': '#e53935'},
        'moderate_inf': {'ls': '-', 'c': '#3949ab'}, 'moderate_zap': {'ls': '--', 'c': '#3949ab'},
        'strong_inf': {'ls': '-', 'c': '#00897b'}, 'strong_zap': {'ls': '--', 'c': '#00897b'},
        }
    ANNOTATIONS = {
        'untracked': {
            "$\\mathrm{W}_{+\\infty}$": {"text_pos": [-30, -30], "arrow_pos": [0.53, -0.45], "angle_coeff": -1},
            "$\\mathrm{W}_{z_\\mathrm{ap}}$": {"text_pos": [25, -15], "arrow_pos": [1.374, -0.71]},
            "$\\mathrm{M}_{+\\infty}$": {"text_pos": [5, 20], "arrow_pos": [0.47, -0.79]},
            "$\\mathrm{M}_{z_\\mathrm{ap}}$": {"text_pos": [25, -15], "arrow_pos": [0.78, -0.87]},
            "$\\mathrm{S}_{+\\infty}$": {"text_pos": [5, 20], "arrow_pos": [0.23, -0.75]},
            "$\\mathrm{S}_{z_\\mathrm{ap}}$": {"text_pos": [-27, 20], "arrow_pos": [0.23, -0.77], "angle_coeff": -1}
        },
        'tracked': {
            "$\\mathrm{W}_{+\\infty}$": {"text_pos": [26.5, 10], "arrow_pos": [1.13, -0.008], "angle_coeff": -1},
            "$\\mathrm{W}_{z_\\mathrm{ap}}$": {"text_pos": [10, -30], "arrow_pos": [1.45, -0.018]},
            "$\\mathrm{M}_{+\\infty}$": {"text_pos": [-10, -30], "arrow_pos": [1.05, -0.022]},
            "$\\mathrm{M}_{z_\\mathrm{ap}}$": {"text_pos": [-10, -30], "arrow_pos": [0.8, -0.022]},
            "$\\mathrm{S}_{+\\infty}$": {"text_pos": [17, -24], "arrow_pos": [0.177, -0.061]},
            "$\\mathrm{S}_{z_\\mathrm{ap}}$": {"text_pos": [20, -20], "arrow_pos": [0.17, -0.074]}
        },
    }

    # Untracked
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    for channel_name in CHANNELS[:]:
        r0_eta.r0_eta_correlation_plot(ax, channel_name, **KWARGS[channel_name])
    for i, (ann_title, ann_params) in enumerate(ANNOTATIONS['untracked'].items()):
        ax.annotate(
            ann_title, tuple(ann_params['arrow_pos']),
            xytext=tuple(ann_params['text_pos']), textcoords="offset points",
            arrowprops={'arrowstyle': '->',
                        'connectionstyle': f'arc3,rad={ann_params.get("angle_coeff", 1) * -0.3}',
                        'color': ax.get_lines()[i].get_color()},
            color=ax.get_lines()[i].get_color(),
        )
    plt.savefig(config.PLOTS_PATH / ('r_0_eta.pdf'),
                **config.SAVEFIG_KWARGS)

    # Tracked
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    for channel_name in CHANNELS[:]:
        r0_eta.r0_eta_correlation_plot(ax, channel_name, is_tracked=True, **KWARGS[channel_name])
    for i, (ann_title, ann_params) in enumerate(ANNOTATIONS['tracked'].items()):
        ax.annotate(
            ann_title, tuple(ann_params['arrow_pos']),
            xytext=tuple(ann_params['text_pos']), textcoords="offset points",
            arrowprops={'arrowstyle': '->',
                        'connectionstyle': f'arc3,rad={ann_params.get("angle_coeff", 1) * -0.3}',
                        'color': ax.get_lines()[i].get_color()},
            color=ax.get_lines()[i].get_color(),
        )
    plt.ylim(-0.11, 0.01)
    plt.savefig(config.PLOTS_PATH / ('r_0_eta_tracked.pdf'),
                **config.SAVEFIG_KWARGS)


def print_rotated_theta_i():
    print("(theta_1 + theta_2) / sqrt(2) vs (theta_1 - theta_2) / sqrt(2) correlation:")
    res = {channel_name: semiaxis.rotated_theta_1_theta_2_correlation(channel_name)
           for channel_name in CHANNELS}
    print(fjson.dumps(res, float_format='.1e', indent=4))


def plot_W2_i_distribution():
    RANGES = {'weak_inf': (0.0003, 0.0011), 'weak_zap': (0.00016, 0.00035),
              'moderate_inf': (0.0008, 0.0038), 'moderate_zap': (0.0007, 0.0023),
              'strong_inf': (0.055, 0.16), 'strong_zap': (0.055, 0.16)}
    for channel_name in CHANNELS:
        _, ax = plt.subplots(1, 1, figsize=(4, 3))
        semiaxis.W2_1_W2_2_plot(ax, channel_name, range=RANGES.get(channel_name))
        plt.savefig(config.PLOTS_PATH / ('W2_1_W2_2_' + channel_name + '.pdf'),
                    **config.SAVEFIG_KWARGS)


def plot_theta_i_distribution():
    RANGES = {'weak_inf': (-0.16, 1), 'weak_zap': (-0.9, -0.1),
              'moderate_inf': (0.65, 2.3), 'moderate_zap': (0.6, 1.8),
              'strong_inf': (3.1, 4.3), 'strong_zap': (3.1, 4.2)}
    for channel_name in CHANNELS:
        _, ax = plt.subplots(1, 1, figsize=(4, 3))
        semiaxis.theta_1_theta_2_plot(ax, channel_name, range=RANGES.get(channel_name))
        plt.savefig(config.PLOTS_PATH / ('theta_1_theta_2_' + channel_name + '.pdf'),
                    **config.SAVEFIG_KWARGS)


def main():
    ### 1. Beam centroid position
    print_beam_centroid_cumulants()
    plot_beam_centroids_distribution()

    ### 2. Beam-centroid position and beam shape
    print_x0_W2i_correlation()
    print_r0_W2r_correlation()
    plot_r0_W2r_correlation()

    ### 3. Correlation between the transmission efficiency and the beam deflection
    plot_r0_eta_correlation()

    ### 4. Length of semi-axes for the ellipse
    print_rotated_theta_i()
    plot_W2_i_distribution()
    plot_theta_i_distribution()

if __name__ == "__main__":
    main()
