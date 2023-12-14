import dash
from dash import Input, Output, html
from dash import callback

dash.register_page(__name__, name='Div Data', order=6, is_menu=True, icon='fa-solid fa-cubes me-2')


def layout() -> html.Div:
    return html.Div(
        [
            html.H1("Div 에 데이터 저장하기"),
            html.Ul(
                [
                    html.Li(html.A("설명 보기", href='https://wefree.tistory.com/345', target='_blank')),
                ]
            ),
            html.Div(id="hidden-data-value", hidden=True, **{
                "data-value-1": "dummy data - AAAA"
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
    return "changed data - BBBB"


@callback(
    Output("hidden-data-show", "children"),
    Input('hidden-data-value', "data-value-1")
)
def show_result(hidden_data) -> str:
    print(f"show result called: {hidden_data}")
    return hidden_data
