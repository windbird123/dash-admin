import math
import os
import time
from datetime import datetime
from urllib import parse

import dash
import dash_bootstrap_components as dbc
import duckdb
import pandas as pd
import plotly.express as px
import requests
from dash import Input, Output, dcc, html, callback, dash_table
from loguru import logger
from plotly.graph_objs import Figure
from pydantic import BaseModel

BLOG_NAME = os.getenv("BLOG_NAME")
APP_ID = os.getenv("APP_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
SERVICE_URL = os.getenv("SERVICE_URL")
CALLBACK_URL = os.getenv("CALLBACK_URL")


# BlogPost join BlogCategory
class MyPost(BaseModel):
    title: str
    post_url: str
    main_category: str
    sub_category: str
    date: datetime


class BlogPost(BaseModel):
    title: str
    post_url: str
    category_id: str
    date: datetime


class BlogCategory(BaseModel):
    id: str
    name: str
    parent_id: str
    label: str


dash.register_page(__name__, name='Tistory', order=2, is_menu=True, icon='fas fa-marker me-2')

# MyPost as rows
# global variable 의 변경은 모든 USER 의 UI 에 영향을 줌
post_df: pd.DataFrame = pd.read_csv('data/post_df.csv', parse_dates=['date'])


def layout(code: str = '') -> html.Div:
    """code 값이 직접적으로 사용되지는 않지만, tistory 인증시 code 값이 전달되어 param 으로 필요함"""

    # 콜백을 사용하지 않고 location 을 직접 업데이트해 리다이렉트하기 위함
    location = dcc.Location(id='location_tistory', refresh=True)
    global post_df

    if code:
        post_df = get_post_df(code)  # 인증 코드를 받았을 경우 global post_df 를 업데이트 함
        location.href = CALLBACK_URL  # /tistory 로 redirect (code param 제거를 위해)
        # post_df.to_csv('data/post_df.csv')

    return html.Div(
        [
            location,
            html.H1("wefree.tistory.com 통계"),
            dbc.Button("update statistics (admin only)", id="update_data", color="primary", n_clicks=0),
            dcc.Graph(id='monthly_fig', figure=build_monthly_fig(post_df)),
            dcc.Graph(id='daily_fig', figure=build_daily_fig(post_df)),
            build_table(post_df)
        ]
    )


@callback(
    Output('location_tistory', 'href', allow_duplicate=True),
    Input('update_data', 'n_clicks'),
    prevent_initial_call=True
)
def redirect_to_auth(n_clicks) -> str:
    params = {
        "client_id": APP_ID,
        "redirect_uri": CALLBACK_URL,
        "response_type": "code"
    }

    url: str = "https://www.tistory.com/oauth/authorize?" + parse.urlencode(params, encoding='utf-8')
    return url


def build_daily_fig(df: pd.DataFrame) -> Figure:
    return px.scatter(
        df,
        x='date',
        y='main_category',
        color='main_category',
        hover_data=['title', 'post_url'],
        title='날짜별 블로그 글'
    )


def build_monthly_fig(df: pd.DataFrame) -> Figure:
    df = post_df.copy()
    df = duckdb.sql("""select *, strftime(date, '%Y-%m') as year_month from df""").df()
    # df["year_month"] = df["date"].dt.strftime('%Y-%m')

    monthly_df = df[['year_month', 'main_category']].value_counts().reset_index()
    return px.bar(
        monthly_df,
        x='year_month',
        y='count',
        color='main_category',
        title='월별 블로그 수'
    )


# client 에서 전체 데이터를 받아 paging & sort .. ==> native
# server 에서 특정 페이지에 해당하는 일부 데이터만 보내 줄려면 ==> custom + callback 구현
def build_table(df: pd.DataFrame) -> dash_table.DataTable:
    table_df = duckdb.sql(
        """select date, main_category, title, concat('[', post_url, ']', '(', post_url, ')') post_url from df"""
    ).df()

    return dash_table.DataTable(
        id='table-paging-and-sorting',
        page_current=0,
        page_size=10,
        page_action='native',
        filter_action='native',
        sort_action='native',
        sort_mode='single',
        sort_by=[],
        export_format='csv',
        data=table_df.to_dict('records'),
        columns=[
            {"name": "날짜", "id": "date"},
            {"name": "분류", "id": "main_category"},
            {"name": "URL", "id": "post_url", "type": "text", "presentation": "markdown"},
            {"name": "제목", "id": "title"},
        ],
        style_cell={'textAlign': 'left'},
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(150, 150, 150)',
            'color': 'black',
            'fontWeight': 'bold'
        }
    )


