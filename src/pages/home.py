from pathlib import Path

import math
import os
import time
from datetime import datetime
from urllib import parse
import plotly.express as px

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, dcc, html, callback, ctx
from pydantic import BaseModel
import pandas as pd

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, Dash

dash.register_page(__name__, path='/', name='Home', order=0, is_menu=True, icon='fa-solid fa-home me-2')


def layout() -> html.Div:
    return html.Div(
        [
            html.H1("Plotly dash PoC"),
            html.Ul(
                [
                    html.Li(html.A("어떻게 개발했나? 설명 보기", href='https://wefree.tistory.com/316', target='_blank')),
                    html.Li(html.A("소스 코드 보기", href='https://github.com/windbird123/dash-admin', target='_blank')),
                ]
            )

        ]
    )
