import pandas as pd
import numpy as np
from scipy.stats.mstats import kruskalwallis
from scipy.stats import linregress
import re
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
                 question_key=None,
                 dim_response_map=None,
                 response_map=None,
                 ):

        self.survey_results = import_if_excel(survey_results)
        self.question_key = import_if_excel(question_key)
        self.response_map = import_if_excel(response_map)
        self.dim_response_map = import_if_excel(dim_response_map)
        self.num_bins = 5

    @property
    def dimension_values(self):
        if not hasattr(self, '_dimension_values'):
            qk = self.question_key
            dims = qk[qk.dimension_or_question == 'dimension']
            dim_qs = dims.variable.tolist()

            res_melt = pd.melt(self.survey_results, id_vars='Entry Id')
            res_dim = res_melt[res_melt.variable.isin(dim_qs)]

            # Override with mapped values if available
            if self.dim_response_map is not None:
                rm = self.dim_response_map.set_index(['Entry Id', 'variable'])
                res_dim.set_index(['Entry Id', 'variable'], inplace=True)
                res_dim.loc[res_dim.index.isin(rm.index), 'value'] = rm[
                    'mapped_value']
                res_dim.reset_index(inplace=True)

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
                    mask = (values.notnull() & (values != 0))
                    indicator_v.loc[mask] = code
                    indicator_v.loc[~mask] = "not_" + str(code)
                    dim_values.loc[code_mask, 'bin'] = indicator_v

                    # Add dimension as number
                    indicator_vn = pd.Series(index=values.index)
                    indicator_vn.loc[mask] = 1
                    indicator_vn.loc[~mask] = 0
                    dim_values.loc[
                        code_mask, 'dimension_as_num'] = indicator_vn
                else:
                    values = values[values.notnull()]
                    str_is_num = values.map(
                        lambda s: re.search(str(s), "[\d\.]+") is None)
                    if (str_is_num | values.isnull()).all():
                        values = values.convert_objects(convert_numeric=True)
                        bin_size = (100 / self.num_bins)
                        ptile_num = range(self.num_bins + 1)
                        ptile = np.percentile(
                            values, [x*bin_size for x in ptile_num])
                        bin_nums = pd.Series(
                            np.digitize(values, ptile), index=values.index)
                        dim_values.loc[code_mask, 'bin'] = bin_nums.apply(
                            bin_text, ptiles=ptile)
                        dim_values.loc[code_mask, 'dimension_as_num'] = values
                    else:
                        dim_values.loc[code_mask, 'bin'] = values
                        dim_values.loc[code_mask, 'dimension_as_num'] = None

            cols = ['dimension_code', 'value', 'bin', 'dimension_as_num']
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

    @property
    def q_key(self):
        if not hasattr(self, '_q_key'):
            qk = self.question_key
            qs = qk[qk.dimension_or_question == 'question']

            qs.rename(columns={
                'analysis_code': 'question_code',
                'variable': 'text',
                'question_theme': 'group'
            }, inplace=True)
            self._q_key = qs.set_index('question_code')
        return self._q_key

    @property
    def response_values(self):
        if not hasattr(self, '_response_values'):
            qk = self.question_key
            qs = qk[qk.dimension_or_question == 'question'].variable.tolist()
            res_melt = pd.melt(self.survey_results, id_vars='Entry Id')
            res_qs = res_melt[res_melt.variable.isin(qs)]

            # Override with mapped values if available
            if self.response_map is not None:
                rm = self.response_map.set_index(['variable', 'value'])
                res_qs.set_index(['variable', 'value'], inplace=True)
                res_qs.loc[res_qs.index.isin(rm.index), 'mapped_value'] = rm[
                    'numerical_value']
                res_qs.reset_index(inplace=True)
                res_qs.loc[res_qs.mapped_value.notnull(), 'value'] = res_qs.loc[
                    res_qs.mapped_value.notnull(), 'mapped_value']
                res_qs = res_qs.convert_objects()

            res_qs = pd.merge(res_qs, qk, on='variable').set_index('Entry Id')
            res_qs.rename(
                columns={'analysis_code': 'question_code'}, inplace=True)
            columns = ['question_code', 'value']
            self._response_values = res_qs.loc[:, columns]
        return self._response_values

    def dimensions_in_group(self, group):
        dk = self.dimension_key
        return dk[dk.group == group].index.tolist()

    def questions_in_group(self, group):
        qk = self.q_key
        return qk[qk.group == group].index.tolist()

    def all_dimensions(self):
        dk = self.dimension_key
        return dk.index.tolist()

    def all_questions(self):
        qk = self.q_key
        return qk.index.tolist()

    def dimension_value_frame(self, dim_code, q_code):
        dv = self.dimension_values
        dims = dv.ix[
            dv.dimension_code == dim_code, ['bin', 'dimension_as_num']]
        dims.rename(columns={'bin': 'dimension'}, inplace=True)

        rv = self.response_values
        resp = rv.ix[rv.question_code == q_code].value
        resp[resp == 0] = None

        return dims.join(resp)


class GroupAnalysis(object):

    """"Analyzes groups of responses and dimensions"""

    def __init__(self, processor=None):
        self.processor = processor
        self.alpha = 0.05

    def significant_relationships_list(self,
                                       d_group=None,
                                       q_group=None,
                                       test_type='kruskalwallis'):
        alpha = self.alpha
        dims = list()
        if d_group is not None:
            dims = self.processor.dimensions_in_group(d_group)
        else:
            dims = self.processor.all_dimensions()

        qs = list()
        if q_group is not None:
            qs = self.processor.questions_in_group(q_group)
        else:
            qs = self.processor.all_questions()

        dim_q_combos = list()
        for d in dims:
            for q in qs:
                dim_q_combos.append((d, q))

        analysis_results = list()

        for combo in dim_q_combos:
            a = Analyzer(processor=self.processor)
            (d, q) = combo
            p_val = a.significance_of_relationship(d, q, test_type)
            analysis_results.append((d, q, p_val))

        cols = ['dimension', 'question', 'p_value']
        df = pd.DataFrame().from_records(analysis_results, columns=cols)

        df.sort('p_value', inplace=True)
        df['comp_p'] = [(x + 1) * alpha / len(df) for x in range(len(df))]
        df['sig'] = False
        df.loc[df.p_value <= df.comp_p, 'sig'] = True
        df['test_type'] = test_type

        df.set_index(['dimension', 'question'], inplace=True)

        return df


class Analyzer(object):

    """"Analyzes a single question and dimension"""

    def __init__(self, processor=None):
        self.processor = processor

    def significance_of_relationship(self, dimension, question, test_type):
        frame = self.processor.dimension_value_frame(dimension, question)
        frame = frame[frame.dimension.notnull() & frame.value.notnull()]

        if test_type == 'kruskalwallis':
            return self.sig_relationship_kruskalwallis(frame)
        if test_type == 'linearmodel':
            return self.sig_relationship_linear_model(frame)

    def sig_relationship_kruskalwallis(self, frame):
        factors = frame.dimension.unique().tolist()
        data_sets = list()
        for factor in factors:
            data_sets.append(frame.ix[frame.dimension == factor, 'value'])

        if len(data_sets) < 2:
            return 1
        else:
            return kruskalwallis(*data_sets)[1]

    def sig_relationship_linear_model(self, frame):
        return linregress(frame['dimension_as_num'], frame['value'])[3]
