from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d


# matplotlib.use('Qt5Agg')
plt.rcParams['axes.axisbelow'] = True
plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams["font.serif"] = "STIX"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

RESULTS_PATH = Path('../results')
T_RESULTS_PATH = Path('../analyse/results')
PLOTS_PATH = Path('../analyse/plots')

models = {
    'numerical': {
        'name': 'numerical', 'label': 'N', 'smooth': 1.2,
        'plot_kwargs': {'color': '#000000', 'ls': '-', 'zorder': 8},
    },
    'tracked_numerical': {
        'name': 'tracked_numerical', 'label': 'R', 'smooth': 1.2,
        'plot_kwargs': {'color': '#555555', 'ls': '--', 'zorder': 7},
    },
    'lognormal': {
        'name': 'lognormal', 'label': 'L', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#e53935', 'linestyle': '-', 'zorder': 4},
    },
    'beam_wandering': {
        'name': 'beam_wandering', 'label': 'W', 'ks_smooth': 4,
        'plot_kwargs': {'color': '#fb8c00', 'linestyle': '-', 'zorder': 1},
    },
    'elliptical_beam': {
        'name': 'elliptical_beam', 'label': 'E',
        'smooth': 2.5, 'ks_smooth': 4,
        'plot_kwargs': {'color': '#d81b60', 'linestyle': '-', 'zorder': 2},
    },
    'total_probability': {
        'name': 'total_probability', 'label': 'T', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#00897b', 'linestyle': '-', 'zorder': 3},
    },
    'beta': {
        'name': 'beta', 'label': 'B', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#3949ab', 'linestyle': '-', 'zorder': 6},
    },
    'beta_total_probability': {
        'name': 'beta_total_probability', 'label': 'P', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#e28544', 'linestyle': '-', 'zorder': 5},
    },
    'num_total_probability': {
        'name': 'num_total_probability', 'label': '$\overline{T}$', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#e28544', 'linestyle': '-', 'zorder': 5},
    },
    'num_beta_total_probability': {
        'name': 'num_beta_total_probability', 'label': '$\overline{B}$', 'ks_smooth': 1,
        'plot_kwargs': {'color': '#e28544', 'linestyle': '-', 'zorder': 5},
    },
}


def get_available_channels():
    return [loc.name for loc in RESULTS_PATH.iterdir() if loc.is_dir()]


def get_available_models(channel_name):
    channel_path = RESULTS_PATH / channel_name
    main = [loc.name for loc in channel_path.iterdir() if loc.is_dir()]
    t_channel_path = T_RESULTS_PATH / channel_name
    total_prob = [loc.name for loc in t_channel_path.iterdir() if loc.is_dir()]
    return main + total_prob


def get_aperture_radiuses(channel_name):
    channel_path = RESULTS_PATH / channel_name
    return list(pd.read_csv(channel_path / 'ks_values.csv', index_col=0).index)


