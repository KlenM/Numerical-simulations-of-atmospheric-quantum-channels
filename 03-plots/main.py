from matplotlib import pyplot as plt

import config
from lib.plot import plot_ks_values, plot_pdt
from lib.plot_params import (BeamWanderingPlotParams, BetaPlotParams,
                             BetaTotalProbabilityPlotParams,
                             EllipticalBeamPlotParams, LognormalPlotParams,
                             NumBetaTotalProbabilityPlotParams, NumEllipticalBeamPlotParams,
                             NumericalPlotParams,
                             NumTotalProbabilityPlotParams,
                             TotalProbabilityPlotParams,
                             TrackedNumericalPlotParams)

RAP_SYM = "R_{{\\mathrm{{ap}}}}"


def pdt_weak_zap_channel():
    channel_name = 'weak_zap'
    aperture_radius = 0.012

    print(f"Plotting pdt of '{channel_name}' channel, a = {aperture_radius}.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_file_name = plot_pdt(
        ax, channel_name, aperture_radius,
        models=[
            NumericalPlotParams(smooth=1.2, label_pos=152, label_dy=0.02),
            LognormalPlotParams(ks_smooth=1, label_pos=125, label_dy=0.015),
            BetaPlotParams(ks_smooth=1, label_pos=122, label_dy=0.005),
            EllipticalBeamPlotParams(
                smooth=2.5, ks_smooth=4, label_pos=124, label_dy=0.025),
            # NumEllipticalBeamPlotParams(
            #     smooth=2.5, ks_smooth=4, label_pos=125, label_dy=0.025),
            # TotalProbabilityPlotParams(label_pos=150),
            BetaTotalProbabilityPlotParams(label_pos=151),
            # NumTotalProbabilityPlotParams(label_pos=150),
            NumBetaTotalProbabilityPlotParams(label_pos=145),
        ])
    ax.set_ylim(0, 6.2)
    ax.set_xlim(0.32, 1)
    ax.text(0.335, 2.1, f"${RAP_SYM} = {aperture_radius * 100:.2}$ cm")
    plt.savefig(config.PLOTS_PATH / plot_file_name, **config.SAVEFIG_KWARGS)


def pdt_weak_inf_channel():
    channel_name = 'weak_inf'
    aperture_radius = 0.025

    print(f"Plotting pdt of '{channel_name}' channel, a = {aperture_radius}.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_file_name = plot_pdt(
        ax, channel_name, aperture_radius=aperture_radius,
        models=[
            NumericalPlotParams(smooth=1.2, label_pos=153, label_dy=0.035),
            LognormalPlotParams(ks_smooth=1, label_pos=153, label_dy=0.015),
            BetaPlotParams(ks_smooth=1, label_pos=155, label_dy=0.005),
            BeamWanderingPlotParams(
                ks_smooth=4, label_pos=122, label_dy=-0.045),
            # EllipticalBeamPlotParams(
            #     smooth=2.5, ks_smooth=4, label_pos=124, label_dy=0.025),
            # NumEllipticalBeamPlotParams(
            #     smooth=2.5, ks_smooth=4, label_pos=124, label_dy=0.025),
            # TotalProbabilityPlotParams(label_pos=50),
            # BetaTotalProbabilityPlotParams(label_pos=50),
            NumTotalProbabilityPlotParams(label_pos=140),
            # NumBetaTotalProbabilityPlotParams(label_pos=50),
        ])
    ax.set_ylim(0, 10.8)
    ax.set_xlim(0.52, 1)
    ax.text(0.54, 1.1, f"${RAP_SYM} = {aperture_radius * 100:.2}$ cm")
    plt.savefig(config.PLOTS_PATH / plot_file_name, **config.SAVEFIG_KWARGS)


def pdt_moderate_channels():
    aperture_radius = 0.019

    print(f"Plotting pdt of 'modeate' channels, a = {aperture_radius}.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    _ = plot_pdt(
        ax, 'moderate_zap', aperture_radius=aperture_radius,
        models=[
            NumericalPlotParams(smooth=2.2, label=None, linestyle='-.'),
            TrackedNumericalPlotParams(smooth=1.2, label=None, linestyle='-.'),
            ])
    plot_file_name = plot_pdt(
        ax, 'moderate_inf', aperture_radius=aperture_radius,
        models=[
            NumericalPlotParams(smooth=2.2, label=None),
            TrackedNumericalPlotParams(smooth=1.2, label=None),
                 ])
    ax.annotate(
        "$F_0 = +\\infty$", (0.29, 2.42),
        xytext=(0.26, 2.8), textcoords="data",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=-0.2'},
    )
    ax.annotate(
        "$F_0 = +\\infty$", (0.43, 2.42),
        xytext=(0.26, 2.8), textcoords="data", alpha=0,
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.2'},
    )
    ax.annotate(
        "$F_0 = z_\\mathrm{ap}$", (0.46, 1.87),
        xytext=(0.41, 3.25), textcoords="data",
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=-0.15'},
    )
    ax.annotate(
        "$F_0 = z_\\mathrm{ap}$", (0.585, 2.75),
        xytext=(0.41, 3.25), textcoords="data", alpha=0,
        arrowprops={'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0.2'},
    )
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, 1)
    ax.text(0.03, 3.6, f"${RAP_SYM} = {aperture_radius * 100:.2}$ cm")
    plot_file_name = plot_file_name.replace('_inf', '')
    plt.savefig(config.PLOTS_PATH / plot_file_name, **config.SAVEFIG_KWARGS)


