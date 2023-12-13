import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash import State, callback
from dash import clientside_callback

dash.register_page(__name__, name='Javascript', order=3, is_menu=True, icon='fa-solid fa-code me-2')

description = html.Div([
    html.A("Javascript sortable library", href="https://github.com/SortableJS/Sortable", target="_blank"),
    html.Span(" 을 Dash 에서 사용해 본다."),
    html.Ul(
        [
            html.Li("아래 5개 항목은 drag & drop 으로 순서를 변경할 수 있다. 순서 변경 즉시 Sorted 값도 갱신된다."),
            html.Li([
                "상세한 개발 설명은 블로그 글을 참고 한다. ",
                html.A("https://wefree.tistory.com/335", href="https://wefree.tistory.com/335", target="_blank")
            ]),
        ]
    ),
    html.Hr()
])


def layout() -> html.Div:
    return html.Div(
        [
            html.H1('Javascript Library 를 Dash 에서 사용하기'),
            description,
            dcc.Store(id='state', storage_type='memory', data=["1:A", "2:B", "3:C", "4:D", "5:E"]),
            html.Button("Sync", id="hidden_sync_button", hidden=True),
            html.Div(id="display_result"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem("0:A", color="primary", id="0:A"),
                    dbc.ListGroupItem("1:B", color="secondary", id="1:B"),
                    dbc.ListGroupItem("2:C", color="success", id="2:C"),
                    dbc.ListGroupItem("3:D", color="danger", id="3:D"),
                    dbc.ListGroupItem("4:E", color="info", id="4:E"),
                ],
                id="items",
            )
        ]
    )


# 최초 한번만 호출되는 callback 으로 Sortable 설정한다.
clientside_callback(
    '''
    (value) => {
       Sortable.create(items, {
        animation: 150,
        group: "state",
        dataIdAttr: "id",
        store: {
          get: (sortable) => {
            let order = sessionStorage.getItem(sortable.options.group.name);
            return JSON.parse(order);
          },
          set: (sortable) => {
            let order = sortable.toArray();
            sessionStorage.setItem(sortable.options.group.name, JSON.stringify(order)); 
            document.getElementById("hidden_sync_button").click();
          }
        }
      }); 
    }
    ''',
    Output("hidden_sync_button", "style"),
    Input("hidden_sync_button", "title"),
)

# drag&drop 으로 변경이 발생시 sessionStorage 에 저장된 값을 dcc.Store(id=state) 에 저장
clientside_callback(
    '''
    (n_clicks) => {
       let json = sessionStorage.getItem("state");
       return JSON.parse(json);
    }
    ''',
    Output("state", "data"),
    Input("hidden_sync_button", "n_clicks"),
    prevent_initial_call=True
)


@callback(
    Output("display_result", "children"),
    Input("state", "modified_timestamp"),
    State("state", "data"),
)
def show_result(_, state_data):
    return 'Sorted: ' + ' -> '.join([str(x) for x in state_data])
