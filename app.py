import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output # this is for web framework
from scipy import stats # this calculates Pearson's correlation coefficient

import os # this is for file handling (paths, directories, etc.)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data') # directory with data files

results = pd.read_csv(os.path.join(DATA_DIR, 'results.csv'), na_values=['\\N'])
drivers = pd.read_csv(os.path.join(DATA_DIR, 'drivers.csv'), na_values=['\\N'])
races = pd.read_csv(os.path.join(DATA_DIR, 'races.csv'), na_values=['\\N'])
qualifying = pd.read_csv(os.path.join(DATA_DIR, 'qualifying.csv'), na_values=['\\N'])

# Merging stuff now

df= results.merge(drivers[['driverId', 'forename', 'surname', 'nationality']], on='driverId')
df = df.merge(races[['raceId', 'year', 'name', 'round']], on='raceId')

df['driver_name'] = df['forename'] + ' ' + df['surname']

# Cleaning up the data now

df = df[(df['grid']>0) & (df['position'].notna())].copy() # only keep rows where grid position is greater than 0 and final position is not null
df['position'] = df['position'].astype(int)
df['grid_delta'] = df['grid'] - df['position'] 

# Intializing App
app = Dash(__name__, title='F1 Grid Analysis')

# Colour Palette
C = {
    'bg':       '#0d0d0d',
    'surface':  '#1a1a1a',
    'card':     '#242424',
    'border':   '#2e2e2e',
    'accent':   '#e8002d',
    'accent2':  '#ff8c00',
    'text':     '#f0f0f0',
    'muted':    '#888888',
    'blue':     '#00aaff',
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', #transparent
    plot_bgcolor='rgba(0,0,0,0)', #transparent
    font=dict(color=C['text'], family='Inter, Arial, sans-serif'),
    xaxis=dict(gridcolor=C['border'], zerolinecolor=C['border']),
    yaxis=dict(gridcolor=C['border'], zerolinecolor=C['border']),
    margin=dict(l=40, r=20, t=40, b=40),
)
corr, pval = stats.pearsonr(df['grid'], df['position'])

#building app layout