def plot_pdt(ax, channel_name, aperture_radius, models):
    available_models = get_available_models(channel_name)
    channel_path = RESULTS_PATH / channel_name
    t_channel_path = T_RESULTS_PATH / channel_name
    file_name = str(aperture_radius).replace('.', '_') + '.csv'
    for model in models:
        if model['name'] not in available_models:
            print("ERROR: '%s' model for the '%s' channel not found" %
                  (model['name'], channel_name))
            continue
        if model['name'] in ['num_total_probability', 'num_beta_total_probability']:
            df = pd.read_csv(t_channel_path / model['name'] / file_name)
        else:
            df = pd.read_csv(channel_path / model['name'] / file_name)

        # Smooth data
        if 'smooth' in model:
            df['probability_density'] = gaussian_filter1d(
                df['probability_density'], model['smooth'])

        # Clip tails
        tails_mask = df['probability_density'] > model.get('clip_tails', 0.01)
        eta_axis = df['transmittance'][tails_mask].tolist()
        data = df['probability_density'][tails_mask].tolist()
        if model['name'] == 'beam_wandering':
            eta_axis = list(eta_axis) + [eta_axis[-1]]
            data = list(data) + [0]

        ax.plot(eta_axis, data, label=model['name'], **model['plot_kwargs'])

        # Circle labels
        label = model.get('label')
        if label:
            color = model['plot_kwargs'].get('color', 'black')
            label_pos = model.get('label_pos',
                                  np.random.randint(0, len(eta_axis)))
            label_dx = model.get('label_dx', 0)
            label_dy = model.get('label_dy', 0)
            ax.scatter([eta_axis[label_pos]], [data[label_pos]], s=100,
                       marker="o", zorder=10, clip_on=False, linewidth=1.2,
                       edgecolor=color, facecolor="white")
            ax.text(eta_axis[label_pos] + label_dx,
                    0.99 * data[label_pos] + label_dy, label, zorder=20,
                    color=color, ha="center", va="center", size="x-small",
                    clip_on=False, weight='bold', fontfamily='sans-serif')

    ax.grid(which='major', color='#BBBBBB', linestyle='-')
    ax.set_ylabel("Probability distribution")
    ax.set_xlabel("Transmittance $\\eta$")
    plot_file_name = (channel_name + '_pdt_' +
                      str(aperture_radius).replace('.', '_') + '.pdf')
    return plot_file_name


def plot_ks_values(ax, channel_name, models):
    available_models = get_available_models(channel_name)
    channel_path = RESULTS_PATH / channel_name
    ks_values_df = pd.read_csv(channel_path / 'ks_values.csv', index_col=0)
    beam_df = pd.read_csv(channel_path / 'beam_params.csv')
    lt2 = beam_df['lt2'][0]
    
    t_channel_path = T_RESULTS_PATH / channel_name
    ks_values_df = pd.concat([ks_values_df, pd.read_csv(t_channel_path / 'ks_values.csv', index_col=0)], axis=1)
    
    for model in models:
        if model['name'] not in available_models:
            print("ERROR: '%s' model for the '%s' channel not found" %
                  (model['name'], channel_name))
            continue

        _normed_x = (ks_values_df.index / np.sqrt(lt2)).tolist()

        # Smooth data
        if 'ks_smooth' in model:
            normed_x = np.linspace(min(_normed_x), max(_normed_x), 200)
            f = interp1d(_normed_x, ks_values_df[model['name']])
            data = gaussian_filter1d(f(normed_x),
                                     model['ks_smooth'])
        else:
            data = ks_values_df[model['name']]
            normed_x = _normed_x

        data[data > 1] = 1
        data = data.tolist()
        ax.plot(normed_x, data, label=model['name'], **model['plot_kwargs'])

        # Circle labels
        label = model.get('label')
        if 'label' in model:
            color = model['plot_kwargs'].get('color', 'black')
            label_pos = model.get('label_pos',
                                  np.random.randint(0, len(normed_x)))
            label_dx = model.get('label_dx', 0)
            label_dy = model.get('label_dy', 0)
            ax.scatter([normed_x[label_pos]], [data[label_pos]], s=100,
                       marker="o", zorder=10, clip_on=False, linewidth=1.2,
                       edgecolor=color, facecolor="white")
            ax.text(normed_x[label_pos] + label_dx,
                    0.985 * data[label_pos] + label_dy, label, zorder=20,
                    color=color, ha="center", va="center", size="x-small",
                    clip_on=False, weight='bold', fontfamily='sans-serif')

    secax = ax.secondary_xaxis(
        1, functions=(lambda x: x * np.sqrt(lt2) * 100, lambda r: r)
    )
    secax.set_xlabel("Aperture radius $R_{{\\mathrm{{ap}}}}$ (cm)", labelpad=4)
    ax.grid(which='major', color='#BBBBBB', linestyle='-')
    ax.set_yscale('log')
    ax.set_ylabel("Kolmogorov-Smirnov statistic $D_M$")
    ax.set_xlabel("Normed aperture radius "
                  "$R_{{\\mathrm{{ap}}}} / W_{{\\mathrm{{LT}}}}$", labelpad=3)
    ax.set_xlim(left=0, right=ax.get_xlim()[1] * 0.98)
    ax.set_xticks(np.arange(0, ax.get_xlim()[1], 0.25))


