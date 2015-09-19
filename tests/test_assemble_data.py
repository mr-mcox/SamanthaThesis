from SamanthaThesis.process import Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest
import numpy as np
import pdb


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

    assert_frame_equal(p.dimension_values.loc[:, exp_df.columns], exp_df)


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

    assert_frame_equal(proc.dimension_key, exp_df)


def test_single_dimension_bins(mock_question_key, mock_resp, monkeypatch):
    exp_c = ['Entry Id', 'dimension_code', 'bin']
    exp_r = [(1, 'QC1', "1-2"), (2, 'QC1', "2-3")]
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    def mock_percentile(a, q):
        return np.array([1, 2, 3, 4, 5])

    monkeypatch.setattr(np, 'percentile', mock_percentile)
    p = Processor(question_key=mock_question_key, survey_results=mock_resp)

    assert_frame_equal(p.dimension_values.loc[:, exp_df.columns], exp_df)


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

    assert_frame_equal(proc.dimension_values.loc[:, exp_df.columns], exp_df)