app.layout= html.Div(className='page', children=[
    html.Header(className='header', children=[
        html.Div(className='header-inner', children=[
            html.Div(className='logo', children=[
                html.Span('F1', className='logo-f1'),
                html.Span('Grid Analytics', className='logo-sub'),
            ]),
            html.P(
                'Which drivers consistently outperform their starting grid position, and which ones underperform? This dashboard explores the relationship between starting grid position and finishing position in Formula 1.',
                className='header-tagline'
            ),
        ])
    ]),


html.Section(className='stat-banner', children=[
        html.Div(className='stat-card', children=[
            html.P('Overall Correlation', className='stat-label'),
            html.H2(f'{corr:.3f}', className='stat-value accent'),
            html.P('Grid → Finish (Pearson r)', className='stat-sub'),
        ]),
        html.Div(className='stat-card', children=[
            html.P('Total Race Entries', className='stat-label'),
            html.H2(f'{len(df):,}', className='stat-value'),
            html.P('1950 – 2024', className='stat-sub'),
        ]),
        html.Div(className='stat-card', children=[
            html.P('Avg Grid Delta', className='stat-label'),
            html.H2(f'{df["grid_delta"].mean():+.2f}', className='stat-value accent2'),
            html.P('Places gained per race', className='stat-sub'),
        ]),
    ]),

html.Section(className='section', children=[
        html.H2('Grid Position vs. Finishing Position — All Time', className='section-title'),
        html.P('Each dot is a single race entry. The red line shows the trend.',
               className='section-desc'),
        dcc.Graph(id='scatter-all', config={'displayModeBar': False}),
        ]),

#drop dpwn section

html.Section(className='section', children=[
        html.H2('Driver Deep Dive', className='section-title'),
        html.P('Select a driver to explore their career grid performance.',
               className='section-desc'),

        html.Div(className='controls', children=[
            html.Div(className='control-group', children=[
                html.Label('Select Driver', className='control-label'),
                dcc.Dropdown(
                    id='driver-select',
                    options=[{'label': row['driver_name'], 'value': row['driverId']}
                             for _, row in df.groupby(['driverId','driver_name'])
                             .size().reset_index().iterrows()],
                    value=1,
                    clearable=False,
                    className='dropdown',
                ),
            ]),
            html.Div(className='control-group', children=[
                html.Label('Year Range', className='control-label'),
                dcc.RangeSlider(
                    id='year-range',
                    min=int(df['year'].min()),
                    max=int(df['year'].max()),
                    value=[int(df['year'].min()), int(df['year'].max())],
                    marks={y: str(y) for y in range(1950, 2025, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False},
                ),
            ]),
        ]),

        html.Div(id='driver-stats', className='stat-banner mini'),
        dcc.Graph(id='driver-scatter',    config={'displayModeBar': False}),
        dcc.Graph(id='driver-career',     config={'displayModeBar': False}),
    ]),

#compare drivers

html.Section(className='section', children=[
        html.H2('Compare Two Drivers', className='section-title'),
        html.P('Select two drivers to compare their grid performance head to head.',
               className='section-desc'),

        html.Div(className='controls two-col', children=[
            html.Div(className='control-group', children=[
                html.Label('Driver A', className='control-label red'),
                dcc.Dropdown(
                    id='compare-a',
                    options=[{'label': row['driver_name'], 'value': row['driverId']}
                             for _, row in df.groupby(['driverId','driver_name'])
                             .size().reset_index().iterrows()],
                    value=1,
                    clearable=False,
                    className='dropdown',
                ),
            ]),
            html.Div(className='control-group', children=[
                html.Label('Driver B', className='control-label blue'),
                dcc.Dropdown(
                    id='compare-b',
                    options=[{'label': row['driver_name'], 'value': row['driverId']}
                             for _, row in df.groupby(['driverId','driver_name'])
                             .size().reset_index().iterrows()],
                    value=30,
                    clearable=False,
                    className='dropdown',
                ),
            ]),
        ]),

        html.Div(id='compare-stats', className='stat-banner mini'),
        dcc.Graph(id='compare-bar',    config={'displayModeBar': False}),
        dcc.Graph(id='compare-delta',  config={'displayModeBar': False}),
    ]),

html.Footer(className='footer', children=[
        html.P('Data: Ergast F1 World Championship Dataset · Built with Plotly Dash'),
    ]),
])

# callback

@app.callback(
    Output('scatter-all', 'figure'),
    Input('scatter-all', 'id')
)
def global_scatter(_):
    sample = df.sample(min(3000, len(df)), random_state=42)
    m, b, *_ = stats.linregress(df['grid'], df['position'])
    x_line = np.linspace(1, df['grid'].max(), 100)

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=sample['grid'], 
        y=sample['position'],
        mode='markers',
        marker=dict(color=C['accent'], size=4, opacity=0.25),
        hovertemplate='Grid: %{x}<br>Finish: %{y}',
        name='Race entry'
        ))
    fig.add_trace(go.Scatter(
        x=x_line,
        y=m*x_line + b,
        mode='lines',
        line=dict(color=C['accent2'], width=2),
        name=f'Trend (r={corr:.3f})'
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title='Starting Grid Position',
        yaxis_title='Finishing Position',
        height=420,
    )
    return fig

@app.callback(
    Output('driver-stats', 'children'),
    Output('driver-scatter', 'figure'),
    Output('driver-career', 'figure'),
    Input('driver-select', 'value'),
    Input('year-range', 'value'),
)
def driver_deep_dive(driver_id, year_range):
    d = df[
        (df['driverId'] == driver_id) &
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1])
    ].copy()

    name      = d['driver_name'].iloc[0] if len(d) else 'Unknown'
    avg_delta = d['grid_delta'].mean() if len(d) else 0
    avg_grid  = d['grid'].mean() if len(d) else 0
    avg_finish= d['position'].mean() if len(d) else 0
    wins      = (d['position'] == 1).sum()
    poles     = (d['grid'] == 1).sum()

    stats_cards = html.Div(className='stat-banner mini', children=[
        html.Div(className='stat-card mini', children=[
            html.P('Races',      className='stat-label'),
            html.H3(str(len(d)), className='stat-value'),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Avg Grid',          className='stat-label'),
            html.H3(f'{avg_grid:.1f}',  className='stat-value'),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Avg Finish',          className='stat-label'),
            html.H3(f'{avg_finish:.1f}',  className='stat-value'),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Avg Delta',            className='stat-label'),
            html.H3(f'{avg_delta:+.2f}',   className='stat-value accent'),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Wins',     className='stat-label'),
            html.H3(str(wins), className='stat-value'),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Poles',     className='stat-label'),
            html.H3(str(poles), className='stat-value'),
        ]),
    ])

    fig_scatter = go.Figure()
    if len(d) > 1:
        m, b, r, *_ = stats.linregress(d['grid'], d['position'])
        x_line = np.linspace(d['grid'].min(), d['grid'].max(), 50)
        fig_scatter.add_trace(go.Scatter(
            x=d['grid'], y=d['position'],
            mode='markers',
            marker=dict(color=C['accent'], size=7, opacity=0.75),
            text=d['year'].astype(str) + ' ' + d['name'],
            hovertemplate='%{text}<br>Grid %{x} → P%{y}<extra></extra>',
            name=name,
        ))
        fig_scatter.add_trace(go.Scatter(
            x=x_line, y=m * x_line + b,
            mode='lines',
            line=dict(color=C['accent2'], width=2, dash='dash'),
            name=f'r={r:.3f}',
        ))
    fig_scatter.update_layout(
        **PLOTLY_LAYOUT, height=360,
        title=dict(text='Grid vs Finish Position', font=dict(size=14)),
        xaxis_title='Grid Position',
        yaxis_title='Finish Position',
    )

    career = d.groupby('year')['grid_delta'].mean().reset_index()
    fig_career = go.Figure()
    if len(career) > 0:
        fig_career.add_trace(go.Scatter(
            x=career['year'], y=career['grid_delta'],
            mode='lines+markers',
            line=dict(color=C['accent'], width=2),
            marker=dict(size=7, color=C['accent2']),
            fill='tozeroy',
            fillcolor='rgba(232,0,45,0.1)',
            hovertemplate='%{x}: %{y:+.2f} avg delta<extra></extra>',
        ))
        fig_career.add_hline(y=0, line_color=C['muted'], line_dash='dot')
    fig_career.update_layout(
        **PLOTLY_LAYOUT, height=320,
        title=dict(text='Avg Grid Delta by Season', font=dict(size=14)),
        xaxis_title='Season',
        yaxis_title='Avg Grid Delta',
    )

    return stats_cards, fig_scatter, fig_career

