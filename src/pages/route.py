from urllib import parse

import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, name='Dev: route', order=4, is_menu=True, icon='fa-solid fa-share-nodes me-2')


def layout(city: str = 'Montreal') -> html.Div:
    description = """
    * 선택한 도시 이름이 URL query parameter `city` 로 들어간다.
    * URL query parameter 를 분석해 선택한 도시를 `checked` 로 보여준다.
    * 참고: https://wefree.tistory.com/323
    """

    return html.Div([
        # refresh 값으로 callback-nav 를 사용하면 (callback 에 의해 dcc.Location 값이 변할 때)
        # 전체화면 갱신 없이 브라우저 URL 이 변경되면서, 필요한 화면만 갱신된다!
        dcc.Location(id='location_calendar', refresh='callback-nav'),

        html.H1('URL Route 테스트'),
        dcc.Markdown(description),
        html.Hr(),
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
