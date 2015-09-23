from bokeh.plotting import figure, show, output_file, vplot
from bokeh.models import NumeralTickFormatter
from bokeh.charts import Area
from unittest.mock import patch
import os


class SurveyPlot(object):

    """Creates visualization of survey data"""

    def __init__(self, data):
        self.data = data
        self.location = os.getcwd()

    def draw(self):
        data = self.data

        output_file(os.path.join(self.location, data['title'] + '.html'))
        levels = data['levels']
        plots = list()
        prim_bar_width = 0.5
        comp_bar_width = 0.2
        overall_f = data['overall_f']
        m_bar_x = [(x+1) + (comp_bar_width / 2) for x in range(len(overall_f))]
        m_bar_y = [h / 2 for h in overall_f]
        for dim in data['dimensions']:
            p = figure(plot_width=400,
                       plot_height=400,
                       x_range=levels,
                       y_range=[0, 1],
                       title=dim['name'],
                       tools="")
            p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
            dim_f = dim['freq']
            bar_x = [(x+1) - (prim_bar_width / 2) for x in range(len(dim_f))]
            bar_y = [h / 2 for h in dim_f]

            p.rect(bar_x, bar_y, color='#3182bd', 
                width=prim_bar_width, height=dim_f)

            p.rect(m_bar_x, m_bar_y, color='#d9d9d9',
                   width=0.2, height=overall_f)
            plots.append(p)
        show(vplot(*plots))


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
