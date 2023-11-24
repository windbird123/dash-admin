from enum import Enum, auto
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash import callback, ctx, ALL
from pydantic import BaseModel

dash.register_page(__name__, name='Resume', order=1, is_menu=True, icon='fas fa-user me-2')


class Tech(Enum):
    spark = auto()
    spark_streaming = auto()
    hadoop_mapreduce = auto()
    flink = auto()
    kafka = auto()
    rabbitmq = auto()
    elasticsearch = auto()
    hbase = auto()
    hive = auto()
    airflow = auto()
    azkaban = auto()
    kubernetes = auto()
    playframework = auto()
    fastapi = auto()
    jersey = auto()
    graphQL = auto()
    avro_rpc = auto()
    nginx = auto()
    mysql = auto()
    github_actions = auto()
    ansible = auto()
    chrome_extension = auto()
    jni = auto()
    vaadin = auto()
    scala = auto()
    scalajs = auto()
    python = auto()
    java = auto()
    c = auto()
    apache_module = auto()


class Project(BaseModel):
    item_id: str
    title: str
    tech_stacks: list[Tech]
    path: str


PROJECTS = [
    Project(
        item_id='project_dna',
        title='네이버 검색 품질 온라인 A/B 테스트, Side by Side 테스트',
        tech_stacks=[
            Tech.kubernetes, Tech.spark, Tech.playframework, Tech.scala, Tech.scalajs, Tech.airflow, Tech.python,
            Tech.fastapi, Tech.graphQL, Tech.github_actions, Tech.chrome_extension, Tech.ansible, Tech.mysql, Tech.hive
        ],
        path='data/resume/dna.md'
    ),
    Project(
        item_id='project_rising',
        title='네이버 실시간 급상승 검색어 API 개발',
        tech_stacks=[Tech.spark, Tech.playframework, Tech.flink, Tech.elasticsearch, Tech.scala],
        path='data/resume/rising.md'
    ),
    Project(
        item_id='project_argos',
        title='네이버 중요 질의에 대한 검색 품질 모니터링 시스템 개발',
        tech_stacks=[Tech.spark, Tech.playframework, Tech.rabbitmq, Tech.hbase, Tech.elasticsearch, Tech.scala,
                     Tech.ansible],
        path='data/resume/argos.md'
    ),
    Project(
        item_id='project_image_search',
        title='네이버 이미지 검색',
        tech_stacks=[Tech.spark, Tech.jersey, Tech.elasticsearch, Tech.scala, Tech.kafka, Tech.jni, Tech.azkaban,
                     Tech.vaadin, Tech.ansible],
        path='data/resume/image_search.md'
    ),
    Project(
        item_id='project_biz_advisor',
        title='Naver Biz Advisor 개발',
        tech_stacks=[Tech.spark, Tech.elasticsearch, Tech.scala, Tech.azkaban],
        path='data/resume/biz_advisor.md'
    ),
    Project(
        item_id='project_clova',
        title='클로바 음성 인식 전사 시스템 개발/운영',
        tech_stacks=[Tech.jersey, Tech.scala, Tech.nginx, Tech.spark, Tech.spark_streaming, Tech.hbase, Tech.kafka,
                     Tech.hive],
        path='data/resume/clova.md'
    ),
    Project(
        item_id='project_image_api',
        title='이미지 분석 API 개발',
        tech_stacks=[Tech.jersey, Tech.jni, Tech.scala, Tech.nginx],
        path='data/resume/image_api.md'
    ),
    Project(
        item_id='project_sunny',
        title='웹 문서 수집 시스템 개발',
        tech_stacks=[Tech.java, Tech.hadoop_mapreduce, Tech.avro_rpc, Tech.chrome_extension],
        path='data/resume/sunny.md'
    ),
    Project(
        item_id='project_early_image',
        title='초기 네이버 이미지 검색 정제 개발',
        tech_stacks=[Tech.java, Tech.hadoop_mapreduce],
        path='data/resume/early_image.md'
    ),
    Project(
        item_id='project_nexus',
        title='네이버 검색엔진을 이용한 색인, 검색서비스 운영',
        tech_stacks=[Tech.c, Tech.apache_module],
        path='data/resume/nexus.md'
    )
]


def layout() -> html.Div:
    def create_accordion_item(project: Project) -> dbc.AccordionItem:
        body = Path(project.path).read_text(encoding='utf-8')
        return dbc.AccordionItem(
            [
                dcc.Markdown(body),
                html.Div(
                    [
                        html.H4("Tech Stack"),
                        html.Div(", ".join([tech.name for tech in project.tech_stacks]))
                    ]
                )
            ],
            title=project.title,
            item_id=project.item_id
        )

    def create_tech_stacks(tech: Tech, projects: list[Project]) -> html.Div:
        return html.Div(
            [
                html.H4(tech.name),
                html.Ul(
                    [
                        html.Li(
                            html.A(project.title, href='/resume#project',
                                   id={"type": "tech_stack", "item_id": project.item_id})
                        )
                        for project in projects
                    ]
                )
            ]
        )

    def find_projects_using(tech: Tech) -> list[Project]:
        return [project for project in PROJECTS if tech in project.tech_stacks]

    return html.Div(
        [
            html.H1("프로젝트", id='project'),
            dbc.Accordion(
                [
                    create_accordion_item(project) for project in PROJECTS
                ],
                id='project_list'
            ),

            html.H1("기술스택", className='mt-5'),

            html.Div(
                [
                    create_tech_stacks(tech, find_projects_using(tech)) for tech in Tech
                ]
            )
        ]
    )


# ALL 대신 MATCH 를 쓸려면 Input 뿐만 아니라 Output 에도 MATCH 가 들어가야 함
@callback(
    Output('project_list', 'active_item'),
    Input({"type": "tech_stack", "item_id": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def goto_project(n_clicks) -> str:
    if n_clicks:
        return ctx.triggered_id["item_id"]
