from urllib import parse

import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, Dash, callback

import dash

import ids

dash.register_page(__name__, name='Messages', order=4, is_menu=True, icon='fas fa-envelope-open-text me-2')


def layout(input: str = '') -> html.Div:
    return html.Div(
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
                        html.P(id="output")
                    ]
                ),
            ],
            className="g-4"
        )
    )


@callback(
    Output("output", "children"),
    Input("click", "n_clicks"),
    State("input", "value")
)
def output_text(click, value):
    return value


@callback(
    Output(ids.URL, 'search', allow_duplicate=True),
    Input('click', 'n_clicks'),
    State("input", "value"),
    prevent_initial_call=True
)
def update_url_query_param(click, input_value):
    """input_value 가 None 이 될 수 있어서, 폼의 초기값으로 empty string 지정함"""
    return f"?input={parse.quote(input_value, encoding='utf-8')}"
