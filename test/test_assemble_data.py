from ..process import Processor
import pandas as pd
from pandas.util.testing import assert_frame_equal

def test_regular_dimension():
    question_r = [
        ("Q1", "QC1", "G1","dimension"),
        ("Q2", "QC2", "G2","question"),
    ]
    question_c = ['variable',
                  'analysis_code',
                  'question_theme',
                  'dimension_or_question']

    mock_q_key = pd.DataFrame.from_records(question_r, columns=question_c)

    resp_r = [
        (1, 1, 2),
        (2, 2, 3),
    ]

    resp_c = ['Entry Id', 'Q1', 'Q2']

    mock_resp = pd.DataFrame.from_records(resp_r, columns=resp_c)

    exp_r = [(1, 'QC1', 1), (2, 'QC1', 2)]
    exp_c = ['Entry Id', 'dimension_code', 'value']
    exp_df = pd.DataFrame.from_records(exp_r, columns=exp_c).set_index('Entry Id')

    p = Processor(question_key=mock_q_key, survey_results=mock_resp)

    assert_frame_equal(p.dimension_values, exp_df)