def pdt_strong_zap_channel():
    channel_name = 'strong_zap'
    aperture_radiuses = [0.06, 0.1, 0.14, 0.32]

    print(f"Plotting pdt of '{channel_name}' channel, a: {aperture_radiuses}.")
    _, axs = plt.subplots(1, 4, figsize=(10, 2.2))
    _ = plot_pdt(axs[0], channel_name, aperture_radius=aperture_radiuses[0],
        models=[
            NumericalPlotParams(smooth=2.2, label_pos=72, label_dy=-0.05),
            LognormalPlotParams(ks_smooth=1, label_pos=22),
        ])
    _ = plot_pdt(axs[1], channel_name, aperture_radius=aperture_radiuses[1],
        models=[
            NumericalPlotParams(smooth=2.2, label_pos=107, label_dy=0.005),
            BetaPlotParams(ks_smooth=1, label_pos=48),
        ])
    _ = plot_pdt(axs[2], channel_name, aperture_radius=aperture_radiuses[2],
        models=[
            NumericalPlotParams(smooth=2.2, label_pos=134, label_dy=-0.02),
            BetaPlotParams(ks_smooth=1, label_pos=42),
        ])
    _ = plot_pdt(axs[3], channel_name, aperture_radius=aperture_radiuses[3],
        models=[
            NumericalPlotParams(smooth=2.2, label_pos=151, label_dy=-0.04),
            BeamWanderingPlotParams(ks_smooth=4, label_pos=78, label_dy=-0.08),
        ])

    for i, ax in enumerate(axs):
        if i != 0:
            axs[i].set_ylabel(None)  # type: ignore
        if i in [1, 2]:
            ax.set_ylim(0, 5)
        else:
            ax.set_ylim(0, 14)
            ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14])
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(['0.0', 0.25, 0.5, 0.75, '1.0'])
        ax.text(
            0.105,  0.89,
            f"${RAP_SYM} = {aperture_radiuses[i] * 100:.0f}$ cm",
            transform=ax.transAxes
        )
    plt.savefig(config.PLOTS_PATH / 'strong_zap_pdt.pdf',
                **config.SAVEFIG_KWARGS)


def ks_weak_zap_channel():
    channel_name = 'weak_zap'

    print(f"Plotting ks_values of '{channel_name}' channel.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(ax, channel_name,
        models=[
            LognormalPlotParams(ks_smooth=1, label_pos=14),
            BeamWanderingPlotParams(
                ks_smooth=4, label_pos=17, label_dy=-0.007),
            EllipticalBeamPlotParams(ks_smooth=4, label_pos=14),
            BetaPlotParams(ks_smooth=1, label_pos=15),
            TotalProbabilityPlotParams(
                ks_smooth=1, label_pos=11, label_dy=-0.0005),
            BetaTotalProbabilityPlotParams(label_pos=17),
            NumTotalProbabilityPlotParams(label_pos=17),
            NumBetaTotalProbabilityPlotParams(label_pos=17),
            ])
    ax.set_ylim(0.008, 1)
    plt.savefig(config.PLOTS_PATH / 'weak_zap_ks_values.pdf',
                **config.SAVEFIG_KWARGS)


def ks_weak_inf_channel():
    channel_name = 'weak_inf'

    print(f"Plotting ks_values of '{channel_name}' channel.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, channel_name,
        models=[
            LognormalPlotParams(
                ks_smooth=1, label_pos=19, label_dy=-0.0002),
            BeamWanderingPlotParams(
                ks_smooth=4, label_pos=25, label_dy=-0.007),
            EllipticalBeamPlotParams(
                ks_smooth=4, label_pos=23, label_dy=-0.002),
            BetaPlotParams(
                ks_smooth=1, label_pos=10, label_dy=-0.00004),
            TotalProbabilityPlotParams(
                ks_smooth=1, label_pos=16, label_dy=-0.0005),
            BetaTotalProbabilityPlotParams(label_pos=17),
            NumTotalProbabilityPlotParams(label_pos=17),
            NumBetaTotalProbabilityPlotParams(label_pos=17),
            ])
    ax.set_ylim(0.001, 1)
    plt.savefig(config.PLOTS_PATH / 'weak_inf_ks_values.pdf',
                **config.SAVEFIG_KWARGS)


