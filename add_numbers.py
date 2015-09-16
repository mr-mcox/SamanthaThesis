# coding: utf-8
import pandas as pd
df = pd.read_excel('DI Access Survey_Excel.xls', 0)
value_vars = df.columns[2:]
id_vars = df.columns[1]
df.set_index('Entry Id', inplace=True)
df_ids = df.ix[:, id_vars].reset_index()
df2 = df.ix[:, value_vars]
df_melt = pd.melt(df2.reset_index(), id_vars='Entry Id')
number_map = pd.read_excel('numerical_template_with_numbers.xlsx')
df_melt_num = pd.merge(df_melt, number_map, how='left')
df_melt_num.ix[df_melt_num.numerical_value.isnull(), 'numerical_value'] = df_melt_num.ix[
    df_melt_num.numerical_value.isnull(), 'value']
df_pivot = pd.pivot_table(
    df_melt_num, values='numerical_value', index='Entry Id', columns='variable', aggfunc='max')
df_all = pd.merge(df_ids, df_pivot.reset_index(), on='Entry Id')
col_order = ['Entry Id'] + [id_vars] + value_vars.tolist()
pd.DataFrame(df_all, columns=col_order) .to_excel(
    'survey_converted_to_numerical.xlsx', index=False)
