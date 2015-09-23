from SamanthaThesis.process import GroupAnalysis, Analyzer, Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal


def assert_frame_subset(actual, expected):
    assert_frame_equal(actual.loc[:, expected.columns], expected)


def mock_sig_of_relationship(self, dimension, question):
    if(dimension == 'D1' and question == 'Q1'):
        return 0.01
    if(dimension == 'D1' and question == 'Q2'):
        return 0.1
    if(dimension == 'D2' and question == 'Q1'):
        return 0.02
    if(dimension == 'D2' and question == 'Q2'):
        return 0.045


def mock_dimensions_in_group(self, group):
    return ['D1', 'D2']


def mock_questions_in_group(self, group):
    return ['Q1', 'Q2']


def test_sig_dim_relationship_list_order(monkeypatch):
    monkeypatch.setattr(
        Analyzer, 'significance_of_relationship', mock_sig_of_relationship)
    monkeypatch.setattr(
        Processor, 'dimensions_in_group', mock_dimensions_in_group)
    monkeypatch.setattr(
        Processor, 'questions_in_group', mock_questions_in_group)

    p = Processor()
    dim_group = 'DG1'
    q_group = 'QG1'

    res = GroupAnalysis(processor=p).significant_relationships_list(
        dim_group, q_group)

    exp_c = ['dimension', 'question', 'p_value', 'sig']
    exp_r = [
        ('D1', 'Q1', 0.01, True),
        ('D2', 'Q1', 0.02, True),
        ('D2', 'Q2', 0.045, False),
        ('D1', 'Q2', 0.1, False),
    ]
    exp_df = pd.DataFrame.from_records(
        exp_r, columns=exp_c).set_index(['dimension', 'question'])

    assert_frame_subset(res, exp_df)
