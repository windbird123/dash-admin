from urllib import parse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback

dash.register_page(__name__, name='Dev: grid layout', order=5, is_menu=True, icon='fa-solid fa-table-cells-large me-2')


def layout(input: str = '') -> html.Div:
    description = """
    * `dbc.Row()`, `dbc.Col()` 을 이용해 화면을 2개 컬럼으로 분할했다.
    * `보기` 버튼을 누르면, 입력한 내용이 오른쪽 컬럼에 출력된다.
    """

    return html.Div([
        html.H1('Grid Layout 테스트'),
        dcc.Markdown(description),

        # refresh 값으로 callback-nav 를 사용하면 (callback 에 의해 dcc.Location 값이 변할 때)
        # 전체화면 갱신 없이 브라우저 URL 이 변경되면서, 필요한 화면만 갱신된다!
        html.Hr(),
        dcc.Location(id='location', refresh='callback-nav'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="input", value=input, placeholder="Type something...", type="text"),
                                dbc.Button("보기", id="click", color="primary", n_clicks=0),
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
