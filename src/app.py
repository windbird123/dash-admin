import os

import dash
import dash_bootstrap_components as dbc
from dash import html, Dash
from dotenv import load_dotenv
from loguru import logger


def create_app() -> Dash:
    APP_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    ENV_FILE = os.getenv("ENV_FILE", ".env")
    load_dotenv(ENV_FILE)

    # logging.basicConfig(level=logging.INFO, format='%(asctime)s\t%(levelname)s\t%(message)s')

    # logger.remove()
    # logger.add(sys.stderr, format="{time}\t{level}\t{message}")

    app: Dash = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
        use_pages=True
    )

    sidebar = html.Div(
        [
            html.Div(
                [
                    # width: 3rem ensures the logo is the exact width of the
                    # collapsed sidebar (accounting for padding)
                    html.Img(src=APP_LOGO, style={"width": "3rem"}),
                    html.H2("Sidebar"),
                ],
                className="sidebar-header",
            ),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.I(className=page['icon']),
                            html.Span(page['name'])
                        ],
                        href=page['path'],
                        active='exact'
                    ) for page in dash.page_registry.values() if page['is_menu']
                ],
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar",
    )

    content = html.Div(
        dbc.Spinner(dash.page_container, color='success', size='md'),
        className="content"
    )

    app.layout = html.Div([
        sidebar,
        content
    ])

    logger.info("App was created ..")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True)
else:
    app = create_app()
    server = app.server  # for gunicorn
