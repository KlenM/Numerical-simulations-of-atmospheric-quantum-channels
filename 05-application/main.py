import dataclasses

import numpy as np
import pandas as pd
from lib.plot_params import (BeamWanderingPlotParams, BetaPlotParams,
                             BetaTotalProbabilityPlotParams,
                             EllipticalBeamPlotParams, LognormalPlotParams,
                             NumBetaTotalProbabilityPlotParams,
                             NumEllipticalBeamPlotParams, NumericalPlotParams,
                             NumTotalProbabilityPlotParams,
                             TotalProbabilityPlotParams)
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d

import config


def get_squeezing(mean_eta, squeeze_in: float):
    DX2_in = 10**(squeeze_in / 10)
    return 10 * np.log10(mean_eta * (DX2_in - 1) + 1)


def _plot_squeezing(ax, channel_name, aperture_radius, squeeze_in, eta_det, max_eta, models):
    channel_path = config.RESULTS_PATH / channel_name
    file_name = str(aperture_radius).replace('.', '_') + '.csv'
    thresholds = np.linspace(0, max_eta, 100)
    for model in models:
        model = dataclasses.asdict(model)
        df = pd.read_csv(channel_path / model['name'] / file_name)
        df['transmittance'] = df['transmittance'] * eta_det
        squeezing = []
        product = df['probability_density'] * df['transmittance']
        for t in thresholds:
            mapping = df['transmittance'] > t
            norm = df['probability_density'][mapping].sum()
            if norm:
                mean_eta = product[mapping].sum() / norm
                squeezing.append(get_squeezing(mean_eta, squeeze_in))
            else:
                squeezing.append(np.nan)
        squeezing = gaussian_filter1d(squeezing, 1.2)

        ax.plot(thresholds[:-1], squeezing[:-1], label=model['name'], c=model['color'],
                ls=model['linestyle'], zorder=model['zorder'])

        # Circle labels
        if model['label'] and model['label_pos']:
            color = model['color']
            # label_pos = model.get('label_pos', np.random.randint(0, len(eta_axis)))
            label_x = thresholds[model['label_pos']]
            label_y = squeezing[model['label_pos']]
            ax.scatter([label_x], [label_y], s=100,
                       marker="o", zorder=10, clip_on=False, linewidth=1.2,
                       edgecolor=color, facecolor="white")
            ax.text(label_x + model['label_dx'],
                    0.99 * label_y + model['label_dy'], model['label'],
                    zorder=20, color=color, ha="center", va="center",
                    size="x-small", clip_on=False, weight='bold',
                    fontfamily='sans-serif')

    ax.grid(which='major', color='#BBBBBB', linestyle='-')
    ax.invert_yaxis()
    ax.set_xlim(left=0)


def _plot_squeezing_by_aperture(ax, channel_name, squeeze_in, eta_det, thresholds):
    data_path = config.RESULTS_PATH / channel_name / 'numerical'
    beam_df = pd.read_csv(config.RESULTS_PATH / channel_name / 'beam_params.csv')
    lt2 = beam_df['lt2'][0]
    apertures = []
    for aperture_path in data_path.glob('*.csv'):
        apertures.append(float(aperture_path.name[:-4].replace('_', '.')))
    apertures.sort()
    normed_apertures = (apertures / np.sqrt(lt2)).tolist()

    squeezing = dict(zip(thresholds, [[] for _ in thresholds]))
    for aperture_radius in apertures:
        file_name = str(aperture_radius).replace('.', '_') + '.csv'
        df = pd.read_csv(data_path / file_name)
        product = df['probability_density'] * df['transmittance']
        for t in thresholds:
            mapping = df['transmittance'] > t
            norm = df['probability_density'][mapping].sum()
            if norm:
                mean_eta = product[mapping].sum() / norm
                squeezing[t].append(get_squeezing(eta_det * mean_eta, squeeze_in))
            else:
                squeezing[t].append(np.nan)
        # squeezing = gaussian_filter1d(squeezing, 1.2)

    for t in squeezing:
        ax.plot(normed_apertures, squeezing[t], c='k')
    ax.grid(which='major', color='#BBBBBB', linestyle='-')
    ax.invert_yaxis()
    ax.set_xlim(left=0)
    ax.set_ylabel('Squeezing (dB)')
    ax.set_xlabel("Normed aperture radius "
                  "$R_{{\\mathrm{{ap}}}} / W_{{\\mathrm{{LT}}}}$", labelpad=3)
    secax = ax.secondary_xaxis(
        1, functions=(lambda x: x * np.sqrt(lt2) * 100, lambda r: r)
    )
    secax.set_xlabel("Aperture radius $R_{{\\mathrm{{ap}}}}$ (cm)", labelpad=4)


