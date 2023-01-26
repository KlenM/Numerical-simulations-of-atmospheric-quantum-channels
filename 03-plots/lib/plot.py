import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

import config
from lib.utils import get_available_models


def plot_pdt(ax, channel_name, aperture_radius, models):
    available_models = get_available_models(channel_name)
    channel_path = config.RESULTS_PATH / channel_name
    file_name = str(aperture_radius).replace('.', '_') + '.csv'
    for model in models:
        if model['name'] not in available_models:
            print("ERROR: '%s' model for the '%s' channel not found" %
                  (model['name'], channel_name))
            continue
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

        ax.plot(eta_axis, data, label=model['name'], c=model['color'],
                ls=model['linestyle'], zorder=model['zorder'])

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
    channel_path = config.RESULTS_PATH / channel_name
    ks_values_df = pd.read_csv(channel_path / 'ks_values.csv')
    beam_df = pd.read_csv(channel_path / 'beam_params.csv')
    lt2 = beam_df['lt2'][0]

    for model in models:
        model = model.asdict()
        if model['name'] not in available_models:
            print("ERROR: '%s' model for the '%s' channel not found" %
                  (model['name'], channel_name))
            continue

        _normed_x = (ks_values_df['aperture_radius'] / np.sqrt(lt2)).tolist()

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
        ax.plot(normed_x, data, label=model['name'], c=model['color'],
                ls=model['linestyle'], zorder=model['zorder'])

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
