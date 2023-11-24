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
from dash import Input, Output, State, dcc, html, callback, ctx, dash_table
from loguru import logger
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
post_df: pd.DataFrame = pd.read_csv('data/post_df.csv', parse_dates=['date'])


def layout(code: str = '') -> html.Div:
    """code 값이 직접적으로 사용되지는 않지만, tistory 인증시 code 값이 전달되어 param 으로 필요함"""

    # post 단위 (daily)
    daily_fig = px.scatter(post_df, x='date', y='main_category', color='main_category',
                           hover_data=['title', 'post_url'],
                           title='날짜별 블로그 글')

    # monthly
    df = post_df.copy()
    df = duckdb.sql("""select *, strftime(date, '%Y-%m') as year_month from df""").df()
    # df["year_month"] = df["date"].dt.strftime('%Y-%m')

    monthly_df = df[['year_month', 'main_category']].value_counts().reset_index()
    monthly_fig = px.bar(monthly_df, x='year_month', y='count', color='main_category', title='월별 블로그 수')

    # data table
    table_df = duckdb.sql(
        """select date, main_category, title, concat('[', post_url, ']', '(', post_url, ')') post_url from post_df"""
    ).df()

    return html.Div(
        [
            dcc.Location(id='tistory_url', refresh=True),
            html.H1("wefree.tistory.com 통계"),
            dcc.Graph(id='monthly_fig', figure=monthly_fig),
            dcc.Graph(id='daily_fig', figure=daily_fig),

            # client 에서 전체 데이터를 받아 paging & sort .. ==> native
            # server 에서 특정 페이지에 해당하는 일부 데이터만 보내 줄려면 ==> custom + callback 구현
            dash_table.DataTable(
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
            ),
            dbc.Button("update statistics (admin only)", id="update_data", color="primary", n_clicks=0)
        ]
    )


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
        ) for post in res.json()["tistory"]["item"]["posts"]
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
        ) for category in res.json()["tistory"]["item"]["categories"]
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
        category = [c for c in categories if c.id == category_id][0]
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


@callback(
    Output('tistory_url', 'href'),
    Input('update_data', 'n_clicks'),
    State('tistory_url', 'href')
)
def redirect_to_auth(n_clicks, href) -> str:
    match ctx.triggered_id:
        case 'update_data':
            params = {
                "client_id": APP_ID,
                "redirect_uri": CALLBACK_URL,
                "response_type": "code"
            }

            url: str = "https://www.tistory.com/oauth/authorize?" + parse.urlencode(params, encoding='utf-8')
            return url

        # 브라우저 URL 로 직접 입력된 경우 triggered_id 값이 None 이다.
        case _:
            query_string = parse.urlparse(href).query
            path_string = parse.urlparse(href).path
            dict_result = parse.parse_qs(query_string)
            codes = dict_result.get("code", [])

            if codes and 'tistory' in path_string:
                code = codes[0]
                access_token = _get_access_token(code)
                logger.info(f"{access_token=}")
                total = get_total_count(access_token)
                logger.info(f"{total=}")

                all_posts: list[BlogPost] = get_all_posts(access_token, total)
                categories: list[BlogCategory] = get_categories(access_token)
                my_posts = make_my_posts(all_posts, categories)

                global post_df
                post_df = pd.DataFrame([my_post.model_dump() for my_post in my_posts])
                # post_df.to_csv('data/post_df.csv')

                return CALLBACK_URL