def run():
    PLOTS_PATH.mkdir(exist_ok=True)

    # Weak zap channel
#     print("Plotting 'weak_zap' channel...")
#     aperture_radius = 0.012
#     _, ax = plt.subplots(1, 1, figsize=(4, 3))
#     plot_file_name = plot_pdt(
#         ax, 'weak_zap', aperture_radius=aperture_radius,
#         models=[
#             {**models['numerical'], 'label_pos': 110, 'label_dy': 0.02},
#             {**models['lognormal'], 'label_pos': 43, 'label_dy': 0.015},
#             {**models['beta'], 'label_pos': 55, 'label_dy': 0.005},
#             {**models['elliptical_beam'], 'label_pos': 79, 'label_dy': 0.025},
#         ])
#     ax.text(0.335, 2.1,
#             f"$R_{{\\mathrm{{ap}}}} = {aperture_radius * 100:.2}$ cm")
#     ax.set_ylim(0, 6.2)
#     ax.set_xlim(0.32, 1)
#     plt.savefig(PLOTS_PATH / plot_file_name, format="pdf", dpi=300,
#                 bbox_inches="tight", pad_inches=0.005)

#     # Weak inf channel
#     print("Plotting 'weak_inf' channel...")
#     aperture_radius = 0.025
#     _, ax = plt.subplots(1, 1, figsize=(4, 3))
#     plot_file_name = plot_pdt(
#         ax, 'weak_inf', aperture_radius=aperture_radius,
#         models=[
#             {**models['numerical'], 'label_pos': 93, 'label_dy': 0.035},
#             {**models['lognormal'], 'label_pos': 43, 'label_dy': 0.015},
#             {**models['beta'], 'label_pos': 60, 'label_dy': 0.005},
#             {**models['beam_wandering'], 'label_pos': 44, 'label_dy': -0.045},
#             ])
#     ax.text(0.54, 1.1,
#             f"$R_{{\\mathrm{{ap}}}} = {aperture_radius * 100:.2}$ cm")
#     ax.set_ylim(0, 10.8)
#     ax.set_xlim(0.52, 1)
#     plt.savefig(PLOTS_PATH / plot_file_name, format="pdf", dpi=300,
#                 bbox_inches="tight", pad_inches=0.005)

#     # Moderate channels
#     print("Plotting 'moderate' channel...")
#     aperture_radius = 0.019
#     _, ax = plt.subplots(1, 1, figsize=(4, 3))
#     _ = plot_pdt(
#         ax, 'moderate_zap', aperture_radius=aperture_radius,
#         models=[
#             {**models['numerical'], 'label': None, 'smooth': 2.2},
#             {**models['tracked_numerical'], 'label': None},
#             ])
#     plot_file_name = plot_pdt(
#         ax, 'moderate_inf', aperture_radius=aperture_radius,
#         models=[
#             {**models['numerical'], 'label': None, 'smooth': 2.2},
#             {**models['tracked_numerical'], 'label': None},
#                  ])
#     ax.annotate(
#         "$F_0 = +\\infty$", (0.29, 2.42),
#         xytext=(0.26, 2.8), textcoords="data",
#         arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=-0.2'},
#     )
#     ax.annotate(
#         "$F_0 = +\\infty$", (0.43, 2.42),
#         xytext=(0.26, 2.8), textcoords="data", alpha=0,
#         arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.2'},
#     )
#     ax.annotate(
#         "$F_0 = z_\\mathrm{ap}$", (0.46, 1.87),
#         xytext=(0.41, 3.25), textcoords="data",
#         arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=-0.15'},
#     )
#     ax.annotate(
#         "$F_0 = z_\\mathrm{ap}$", (0.585, 2.75),
#         xytext=(0.41, 3.25), textcoords="data", alpha=0,
#         arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.2'},
#     )
#     ax.text(0.03, 3.6,
#             f"$R_{{\\mathrm{{ap}}}} = {aperture_radius * 100:.2}$ cm")
#     ax.set_ylim(bottom=0)
#     ax.set_xlim(0, 1)
#     plot_file_name = plot_file_name.replace('_inf', '')
#     plt.savefig(PLOTS_PATH / plot_file_name, format="pdf", dpi=300,
#                 bbox_inches="tight", pad_inches=0.005)

