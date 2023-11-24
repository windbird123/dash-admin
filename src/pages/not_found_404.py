import dash
from dash import html

dash.register_page(__name__, is_menu=False)

layout: html.Div = html.Div(
    [
        html.H1("404: Not found", className="text-danger"),
        html.Hr(),
        html.P(f"The requested path was not recognized..."),
    ],
    className="p-3 bg-light rounded-3"
)
