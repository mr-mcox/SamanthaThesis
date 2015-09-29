from SamanthaThesis.process import GroupAnalysis, Analyzer, Processor
import pandas as pd
from scipy.stats.mstats import kruskalwallis
from scipy.stats import linregress


def mock_dim_value_frame(self, dim_code, q_code):
    mock_c = ['Entry Id', 'dimension', 'value', 'dimension_as_num']
    mock_r = [
        (1, 'D1', 1, 1),
        (1, 'D1', 2, 1),
        (1, 'D1', 5, 1),
        (1, 'D2', 2, 2),
        (1, 'D2', 4, 2),
        (1, 'D2', 7, 2),
    ]
    df = pd.DataFrame().from_records(
        mock_r, columns=mock_c).set_index('Entry Id')
    return df


def test_signficance_of_relationship(monkeypatch):
    monkeypatch.setattr(Processor,
                        'dimension_value_frame',
                        mock_dim_value_frame)

    mock_data = mock_dim_value_frame(None, None, None)
    exp_arr_1 = mock_data.ix[mock_data.dimension == 'D1', 'value']
    exp_arr_2 = mock_data.ix[mock_data.dimension == 'D2', 'value']
    exp = kruskalwallis(exp_arr_1, exp_arr_2)[1]

    p = Processor()
    a = Analyzer(processor=p)
    p_val = a.significance_of_relationship('D1', 'Q1', 'kruskalwallis')
    assert p_val == exp


def test_signficance_of_relationship_lm(monkeypatch):
    monkeypatch.setattr(Processor,
                        'dimension_value_frame',
                        mock_dim_value_frame)

    mock_data = mock_dim_value_frame(None, None, None)
    exp_arr_1 = mock_data['dimension_as_num']
    exp_arr_2 = mock_data['value']
    exp = linregress(exp_arr_1, exp_arr_2)[3]

    p = Processor()
    a = Analyzer(processor=p)
    p_val = a.significance_of_relationship('D1', 'Q1', 'linearmodel')
    assert p_val == exp
