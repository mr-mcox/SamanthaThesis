from bokeh.plotting import figure, show, output_file, hplot
from bokeh.models import NumeralTickFormatter
from scipy.stats import binom
import os


class SurveyPlot(object):

    """Creates visualization of survey data"""

    def __init__(self, data, title):
        self.data = data
        self.title = title
        self.data_formatted = self.data_for_visualization()
        self.location = os.getcwd()

        # Set default display flags
        self.display_overall = True
        self.display_cumulative = True
        self.display_range = True

    def draw(self):
        data = self.data_formatted

        output_file(os.path.join(self.location, data['title'] + '.html'))
        levels = data['levels']
        plots = list()

        # Set up stylings
        prim_bar_width = 0.5
        overall_bar_width = 0.2

        primary_color = '#3182bd'
        overall_color = '#969696'
        range_color = '#E6E6E6'

        overall_f = data['overall_f']

        # Overall bar positions to be used on each plot
        m_bar_x = [(x+1) + (overall_bar_width / 2) + (prim_bar_width / 2)
                   for x in range(len(overall_f))]
        m_bar_y = [h / 2 for h in overall_f]
        for dim in data['dimensions']:

            # Set up plot
            p = figure(plot_width=200,
                       plot_height=200,
                       x_range=levels,
                       y_range=[0, 1],
                       title=dim['name'],
                       tools="")
            p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
            dim_f = dim['freq']

            # Compute positions for bars
            bar_y = [h / 2 for h in dim_f]

            # Compute position for line
            line_x = [0] + levels

            # Compute positions for range
            range_x = line_x + list(reversed(line_x))
            range_y = [0] + dim['overall_range_low'] + \
                list(reversed([0] + dim['overall_range_high']))

            # Render range
            if (self.display_range and
                    self.display_overall and
                    self.display_cumulative):
                p.patches(xs=[range_x],
                          ys=[range_y],
                          color=range_color)

            # Render overall bars and offset for primary
            if self.display_overall:
                if self.display_cumulative:
                    line_y = [0] + data['overall_cum']
                    p.line(line_x, line_y, color=overall_color)
                p.rect(m_bar_x, m_bar_y, color=overall_color,
                       width=overall_bar_width, height=overall_f)

            # Display primary line
            if self.display_cumulative:
                line_y = [0] + dim['cum']
                p.line(line_x, line_y, color=primary_color)

            bar_x = [(x+1) for x in range(len(dim_f))]

            # Render primary bars
            p.rect(bar_x, bar_y, color=primary_color,
                   width=prim_bar_width, height=dim_f)

            plots.append(p)
        show(hplot(*plots))

    def freq_from_df(self, df, levels):
        freq = list()
        agg = df.groupby('value').size()
        pop_size = len(df)
        if pop_size == 0:
            return 0
        for level in levels:
            num_in_group = 0
            if level in agg.index:
                num_in_group = agg.get(level)
            freq.append(num_in_group / pop_size)

        return freq

    def cumulative_frequency(self, freq):
        cum = list()
        total_freq = 0
        for f in freq:
            total_freq = total_freq + f
            cum.append(total_freq)
        return cum

    def data_for_visualization(self):
        df = self.data
        df = df[df.dimension.notnull() & df.value.notnull()]
        output = dict()

        # Set title
        output['title'] = self.title

        # Set levels
        levels = sorted(df.value.unique().tolist(), reverse=True)
        level_s = [str(v) for v in levels]
        output['levels'] = level_s

        # Compute overall freq and cumulative frequency
        overall_f = self.freq_from_df(df, levels)
        overall_cum = self.cumulative_frequency(overall_f)
        output['overall_f'] = overall_f
        output['overall_cum'] = overall_cum

        # Compute dimensions
        dimensions = list()
        for dim in df.dimension.unique().tolist():
            df_d = df[df.dimension == dim]
            pop_size = len(df_d)
            freq = self.freq_from_df(df_d, levels)
            cum = self.cumulative_frequency(freq)
            ranges = binom.interval(0.95, pop_size, overall_cum)
            range_low = [x / pop_size for x in ranges[0]]
            range_high = [x / pop_size for x in ranges[1]]
            dimensions.append(
                {'name': dim,
                 'freq': freq,
                 'cum': cum,
                 'overall_range_low': range_low,
                 'overall_range_high': range_high,
                 })
        output['dimensions'] = dimensions

        return output


if __name__ == '__main__':
    data = {'title': 'Test Plot',
            'levels': ['1', '2', '3'],
            'overall_f': [0.2, 0.7, 0.1],
            'dimensions': [
                {'name': 'Group 1',
                 'freq': [0.25, 0.6, 0.15]},
                {'name': 'Group 2',
                 'freq': [0.15, 0.45, 0.4]}
            ]
            }
    sp = SurveyPlot(data=data)
    sp.location = '/Users/mcox/Dropbox/MDIS/tmp/'
    sp.draw()