#     print("Plotting 'strong' channel...")
#     aperture_radiuses = [0.06, 0.1, 0.14, 0.32]

#     _, axs = plt.subplots(1, 4, figsize=(10, 2.2))
#     _ = plot_pdt(axs[0], 'strong_zap', aperture_radius=aperture_radiuses[0],
#                  models=[
#                      {**models['numerical'], 'label_pos': 72, 'smooth': 2.2,
#                       'label_dy': -0.05},
#                      {**models['lognormal'], 'label_pos': 22}
#                  ])
#     _ = plot_pdt(axs[1], 'strong_zap', aperture_radius=aperture_radiuses[1],
#                  models=[
#                      {**models['numerical'], 'label_pos': 107, 'smooth': 2.2,
#                       'label_dy': -0.02},
#                      {**models['beta'], 'label_pos': 48}
#                  ])
#     _ = plot_pdt(axs[2], 'strong_zap', aperture_radius=aperture_radiuses[2],
#                  models=[
#                      {**models['numerical'], 'label_pos': 134, 'smooth': 2.2,
#                       'label_dy': -0.02},
#                      {**models['beta'], 'label_pos': 42}
#                  ])
#     _ = plot_pdt(axs[3], 'strong_zap', aperture_radius=aperture_radiuses[3],
#                  models=[
#                      {**models['numerical'], 'label_pos': 151, 'smooth': 2.2,
#                       'label_dy': -0.04},
#                      {**models['beam_wandering'], 'label_pos': 78,
#                       'label_dy': -0.08}
#                  ])

#     for i, ax in enumerate(axs):
#         if i != 0:
#             axs[i].set_ylabel(None)
#         if i in [1, 2]:
#             ax.set_ylim(0, 5)
#         else:
#             ax.set_ylim(0, 14)
#             ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14])
#         ax.set_xlim(0, 1)
#         ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
#         ax.set_xticklabels(['0.0', 0.25, 0.5, 0.75, '1.0'])
#         ax.text(
#             0.105,  0.89,
#             f"$R_{{\\mathrm{{ap}}}} = {aperture_radiuses[i] * 100:.0f}$ cm",
#             transform=ax.transAxes
#         )

