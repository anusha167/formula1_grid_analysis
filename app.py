import html

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, htrml, Input, Output # this is for web framework
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
                'Which drivers consistently outperform their starting grid position, and which ones underperform? This dashboard explores the relationship between starting grid position and finishing position in Formula 1.'
                className='header-tagline'
            ),
        ])
    ]),
])

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