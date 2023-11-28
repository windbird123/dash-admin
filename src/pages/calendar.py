from urllib import parse

import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, name='Calendar', order=3, is_menu=True, icon='fas fa-calendar-alt me-2')


def layout(city: str = 'Montreal') -> html.Div:
    return html.Div([
        dcc.Location(id='location_calendar', refresh=True),
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
        html.Div(children=f"You selected: {city}"),
    ])


@callback(
    Output('location_calendar', 'search'),
    Input('analytics-input', 'value')
)
def update_url_query_param(input_value):
    return f"?city={parse.quote(input_value, encoding='utf-8')}"
