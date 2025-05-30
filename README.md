## 개요
plotly dash 를 활용해 admin page 를 개발해 본다.
상세한 내용은 https://wefree.tistory.com/316 참고한다.

## 데모 페이지
https://wefree-tistory.fly.dev/

## 실행 환경 만들기
* python version: `3.10.x`
 
#### Local (Dev)
* `.env_dev` 파일을 `.env` 이름으로 복사
* `.env` 파일을 열어 본인 `tistory` 의 `APP_ID`,`SECRET_KEY` 등의 정보를 넣는다.
#### Prod
* `.env_prod` 파일에 필요한 정보를 수정한다. (`APP_ID`, `SECRET_KEY` 는 기입하지 않는다) 
* `APP_ID`, `SECRET_KEY` 등의 정보는 배포 시스템의 환경 변수로 등록한다. 예) https://fly.io/docs/js/the-basics/secrets/ 

## sidebar 에 메뉴 추가 방법
* `pages` 하위 디렉토리에 파일 추가
* `dash.register_page()` 에 아래 항목 지정
  * name (str): 메뉴 이름으로 사용됨
  * order (int): 노출 순서 (0 이 가장 높음)
  * is_menu (bool): sidebar 메뉴에 노출할지 여부
  * icon (str): sidebar 메뉴 노출시 사용할 아이콘 (참고: https://fontawesome.com/icons)
    * free: https://fontawesome.com/search?o=r&m=free


## fly.io 배포
* [flyctl](https://fly.io/docs/hands-on/install-flyctl/) 설치 후 
  ```bash
  fly auth login

  # 배포할 소스 디렉토리에서
  fly launch
  fly deploy
  
  # 모니터링
  fly status
  fly apps list
  fly apps restart
  
  # console terminal
  flyctl ssh console
  
  # secrets
  fly -a my-app secrets set DATABASE_URL=postgres://example.com/mydb
  ```

* 배포후 https://fly.io/dashboard 에서 app 확인이 가능하다.
* 배포시 에러가 발생 한다면 모니터링 페이지에서 로그 확인이 가능하다. 예) https://fly.io/apps/wefree-tistory/monitoring
* 한번 배포가 되면 이후에는 `fly launch` 없이 바로 `fly deploy` 로 배포 가능하다. 
