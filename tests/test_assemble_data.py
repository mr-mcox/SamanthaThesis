from SamanthaThesis.process import Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest


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
    resp_r = [
        (1, 1, 2),
        (2, 2, 3),
    ]

    resp_c = ['Entry Id', 'Q1', 'Q2']

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


def test_regular_dimension(mock_question_key, mock_resp):

    exp_r = [(1, 'QC1', 1), (2, 'QC1', 2)]
    exp_c = ['Entry Id', 'dimension_code', 'value']
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index('Entry Id')

    p = Processor(question_key=mock_question_key, survey_results=mock_resp)

    assert_frame_equal(p.dimension_values, exp_df)


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
