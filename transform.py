# coding: utf-8
import pandas as pd
import os.path
df = pd.read_excel('../inputs/DI Access Survey_Excel.xls', 0)
dfm = pd.melt(df, id_vars='Entry Id')
df_names = dfm.ix[:, ['variable', 'value']].drop_duplicates()
df_names.groupby('variable').size()
responses_by_q = df_names.groupby('variable').size()
dfm.ix[dfm.variable.isin( responses_by_q[responses_by_q < 10] ), ['variable', 'value']
       ]
q_mask = dfm.variable.isin(responses_by_q[responses_by_q < 10].index)
q_out = dfm.ix[q_mask, ['variable', 'value']].drop_duplicates()
q_out['numerical_value'] = None
q_out.to_excel('numerical_template.xlsx', index=False)
responses_by_q[responses_by_q >= 10].index.drop_duplicates()
d_qs = responses_by_q[responses_by_q >= 10].index.drop_duplicates()
dropped_questions = pd.DataFrame({'question': d_qs})
dropped_questions.to_excel(
    'inferred_non_numerical_questions.xlsx', index=False)

#Only export questions file if it currently doesn't exist
if not os.path.isfile('question_template.xlsx'):
    qs_out = dfm.ix[q_mask, ['variable']].drop_duplicates()
    qs_out['analysis_code'] = None
    qs_out['question_theme'] = None
    qs_out.to_excel('question_template.xlsx', index=False)

#Export resutls for any question that asks how many which does not have number only answer
if not os.path.isfile('non_numerical_dimension_map.xlsx'):
    non_numerical_resp = dfm.ix[dfm.variable.str.contains("How many") & dfm.value.str.contains("\D+")]
    non_numerical_resp.to_excel('non_numerical_dimension_map.xlsx',index=False)