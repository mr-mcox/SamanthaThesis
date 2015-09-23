from SamanthaThesis.process import Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal
import pytest
import numpy as np


def assert_frame_subset(actual, expected):
    assert_frame_equal(actual.loc[:, expected.columns], expected)


@pytest.fixture
def mock_question_key():
    question_r = [
        ("Q1", "QC1", "G1", "dimension"),
        ("Q2", "QC2", "G2", "question"),
        ("Q3", "QC3", "G3", "dimension"),
        ("Q4", "QC4", "G3", "dimension"),
    ]
    question_c = ['variable',
                  'analysis_code',
                  'question_theme',
                  'dimension_or_question']

    return pd.DataFrame.from_records(question_r, columns=question_c)


@pytest.fixture
def mock_resp():
    resp_c = ['Entry Id', 'Q1', 'Q2']
    resp_r = [
        (1, 1, 2),
        (2, 2, 3),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture
def mock_complex_dim_question_key():
    question_r = [
        ("Q1", "QC1", "G1", "dimension"),
        ("Q2", "QC2", "G2", "dimension"),
    ]
    question_c = ['variable',
                  'analysis_code',
                  'question_theme',
                  'dimension_or_question']

    return pd.DataFrame.from_records(question_r, columns=question_c)


@pytest.fixture
def mock_complex_dim_resp():
    resp_c = ['Entry Id', 'Q1', 'Q2']
    resp_r = [
        (1, 1, 10),
        (2, 2, 20),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


def test_regular_dimension(mock_question_key, mock_resp):

    exp_r = [(1, 'QC1', 1), (2, 'QC1', 2)]
    exp_c = ['Entry Id', 'dimension_code', 'value']
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    p = Processor(question_key=mock_question_key, survey_results=mock_resp)

    assert_frame_subset(p.dimension_values, exp_df)


def test_dimension_key(mock_question_key):
    exp_c = ['dimension_code', 'text', 'group', 'type']
    exp_r = [
        ('QC1', 'Q1', 'G1', 'complete'),
        ('QC3', 'Q3', 'G3', 'overlapping'),
        ('QC4', 'Q4', 'G3', 'overlapping'),
    ]
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('dimension_code')

    proc = Processor(question_key=mock_question_key)

    assert_frame_subset(proc.dimension_key, exp_df)


def test_single_dimension_bins(mock_question_key, mock_resp, monkeypatch):
    exp_c = ['Entry Id', 'dimension_code', 'bin']
    exp_r = [(1, 'QC1', "1-2"), (2, 'QC1', "2-3")]
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    def mock_percentile(a, q):
        return np.array([1, 2, 3, 4, 5])

    monkeypatch.setattr(np, 'percentile', mock_percentile)
    p = Processor(question_key=mock_question_key, survey_results=mock_resp)

    assert_frame_subset(p.dimension_values, exp_df)


def test_multiple_dimension_bins(mock_complex_dim_question_key,
                                 mock_complex_dim_resp,
                                 monkeypatch):
    exp_c = ['Entry Id', 'dimension_code', 'bin']
    exp_r = [(1, 'QC1', "1-2"),
             (2, 'QC1', "2-3"),
             (1, 'QC2', "10-20"),
             (2, 'QC2', "20-30")]
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    def mock_percentile(arr, q):
        if(arr.iloc[0] < 10):
            print("Returned small array")
            return np.array([1, 2, 3, 4, 5])
        else:
            print("Returned large array")
            return np.array([10, 20, 30, 40, 50])

    monkeypatch.setattr(np, 'percentile', mock_percentile)
    proc = Processor(question_key=mock_complex_dim_question_key,
                     survey_results=mock_complex_dim_resp)

    assert_frame_subset(proc.dimension_values, exp_df)


@pytest.fixture
def resp_for_overlap_dim():
    resp_c = ['Entry Id', 'Q1', 'Q2', 'Q3']
    resp_r = [
        (1, 1, 2, 1),
        (2, 2, 3, 0),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


def test_overlapping_dim_indicator_variable(mock_question_key,
                                            resp_for_overlap_dim,
                                            monkeypatch):

    res = Processor(question_key=mock_question_key,
                    survey_results=resp_for_overlap_dim).dimension_values

    res = res.reset_index().set_index(
        ['Entry Id', 'dimension_code'])

    assert res.loc[(1, 'QC3'), 'bin'] == 'QC3'
    assert np.isnan(res.loc[(2, 'QC3'), 'bin'])


def test_regular_response(mock_question_key, mock_resp):

    exp_r = [(1, 'QC2', 2), (2, 'QC2', 3)]
    exp_c = ['Entry Id', 'question_code', 'value']
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    p = Processor(question_key=mock_question_key, survey_results=mock_resp)

    assert_frame_subset(p.response_values, exp_df)


def test_dimensions_in_group(mock_question_key):
    exp = ['QC3', 'QC4']

    p = Processor(question_key=mock_question_key)
    assert p.dimensions_in_group('G3') == exp


def test_questions_in_group(mock_question_key):
    exp = ['QC2']

    p = Processor(question_key=mock_question_key)
    assert p.questions_in_group('G2') == exp


def test_dimension_value_frame(mock_question_key, resp_for_overlap_dim):

    exp_r = [(1, 'QC3', 2), (2, None, 3)]
    exp_c = ['Entry Id', 'dimension', 'value']
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    p = Processor(
        question_key=mock_question_key, survey_results=resp_for_overlap_dim)

    assert_frame_subset(p.dimension_value_frame('QC3', 'QC2'), exp_df)


def mock_dim_value_frame(self, dim_code, q_code):
    mock_c = ['Entry Id', 'dimension', 'value']
    mock_r = [
        (1, 'D1', 1),
        (2, 'D1', 2),
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


def test_data_for_visualizer(monkeypatch):
    exp = {'title': 'QC2',
           'levels': ['1', '2', '3'],
           'overall_f': [.375, .375, 0.25],
           'dimensions': [
               {'name': 'D1',
                'freq': [0.25, 0.5, 0.25]},
               {'name': 'D2',
                'freq': [0.5, 0.25, 0.25]}
           ]
           }
    monkeypatch.setattr(
        Processor, 'dimension_value_frame', mock_dim_value_frame)

    p = Processor()
    res = p.data_for_visualizer('QC1', 'QC2')
    assert res == exp
