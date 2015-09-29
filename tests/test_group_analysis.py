from SamanthaThesis.process import GroupAnalysis, Analyzer, Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest

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
    if group is not None:
        return ['D1', 'D2']
    else:
        return None


def mock_questions_in_group(self, group):
    if group is not None:
        return ['Q1', 'Q2']
    else:
        return None

def mock_all_questions(self):
    return ['Q1', 'Q2']

def mock_all_dimensions(self):
    return ['D1', 'D2']

@pytest.fixture(params=[
    ('DG1', 'QG1'),
    ('DG1', None),
    (None, 'QG1'),
    (None, None),
    ])
def params_to_use(request):
    return request.param


def test_sig_dim_relationship_list_order(monkeypatch, params_to_use):
    monkeypatch.setattr(
        Analyzer, 'significance_of_relationship', mock_sig_of_relationship)
    monkeypatch.setattr(
        Processor, 'dimensions_in_group', mock_dimensions_in_group)
    monkeypatch.setattr(
        Processor, 'questions_in_group', mock_questions_in_group)
    monkeypatch.setattr(
        Processor, 'all_questions', mock_all_questions)
    monkeypatch.setattr(
        Processor, 'all_dimensions', mock_all_dimensions)

    p = Processor()
    dim_group = 'DG1'
    q_group = 'QG1'

    res = GroupAnalysis(processor=p).significant_relationships_list(
        *params_to_use)

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