def get_post_df(code) -> pd.DataFrame:
    """code 값을 이용해 전체 블로그 데이터를 읽어 옴"""

    access_token = _get_access_token(code)
    logger.info(f"{access_token=}")
    total = get_total_count(access_token)
    logger.info(f"{total=}")

    # category = '0' 은 공지글로 BlogCategory 에 필요한 모든 속성을 가져올 수 없어 처리에서 제외한다.
    all_posts: list[BlogPost] = get_all_posts(access_token, total)
    all_posts: list[BlogPost] = [post for post in all_posts if post.category_id != '0']

    categories: list[BlogCategory] = get_categories(access_token)  # category_id = '0' 에 대한 정보는 없다.
    my_posts = make_my_posts(all_posts, categories)

    return pd.DataFrame([my_post.model_dump() for my_post in my_posts])


def _get_access_token(code: str) -> str:
    res = requests.get(
        "https://www.tistory.com/oauth/access_token",
        params={
            "client_id": APP_ID,
            "client_secret": SECRET_KEY,
            "redirect_uri": CALLBACK_URL,
            "code": code,
            "grant_type": "authorization_code"
        })
    # response 예)
    #   access_token=62757643d27fd3b34af15e13c817c94b_005a1761170a5c4969dc7103656a8098
    # len("access_token=") = 13
    return res.text[13:]


def get_posts(access_token: str, page: int) -> list[BlogPost]:
    res = requests.get(
        "https://www.tistory.com/apis/post/list",
        params={
            "access_token": access_token,
            "output": "json",
            "blogName": BLOG_NAME,
            "page": page
        })

    return [
        BlogPost(
            title=post["title"],
            post_url=post["postUrl"],
            category_id=post["categoryId"],
            date=post["date"]
        )
        for post in res.json()["tistory"]["item"]["posts"]
    ]


def get_all_posts(access_token: str, total: int) -> list[BlogPost]:
    full_list = []
    start_page = 1
    end_page = math.ceil(total / 10)

    for page in range(start_page, end_page + 1):
        posts = get_posts(access_token, page)
        full_list += posts
        time.sleep(0.1)

    return full_list


def get_categories(access_token: str) -> list[BlogCategory]:
    res = requests.get(
        "https://www.tistory.com/apis/category/list",
        params={
            "access_token": access_token,
            "output": "json",
            "blogName": BLOG_NAME
        }
    )

    return [
        BlogCategory(
            id=category["id"],
            name=category["name"],
            parent_id=category["parent"],
            label=category["label"]
        )
        for category in res.json()["tistory"]["item"]["categories"]
    ]


def get_total_count(access_token: str) -> int:
    res = requests.get(
        "https://www.tistory.com/apis/blog/info",
        params={
            "access_token": access_token,
            "output": "json"
        })

    post_count = res.json()["tistory"]["item"]["blogs"][0]["statistics"]["post"]
    return int(post_count)


def make_my_posts(posts: list[BlogPost], categories: list[BlogCategory]) -> list[MyPost]:
    def get_main_sub_category(category_id: str) -> (str, str):
        cc = [c for c in categories if c.id == category_id]
        category = cc[0]

        if category.parent_id:
            parent_category = [c for c in categories if c.id == category.parent_id][0]
            return parent_category.name, category.name
        else:
            return category.name, ''

    my_posts: list[MyPost] = []
    for post in posts:
        main_category, sub_category = get_main_sub_category(post.category_id)
        my_post = MyPost(**post.model_dump(), main_category=main_category, sub_category=sub_category)
        my_posts.append(my_post)

    return my_posts
