from urllib import parse

import dash
from dash import html, dcc, callback, Input, Output

import ids

dash.register_page(__name__, name='Calendar', order=3, is_menu=True, icon='fas fa-calendar-alt me-2')


def layout(city: str = 'Montreal') -> html.Div:
    return html.Div([
        html.H1('This is our Analytics page'),
        html.Div([
            "Select a city: ",
            dcc.RadioItems(
                options=['New York City', 'Montreal', 'San Francisco'],
                value=city,
                id='analytics-input'
            )
        ]),
        html.Br(),
        html.Div(id='analytics-output'),
    ])


@callback(
    Output('analytics-output', 'children'),
    Input('analytics-input', 'value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'


@callback(
    Output(ids.URL, 'search', allow_duplicate=True),
    Input('analytics-input', 'value'),
    prevent_initial_call=True
)
def update_url_query_param(input_value):
    return f"?city={parse.quote(input_value, encoding='utf-8')}"
