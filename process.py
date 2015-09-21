import pandas as pd
import numpy as np
import pdb


def import_if_excel(source):
    if type(source) is str:
        return pd.read_excel(source, 0)
    else:
        return source


def bin_text(bin_num, ptiles):
    if bin_num >= len(ptiles):
        return str(ptiles[-2]) + "-" + str(ptiles[-1])
    else:
        return str(ptiles[bin_num-1]) + "-" + str(ptiles[bin_num])


class Processor(object):

    """Manipulate and process survey data for Samantha's thesis"""

    def __init__(self,
                 survey_results=None,
                 question_key=None):

        self.survey_results = import_if_excel(survey_results)
        self.question_key = import_if_excel(question_key)

    @property
    def dimension_values(self):
        if not hasattr(self, '_dimension_values'):
            qk = self.question_key
            dims = qk[qk.dimension_or_question == 'dimension']
            dim_qs = dims.variable.tolist()

            res_melt = pd.melt(self.survey_results, id_vars='Entry Id')
            res_dim = res_melt[res_melt.variable.isin(dim_qs)]

            dim_values = pd.merge(
                res_dim, dims, on='variable').set_index('Entry Id')
            dim_values.rename(
                columns={'analysis_code': 'dimension_code'}, inplace=True)

            # Set up bins for each dimension code
            dim_codes = dim_values.dimension_code.unique()
            for code in dim_codes:
                code_mask = (dim_values.dimension_code == code)
                values = dim_values.loc[code_mask, 'value']
                if self.dimension_key.get_value(code, 'type') == 'overlapping':
                    indicator_v = pd.Series(index=values.index)
                    indicator_v.loc[values.notnull() & (values != 0)] = code
                    dim_values.loc[code_mask, 'bin'] = indicator_v
                else:
                    if values.map(np.isreal).all():
                        ptile = np.percentile(values, [x*20 for x in range(6)])
                        bin_nums = pd.Series(
                            np.digitize(values, ptile), index=values.index)
                        dim_values.loc[code_mask, 'bin'] = bin_nums.apply(
                            bin_text, ptiles=ptile)
                    else:
                        dim_values.loc[code_mask, 'bin'] = dim_values.value

            cols = ['dimension_code', 'value', 'bin']
            self._dimension_values = dim_values.ix[:, cols]
        return self._dimension_values

    @property
    def dimension_key(self):
        if not hasattr(self, '_dimension_key'):
            qk = self.question_key
            dims = qk[qk.dimension_or_question == 'dimension']

            dims.rename(columns={
                'analysis_code': 'dimension_code',
                'variable': 'text',
                'question_theme': 'group'
            }, inplace=True)

            # Indicate that dimesions that don't have unique groups are
            # overlapping
            dim_count = dims.groupby('group').size()
            dims_overlapping = dim_count[dim_count > 1].index.tolist()
            dims.loc[:, 'type'] = 'complete'
            dims.loc[dims.group.isin(dims_overlapping), 'type'] = 'overlapping'

            cols = ['dimension_code', 'text', 'group', 'type']
            self._dimension_key = dims.ix[:, cols].set_index('dimension_code')

        return self._dimension_key