def ks_moderate_zap_channel():
    channel_name = 'moderate_zap'

    print(f"Plotting ks_values of '{channel_name}' channel.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, channel_name,
        models=[
            LognormalPlotParams(ks_smooth=1, label_pos=23),
            BeamWanderingPlotParams(
                ks_smooth=4, label_pos=24, label_dy=-0.003),
            EllipticalBeamPlotParams(ks_smooth=4, label_pos=18),
            BetaPlotParams(ks_smooth=1, label_pos=20),
            TotalProbabilityPlotParams(
                ks_smooth=1, label_pos=18, label_dy=-0.0005),
            BetaTotalProbabilityPlotParams(label_pos=17),
            NumTotalProbabilityPlotParams(label_pos=17),
            NumBetaTotalProbabilityPlotParams(label_pos=17),
            ])
    ax.set_ylim(0.02, 1)
    plt.savefig(config.PLOTS_PATH / 'moderate_zap_ks_values.pdf',
                **config.SAVEFIG_KWARGS)


def ks_strong_zap_channel():
    channel_name = 'strong_zap'

    print(f"Plotting ks_values of '{channel_name}' channel.")
    _, ax = plt.subplots(1, 1, figsize=(4, 3))
    plot_ks_values(
        ax, channel_name,
        models=[
            LognormalPlotParams(ks_smooth=1, label_pos=22),
            BeamWanderingPlotParams(
                ks_smooth=4, label_pos=24, label_dy=-0.003),
            EllipticalBeamPlotParams(ks_smooth=4, label_pos=18),
            BetaPlotParams(ks_smooth=1, label_pos=12),
            TotalProbabilityPlotParams(ks_smooth=1, label_pos=18),
            BetaTotalProbabilityPlotParams(label_pos=14),
            NumTotalProbabilityPlotParams(label_pos=17),
            NumBetaTotalProbabilityPlotParams(label_pos=21),
            ])
    ax.set_ylim(0.02, 1)
    plt.savefig(config.PLOTS_PATH / 'strong_zap_ks_values.pdf',
                **config.SAVEFIG_KWARGS)


def run():
    config.PLOTS_PATH.mkdir(exist_ok=True)
    # pdt_weak_zap_channel()
    pdt_weak_inf_channel()
    # pdt_moderate_channels()
    # pdt_strong_zap_channel()
    # ks_weak_zap_channel()
    # ks_weak_inf_channel()
    # ks_moderate_zap_channel()
    # ks_strong_zap_channel()


if __name__ == "__main__":
    run()


# models = {
#     'numerical': {
#         'name': 'numerical', 'label': 'N', 'smooth': 1.2,
#         'plot_kwargs': {'color': '#000000', 'ls': '-', 'zorder': 8},
#     },
#     'tracked_numerical': {
#         'name': 'tracked_numerical', 'label': 'R', 'smooth': 1.2,
#         'plot_kwargs': {'color': '#555555', 'ls': '--', 'zorder': 7},
#     },
#     'lognormal': {
#         'name': 'lognormal', 'label': 'L', 'ks_smooth': 1,
#         'plot_kwargs': {'color': '#e53935', 'linestyle': '-', 'zorder': 4},
#     },
#     'beam_wandering': {
#         'name': 'beam_wandering', 'label': 'W', 'ks_smooth': 4,
#         'plot_kwargs': {'color': '#fb8c00', 'linestyle': '-', 'zorder': 1},
#     },
#     'elliptical_beam': {
#         'name': 'elliptical_beam', 'label': 'E',
#         'smooth': 2.5, 'ks_smooth': 4,
#         'plot_kwargs': {'color': '#d81b60', 'linestyle': '-', 'zorder': 2},
#     },
#     'total_probability': {
#         'name': 'total_probability', 'label': 'T', 'ks_smooth': 1,
#         'plot_kwargs': {'color': '#00897b', 'linestyle': '-', 'zorder': 3},
#     },
#     'beta': {
#         'name': 'beta', 'label': 'B', 'ks_smooth': 1,
#         'plot_kwargs': {'color': '#3949ab', 'linestyle': '-', 'zorder': 6},
#     },
#     'beta_total_probability': {
#         'name': 'beta_total_probability', 'label': 'P', 'ks_smooth': 1,
#         'plot_kwargs': {'color': '#e28544', 'linestyle': '-', 'zorder': 5},
#     },
# }
