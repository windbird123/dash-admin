from urllib import parse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback

dash.register_page(__name__, name='Messages', order=4, is_menu=True, icon='fas fa-envelope-open-text me-2')


def layout(input: str = '') -> html.Div:
    return html.Div([
        dcc.Location(id='location', refresh=False),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="input", value=input, placeholder="Type something...", type="text"),
                                dbc.Button("Primary", id="click", color="primary", n_clicks=0),
                            ]),
                    ],
                    width=4
                ),
                dbc.Col(
                    [
                        html.P(children=input)
                    ]
                ),
            ],
            className="g-4"
        )
    ])


@callback(
    Output('location', 'search'),
    Input('click', 'n_clicks'),
    State("input", "value"),
    prevent_initial_call=True
)
def update_url_query_param(click, input_value):
    """input_value 가 None 이 될 수 있어서, 폼의 초기값으로 empty string 지정함"""
    return f"?input={parse.quote(input_value, encoding='utf-8')}"