#     plt.savefig(PLOTS_PATH / 'strong_zap_pdt.pdf', format="pdf", dpi=300,
#                 bbox_inches="tight", pad_inches=0.005)

    # Plot ks_values
    print("Plotting ks_values for 'weak_zap' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'weak_zap',
        models=[
            {**models['lognormal'], 'label_pos': 14*5},
            {**models['beta'], 'label_pos': 15*5},
            {**models['elliptical_beam'], 'label_pos': 14*5},
            {**models['total_probability'], 'label_pos': 11*5,
             'label_dy': -0.0005},
            {**models['beam_wandering'], 'label_pos': 17*5,
             'label_dy': -0.007},
            {**models['num_total_probability'], 'label_pos': 17*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 17*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.008, 1)
    plt.savefig(PLOTS_PATH / 'weak_zap_ks_values.pdf', format="pdf", dpi=300,
                bbox_inches="tight", pad_inches=0.005)

    print("Plotting ks_values for 'weak_inf' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'weak_inf',
        models=[
            {**models['lognormal'], 'label_pos': 19*5,
             'label_dy': -0.0002},
            {**models['beta'], 'label_pos': 10*5,
             'label_dy': -0.00004},
            {**models['elliptical_beam'], 'label_pos': 23*5,
             'label_dy': -0.002},
            {**models['total_probability'], 'label_pos': 16*5,
             'label_dy': -0.0005},
            {**models['beam_wandering'], 'label_pos': 25*5,
             'label_dy': -0.007},
            {**models['num_total_probability'], 'label_pos': 25*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 22*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.001, 1)
    plt.savefig(PLOTS_PATH / 'weak_inf_ks_values.pdf', format="pdf", dpi=300,
                bbox_inches="tight", pad_inches=0.005)

    print("Plotting ks_values for 'moderate_zap' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'moderate_zap',
        models=[
            {**models['lognormal'], 'label_pos': 23*4},
            {**models['beta'], 'label_pos': 20*4},
            {**models['elliptical_beam'], 'label_pos': 18*4},
            {**models['total_probability'], 'label_pos': 18*4,
             'label_dx': -0.0005},
            {**models['beam_wandering'], 'label_pos': 24*4,
             'label_dy': -0.003},
            {**models['num_total_probability'], 'label_pos': 24*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 21*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.003, 1)
    plt.savefig(PLOTS_PATH / 'moderate_zap_ks_values.pdf', format="pdf",
                dpi=300, bbox_inches="tight", pad_inches=0.005)

    print("Plotting ks_values for 'moderate_inf' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'moderate_inf',
        models=[
            {**models['lognormal'], 'label_pos': 23*4},
            {**models['beta'], 'label_pos': 20*4},
            {**models['elliptical_beam'], 'label_pos': 18*4},
            {**models['total_probability'], 'label_pos': 18*4,
             'label_dx': -0.0005},
            {**models['beam_wandering'], 'label_pos': 24*4,
             'label_dy': -0.003},
            {**models['num_total_probability'], 'label_pos': 24*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 21*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.003, 1)
    plt.savefig(PLOTS_PATH / 'moderate_inf_ks_values.pdf', format="pdf",
                dpi=300, bbox_inches="tight", pad_inches=0.005)

    print("Plotting ks_values for 'strong_zap' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'strong_zap',
        models=[
            {**models['lognormal'], 'label_pos': 22*4},
            {**models['beta'], 'label_pos': 12*4},
            {**models['elliptical_beam'], 'label_pos': 18*4},
            {**models['total_probability'], 'label_pos': 18*4},
            {**models['beam_wandering'], 'label_pos': 24*4,
             'label_dy': -0.003},
            {**models['num_total_probability'], 'label_pos': 26*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 22*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.02, 1)
    plt.savefig(PLOTS_PATH / 'strong_zap_ks_values.pdf', format="pdf", dpi=300,
                bbox_inches="tight", pad_inches=0.005)

    print("Plotting ks_values for 'strong_inf' channel...")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, 'strong_inf',
        models=[
            {**models['lognormal'], 'label_pos': 22*4},
            {**models['beta'], 'label_pos': 12*4},
            {**models['elliptical_beam'], 'label_pos': 18*4},
            {**models['total_probability'], 'label_pos': 18*4},
            {**models['beam_wandering'], 'label_pos': 24*4,
             'label_dy': -0.003},
            {**models['num_total_probability'], 'label_pos': 26*5,
             'label_dy': 0},
            {**models['num_beta_total_probability'], 'label_pos': 22*5,
             'label_dy': 0},
            ])
    ax.set_ylim(0.02, 1)
    plt.savefig(PLOTS_PATH / 'strong_inf_ks_values.pdf', format="pdf", dpi=300,
                bbox_inches="tight", pad_inches=0.005)


if __name__ == "__main__":
    run()
