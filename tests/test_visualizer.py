import pytest
from SamanthaThesis.visualize import SurveyPlot
import pandas as pd


@pytest.fixture
def input_data_frame():
    mock_c = ['Entry Id', 'dimension', 'value']
    mock_r = [
        (1, 'D1', 2),
        (2, 'D1', 1),
        (3, 'D1', 2),
        (4, 'D1', 3),
        (5, 'D2', 1),
        (6, 'D2', 1),
        (7, 'D2', 2),
        (8, 'D2', 3),
    ]
    df = pd.DataFrame().from_records(
        mock_r, columns=mock_c).set_index('Entry Id')
    return df


@pytest.fixture
def input_data_frame_with_null():
    mock_c = ['Entry Id', 'dimension', 'value']
    mock_r = [
        (1, 'D1', 2),
        (2, 'D1', 1),
        (3, 'D1', 2),
        (4, 'D1', 3),
        (5, 'D2', 1),
        (6, 'D2', 1),
        (7, 'D2', 2),
        (8, 'D2', 3),
        (9, None, 3),
        (10, 'D2', None),
    ]
    df = pd.DataFrame().from_records(
        mock_r, columns=mock_c).set_index('Entry Id')
    return df


def test_data_for_visualizer(monkeypatch, input_data_frame):

    exp = {'title': 'QC2',
           'levels': ['3', '2', '1'],
           'overall_f': [.25, .375, 0.375],
           'overall_cum': [.25, .625, 1],
           'dimensions': [
               {'name': 'D1',
                'freq': [0.25, 0.5, 0.25],
                'overall_range_low': [0, 0.25, 1],
                'overall_range_high': [0.75, 1, 1],
                'cum': [0.25, 0.75, 1]},
               {'name': 'D2',
                'freq': [0.25, 0.25, 0.5],
                'overall_range_low': [0, 0.25, 1],
                'overall_range_high': [0.75, 1, 1],
                'cum': [0.25, 0.5, 1]}
           ]
           }

    sp = SurveyPlot(input_data_frame, title="QC2")
    res = sp.data_for_visualization()
    assert res == exp


def test_viz_data_with_null(monkeypatch, input_data_frame_with_null):

    exp = {'title': 'QC2',
           'levels': ['3.0', '2.0', '1.0'],
           'overall_f': [.25, .375, 0.375],
           'overall_cum': [.25, .625, 1],
           'dimensions': [
               {'name': 'D1',
                'freq': [0.25, 0.5, 0.25],
                'overall_range_low': [0, 0.25, 1],
                'overall_range_high': [0.75, 1, 1],
                'cum': [0.25, 0.75, 1]},
               {'name': 'D2',
                'freq': [0.25, 0.25, 0.5],
                'overall_range_low': [0, 0.25, 1],
                'overall_range_high': [0.75, 1, 1],
                'cum': [0.25, 0.5, 1]}
           ]
           }

    sp = SurveyPlot(input_data_frame_with_null, title="QC2")
    res = sp.data_for_visualization()
    assert res == exp