def plot_squeezing(channel_name, squeeze_in, aperture_radius, max_eta, eta_det, models=None):
    models = models or [BeamWanderingPlotParams(), BetaPlotParams(), BetaTotalProbabilityPlotParams(),
        EllipticalBeamPlotParams(), LognormalPlotParams(), NumBetaTotalProbabilityPlotParams(),
        NumEllipticalBeamPlotParams(), NumericalPlotParams(), NumTotalProbabilityPlotParams(),
        TotalProbabilityPlotParams()]
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    _plot_squeezing(ax, channel_name, aperture_radius, squeeze_in, eta_det, max_eta, models)
    ax.set_ylabel('Squeezing (dB)')
    ax.set_xlabel(r'Postselection Threshold $\eta_\mathrm{min}$')
    plt.savefig(config.PLOTS_PATH / (f'squeezing_{channel_name}_{aperture_radius}.pdf'),
                **config.SAVEFIG_KWARGS)


def plot_squeezing_by_aperture(channel_name, squeeze_in, eta_det):
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    _plot_squeezing_by_aperture(ax, channel_name, squeeze_in, eta_det, thresholds=[0, 0.25, 0.5, 0.75])
    ax.annotate(
        r'$\eta_\mathrm{min} = 0$', (0.2, -0.2), xytext=(-50, 8), textcoords="offset points",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.3'},
    )
    ax.annotate(
        r'$\eta_\mathrm{min} = 0.25$', (0.3, -0.8), xytext=(-50, 8), textcoords="offset points",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.3'},
    )
    ax.annotate(
        r'$\eta_\mathrm{min} = 0.5$', (0.41, -1.4), xytext=(-50, 8), textcoords="offset points",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.3'},
    )
    ax.annotate(
        r'$\eta_\mathrm{min} = 0.75$', (0.58, -2), xytext=(-50, 8), textcoords="offset points",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.3'},
    )
    plt.savefig(config.PLOTS_PATH / (f'squeezing_by_aperture_{channel_name}.pdf'),
                **config.SAVEFIG_KWARGS)


if __name__ == "__main__":
    SQUEEZE_IN = -3
    LOSSES_PER_KM = 0.1
    OPRICAL_SYSTEM_LOSSES = 0.95
    CHANNEL_PARAMS = {
        'weak_inf': {'aperture_radius': 0.025, 'max_eta': 0.87, 'eta_det': 10**(-LOSSES_PER_KM * 1 / 10) * OPRICAL_SYSTEM_LOSSES},
        'weak_zap': {'aperture_radius': 0.012, 'max_eta': 0.87, 'eta_det': 10**(-LOSSES_PER_KM * 1 / 10) * OPRICAL_SYSTEM_LOSSES},
        'moderate_inf': {'aperture_radius': 0.019, 'max_eta': 0.87, 'eta_det': 10**(-LOSSES_PER_KM * 1.6 / 10) * OPRICAL_SYSTEM_LOSSES},
        'moderate_zap': {'aperture_radius': 0.019, 'max_eta': 0.65, 'eta_det': 10**(-LOSSES_PER_KM * 1.6 / 10) * OPRICAL_SYSTEM_LOSSES,
                         'models': [
                            EllipticalBeamPlotParams(label_pos=75), LognormalPlotParams(label_pos=35),
                            NumericalPlotParams(label_pos=20), BetaPlotParams(label_pos=87)]},
        'strong_inf': {'aperture_radius': 0.14, 'max_eta': 0.87, 'eta_det': 10**(-LOSSES_PER_KM * 10.2 / 10) * OPRICAL_SYSTEM_LOSSES},
        'strong_zap': {'aperture_radius': 0.14, 'max_eta': 0.87, 'eta_det': 10**(-LOSSES_PER_KM * 10.2 / 10) * OPRICAL_SYSTEM_LOSSES},
    }
    for channel_name, cp in CHANNEL_PARAMS.items():
        plot_squeezing(channel_name, SQUEEZE_IN, **cp)

    # by aperture
    plot_squeezing_by_aperture('moderate_zap', SQUEEZE_IN, 10**(-LOSSES_PER_KM * 1.6 / 10) * OPRICAL_SYSTEM_LOSSES)