@app.callback(
    Output('compare-stats', 'children'),
    Output('compare-bar', 'figure'),
    Output('compare-delta', 'figure'),
    Input('compare-a', 'value'),
    Input('compare-b', 'value'),
)
def compare_drivers(id_a, id_b):
    da = df[df['driverId'] == id_a]
    db = df[df['driverId'] == id_b]

    name_a = da['driver_name'].iloc[0] if len(da) else 'Driver A'
    name_b = db['driver_name'].iloc[0] if len(db) else 'Driver B'

    def metrics(d):
        return {
            'races':      len(d),
            'avg_grid':   d['grid'].mean(),
            'avg_finish': d['position'].mean(),
            'avg_delta':  d['grid_delta'].mean(),
            'wins':       (d['position'] == 1).sum(),
            'poles':      (d['grid'] == 1).sum(),
        }

    ma, mb = metrics(da), metrics(db)

    stats_row = html.Div(className='stat-banner mini', children=[
        html.Div(className='stat-card mini', children=[
            html.P('Races', className='stat-label'),
            html.Div(className='cmp-values', children=[
                html.Span(str(ma['races']), className='cmp-val red'),
                html.Span('vs', className='cmp-vs'),
                html.Span(str(mb['races']), className='cmp-val blue'),
            ]),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Avg Grid', className='stat-label'),
            html.Div(className='cmp-values', children=[
                html.Span(f'{ma["avg_grid"]:.1f}', className='cmp-val red'),
                html.Span('vs', className='cmp-vs'),
                html.Span(f'{mb["avg_grid"]:.1f}', className='cmp-val blue'),
            ]),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Avg Delta', className='stat-label'),
            html.Div(className='cmp-values', children=[
                html.Span(f'{ma["avg_delta"]:+.2f}', className='cmp-val red'),
                html.Span('vs', className='cmp-vs'),
                html.Span(f'{mb["avg_delta"]:+.2f}', className='cmp-val blue'),
            ]),
        ]),
        html.Div(className='stat-card mini', children=[
            html.P('Wins', className='stat-label'),
            html.Div(className='cmp-values', children=[
                html.Span(str(ma['wins']), className='cmp-val red'),
                html.Span('vs', className='cmp-vs'),
                html.Span(str(mb['wins']), className='cmp-val blue'),
            ]),
        ]),
    ])

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name=name_a,
        x=['Avg Grid', 'Avg Finish', 'Avg Delta'],
        y=[ma['avg_grid'], ma['avg_finish'], ma['avg_delta']],
        marker_color=C['accent'],
        text=[f'{v:.2f}' for v in [ma['avg_grid'], ma['avg_finish'], ma['avg_delta']]],
        textposition='outside',
    ))
    fig_bar.add_trace(go.Bar(
        name=name_b,
        x=['Avg Grid', 'Avg Finish', 'Avg Delta'],
        y=[mb['avg_grid'], mb['avg_finish'], mb['avg_delta']],
        marker_color=C['blue'],
        text=[f'{v:.2f}' for v in [mb['avg_grid'], mb['avg_finish'], mb['avg_delta']]],
        textposition='outside',
    ))
    fig_bar.update_layout(
        **PLOTLY_LAYOUT, height=360,
        barmode='group',
        title=dict(text='Key Metrics Comparison', font=dict(size=14)),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    fig_delta = go.Figure()
    fig_delta.add_trace(go.Histogram(
        x=da['grid_delta'], name=name_a,
        nbinsx=20, marker_color=C['accent'], opacity=0.6,
    ))
    fig_delta.add_trace(go.Histogram(
        x=db['grid_delta'], name=name_b,
        nbinsx=20, marker_color=C['blue'], opacity=0.6,
    ))
    fig_delta.update_layout(
        **PLOTLY_LAYOUT, height=360,
        barmode='overlay',
        title=dict(text='Grid Delta Distribution', font=dict(size=14)),
        xaxis_title='Places Gained',
        yaxis_title='Races',
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )

    return stats_row, fig_bar, fig_delta

if __name__ == '__main__':
    app.run(debug=True, port=8050)