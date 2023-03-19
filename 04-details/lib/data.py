from functools import lru_cache
import json

import numpy as np
import pandas as pd

import config


@lru_cache(maxsize=None)
def _get_data(channel_name):
    with open(config.DATA_PATH / channel_name / 'params.json', 'r') as f:
        channel = json.load(f)
    beam = pd.read_csv(config.DATA_PATH / channel_name / 'beam.csv')
    beam_params = pd.read_csv(config.RESULTS_PATH / channel_name / 'beam_params.csv')
    eta = pd.read_csv(config.DATA_PATH / channel_name / 'transmittance.csv')
    eta.columns = pd.to_numeric(eta.columns)
    tracked_eta = pd.read_csv(config.DATA_PATH / channel_name / 'tracked_transmittance.csv')
    tracked_eta = tracked_eta.drop(['mean_x', 'mean_y'], axis=1)
    tracked_eta.columns = pd.to_numeric(tracked_eta.columns)
    return {'channel': channel, 'beam': beam, 'beam_params': beam_params,
            'eta': eta, 'tracked_eta': tracked_eta}


def W_0(channel_name):
    return _get_data(channel_name)['channel']['source']['W0']


def x_0(channel_name):
    return _get_data(channel_name)['beam']['mean_x']


def bw2(channel_name):
    return _get_data(channel_name)['beam_params']['bw2'].values[0]


def lt2(channel_name):
    return _get_data(channel_name)['beam_params']['lt2'].values[0]


def r_0(channel_name):
    beam_data = _get_data(channel_name)['beam']
    return np.sqrt(beam_data['mean_x']**2 + beam_data['mean_y']**2)


def W2_r(channel_name):
    beam_data = _get_data(channel_name)['beam']
    r2_0_data = beam_data['mean_x']**2 + beam_data['mean_y']**2
    return 4 * (beam_data['mean_x2_r'] - r2_0_data)


@lru_cache(maxsize=1)
def W2_i(channel_name):
    beam_data = _get_data(channel_name)['beam']
    Sxx = 4 * (beam_data["mean_x2"] - beam_data["mean_x"]**2)
    Syy = 4 * (beam_data["mean_y2"] - beam_data["mean_y"]**2)
    Sxy = 4 * (beam_data["mean_xy"] - beam_data["mean_x"] * beam_data["mean_y"])
    trS = Sxx + Syy
    detS = Sxx * Syy - Sxy * Sxy
    W2_1 = (trS + np.sign(Sxy) * np.sqrt(trS**2 - 4 * detS)) / 2
    W2_2 = (trS - np.sign(Sxy) * np.sqrt(trS**2 - 4 * detS)) / 2
    return {'W2_1': W2_1, 'W2_2': W2_2}


@lru_cache(maxsize=1)
def theta_i(channel_name):
    W2_1 = W2_i(channel_name)['W2_1']
    W2_2 = W2_i(channel_name)['W2_2']
    W_0_value = W_0(channel_name)
    return {'theta_1': np.log(W2_1 / W_0_value**2),
            'theta_2': np.log(W2_2 / W_0_value**2)}


def eta(channel_name):
    return _get_data(channel_name)['eta']


def tracked_eta(channel_name):
    return _get_data(channel_name)['tracked_eta']
