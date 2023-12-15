import dash
from dash import Input, Output, html, dcc
from dash import callback

dash.register_page(__name__, name='Dev: div data', order=6, is_menu=True, icon='fa-solid fa-cubes me-2')


def layout() -> html.Div:
    description = """
    * `div` 에 `data-*` 속성으로 데이터를 저장할 수 있다.
    * `div` 에 hidden data 초기값으로 `dummy data - A` 세팅했다.
    * `Change Hidden Data` 버튼을 누르면 hidden data 가 변경되면서, callback 도 잘 동작해 맨아래 `Hidden Data:` 출력값도 변경된다.
    * 참고: https://wefree.tistory.com/345
    """
    return html.Div(
        [
            html.H1("Div 에 데이터 저장하기 테스트"),
            dcc.Markdown(description),
            html.Hr(),
            html.Div(id="hidden-data-value", hidden=True, **{
                "data-value-1": "dummy data - A"
            }),
            html.Button("Change Hidden Data", id="data-change-button"),
            html.Div(id="hidden-data-show")
        ]
    )


@callback(
    Output('hidden-data-value', "data-value-1"),
    Input('data-change-button', 'n_clicks'),
    prevent_initial_call=True
)
def change_hidden_data(_) -> str:
    return "changed data - B"


@callback(
    Output("hidden-data-show", "children"),
    Input('hidden-data-value', "data-value-1")
)
def show_result(hidden_data) -> str:
    return f"Hidden Data: {hidden_data}"
