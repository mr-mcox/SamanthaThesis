from SamanthaThesis.process import Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest
import numpy as np


def assert_frame_subset(actual, expected):
    assert_frame_equal(actual.loc[:, expected.columns], expected)


@pytest.fixture(scope='module')
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


@pytest.fixture(scope='module')
def mock_resp():
    resp_c = ['Entry Id', 'Q1', 'Q2']
    resp_r = [
        (1, 1, 2),
        (2, 2, 3),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
def mock_resp_with_blank_dim():
    resp_c = ['Entry Id', 'Q1']
    resp_r = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, None),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
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


@pytest.fixture(scope='module')
def mock_complex_dim_resp():
    resp_c = ['Entry Id', 'Q1', 'Q2']
    resp_r = [
        (1, 1, 10),
        (2, 2, 20),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
def mock_dim_response_map():
    resp_c = ['Entry Id', 'variable', 'value', 'mapped_value']
    resp_r = [
        (1, "Q1", "One", 1),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
def resp_for_overlap_dim():
    resp_c = ['Entry Id', 'Q1', 'Q2', 'Q3']
    resp_r = [
        (1, 1, 2, 1),
        (2, 2, 3, 0),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
def mock_resp_for_pre_map():
    resp_c = ['Entry Id', 'Q1', 'Q2']
    resp_r = [
        (1, 1, "Two"),
        (2, 2, 3),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


@pytest.fixture(scope='module')
def mock_response_map():
    resp_c = ['variable', 'value', 'numerical_value']
    resp_r = [
        ("Q2", "One", 1),
        ("Q2", "Two", 2),
    ]

    return pd.DataFrame.from_records(resp_r, columns=resp_c)


class TestDimensionFormat():

    def test_regular_dimension(self, mock_question_key, mock_resp):

        exp_r = [(1, 'QC1', 1), (2, 'QC1', 2)]
        exp_c = ['Entry Id', 'dimension_code', 'value']
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id')

        p = Processor(question_key=mock_question_key, survey_results=mock_resp)

        assert_frame_subset(p.dimension_values, exp_df)

    def test_dimension_key(self, mock_question_key):
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

    def test_single_dimension_bins(self,
                                   mock_question_key,
                                   mock_resp,
                                   monkeypatch):
        exp_c = ['Entry Id', 'dimension_code', 'bin']
        exp_r = [(1, 'QC1', "1-2"), (2, 'QC1', "2-3")]
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id').convert_objects()

        def mock_percentile(a, q):
            return np.array([1, 2, 3, 4, 5])

        monkeypatch.setattr(np, 'percentile', mock_percentile)
        p = Processor(question_key=mock_question_key, survey_results=mock_resp)

        assert_frame_subset(p.dimension_values, exp_df)

    def test_dim_bins_with_blank_dim(self,
                                     mock_question_key,
                                     mock_resp_with_blank_dim,
                                     monkeypatch):
        exp_c = ['Entry Id', 'dimension_code', 'bin']
        exp_r = [
            (1, 'QC1', "1.0-2.0"),
            (2, 'QC1', "2.0-3.0"),
            (3, 'QC1', "3.0-4.0"),
            (4, 'QC1', "4.0-5.0"),
            (5, 'QC1', "5.0-6.0"),
            (6, 'QC1', "5.0-6.0"),
            (7, 'QC1', None),
        ]
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id').convert_objects()

        p = Processor(question_key=mock_question_key,
                      survey_results=mock_resp_with_blank_dim)

        assert_frame_subset(p.dimension_values, exp_df)

    def test_multiple_dimension_bins(self, mock_complex_dim_question_key,
                                     mock_complex_dim_resp,
                                     monkeypatch):
        exp_c = ['Entry Id', 'dimension_code', 'bin']
        exp_r = [(1, 'QC1', "1-2"),
                 (2, 'QC1', "2-3"),
                 (1, 'QC2', "10-20"),
                 (2, 'QC2', "20-30")]
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id').convert_objects()

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

    def test_overlapping_dim_indicator_variable(self, mock_question_key,
                                                resp_for_overlap_dim,
                                                monkeypatch):

        res = Processor(question_key=mock_question_key,
                        survey_results=resp_for_overlap_dim).dimension_values

        res = res.reset_index().set_index(
            ['Entry Id', 'dimension_code'])

        assert res.loc[(1, 'QC3'), 'bin'] == 'QC3'
        assert np.isnan(res.loc[(2, 'QC3'), 'bin'])


class TestResponseFormat():

    def test_map_values(self, mock_resp_for_pre_map,
                        mock_question_key,
                        mock_dim_response_map):
        exp_r = [(1, 'QC1', 1), (2, 'QC1', 2)]
        exp_c = ['Entry Id', 'dimension_code', 'value']
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id')

        p = Processor(question_key=mock_question_key,
                      dim_response_map=mock_dim_response_map,
                      survey_results=mock_resp_for_pre_map)

        assert_frame_subset(p.dimension_values, exp_df)

    def test_mapped_response(self,
                             mock_resp_for_pre_map,
                             mock_question_key,
                             mock_response_map):

        exp_r = [(1, 'QC2', 2.0), (2, 'QC2', 3.0)]
        exp_c = ['Entry Id', 'question_code', 'value']
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id')

        p = Processor(question_key=mock_question_key,
                      survey_results=mock_resp_for_pre_map,
                      response_map=mock_response_map)

        assert_frame_subset(p.response_values, exp_df.convert_objects())

    def test_regular_response(self, mock_question_key, mock_resp):

        exp_r = [(1, 'QC2', 2), (2, 'QC2', 3)]
        exp_c = ['Entry Id', 'question_code', 'value']
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id')

        p = Processor(question_key=mock_question_key, survey_results=mock_resp)

        assert_frame_subset(p.response_values, exp_df)


class TestOutputInterface():

    def test_dimensions_in_group(self, mock_question_key):
        exp = ['QC3', 'QC4']

        p = Processor(question_key=mock_question_key)
        assert p.dimensions_in_group('G3') == exp

    def test_questions_in_group(self, mock_question_key):
        exp = ['QC2']

        p = Processor(question_key=mock_question_key)
        assert p.questions_in_group('G2') == exp

    def test_dimension_value_frame(self,
                                   mock_question_key,
                                   resp_for_overlap_dim):

        exp_r = [(1, 'QC3', 2), (2, None, 3)]
        exp_c = ['Entry Id', 'dimension', 'value']
        exp_df = pd.DataFrame.from_records(
            exp_r, columns=exp_c).set_index('Entry Id')

        p = Processor(
            question_key=mock_question_key,
            survey_results=resp_for_overlap_dim)

        assert_frame_subset(p.dimension_value_frame('QC3', 'QC2'), exp_df)
