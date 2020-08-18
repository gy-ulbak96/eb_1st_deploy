# eb_1st_deploy
eb aws deploy
# 200519 멋사 5주차 세션

## Django 프로젝트 배포하기 : AWS

### AWS 시작하기

Amazon Web Servies : 아마존 닷컴이 제공하는 클라우드 컴퓨팅 서비스

우선 AWS에 다 가입은 하셨죠? 본격적으로 배포를 하기 전에 해야할 일이 있습니다. 바로 IAM으로 새 유저를 만드는 일이에요.

##### IAM 이란?

AWS 리소스에 대한 액세스를 안전하게 제어할 수 있는 웹서비스입니다. 

우리가 AWS에 가입한 계정은 루트 계정이며 모든 권한을 가지고 있기 때문에 루트 계정에  보안이 뚫리게 되면 공격자가 모든 권한을 가질 수 있는 문제가 있어요. 그래서 제한된 권한을 가진 유저를 생성해서 해당 유저로 서버를 관리함으로써 보안이 뚫리더라도 모든 권한을 갖는 것은 막을 수 있습니다.

그럼 IAM에서 유저를 생성해 볼까요? 

우선 서비스에 IAM을 검색해서 들어갑시다. 그 다음에 왼쪽 탭에서 액세스 관리 > 사용자로 들어가 주세요.

![image](https://user-images.githubusercontent.com/42667951/82133018-71def000-9821-11ea-81a2-d142ba6ecdde.png)

여기에서 사용자 추가를 눌러줍니다.

사용자 이름을 입력하고, 액세스 유형은 저희는 CLI를 사용할 거기 때문에 프로그래밍 방식 액세스를 선택합니다.

다음은 이 유저에게 권한을 부여해 줘야하는데요, 기존 정책을 직접 연결해 줍시다.

![image](https://user-images.githubusercontent.com/42667951/82225876-b58c4380-9960-11ea-8663-e999622494ed.png)

정책으로는 우선 `Amazon EC2FullAccess` `AmazonS3FullAccess`  `AWSElasticBeanstalkFullAccess`를 추가해 줍니다.  이 권한 설정이 가끔 좀 귀찮게 오류를 낼 때가 많아서 일단 3개를 다 정책으로 추가했어요. 각각 요소가 무슨 역할인지는 하면서 설명해 드릴게요.

설정을 끝내고 계속 '다음' 버튼을 누르다 보면 이제 사용자 생성을 성공했다는 화면과 함께 액세스 키 ID, 비밀 액세스키가 나옵니다. 이 때 주의 해야할 건, 이 키ID와 비밀 액세스키가 담긴 .csv는 지금이 다운로드 할 수 있는 마지막 기회라는 거에요.

++ 나중에 깃허브에 프로젝트 올릴 때 이 csv파일이 같이 올라가지 않게 주의하세요. 안전한 장소에 따로 저장을 해두는게 좋습니다.

이제 IAM 유저도 생성을 했으니 배포를 시작해 보아요.



### 배포 방법 1

첫번 째 배포 방법입니다. 바로 nginx, uwsgi를 통해서 아마존 EC2 인스턴스를 이용해 배포하는 방법이에요.

일단 처음 보는 개념들이 있을 테니 이 개념에 대해서 먼저 설명을 하고 지나갈게요.

#### 1. 웹서버

![image](https://user-images.githubusercontent.com/42667951/82134070-680fb980-982e-11ea-8d45-850d53410712.png)

우선 웹서버는 HTTP를 통해 웹 브라우저에서 요청하는 HTML문서나 오브젝트를 전송하는 서비스 프로그램을 의미합니다.  웹 사용자가 호스트 파일에 접근하는 것을 관리하는 거죠.

 위 그림을 보면 브라우저(클라이언트)가 웹 서버에서 불려진 파일을 필요로 할 때, 브라우저는 HTTP프로토콜을 통해 파일을 요청하게 됩니다. 요청이 웹서버에 도달하면 HTTP 서버는 요청된 문서를 HTTP를 이용하여 그대로 보내주게 됩니다. 

-> 웹 서버는 기본적으로 '정적' 형태입니다.  그렇기 때문에 단순한 파일에서는 빠르고 안정적입니다.

#### *Nginx

대표적인 웹서버로써 대량의 클라이언트, 트래픽이 많은 웹사이트의 확장성을 위해 설계한 비동기 이벤티 기반 구조의 웹서버 입니다. 

event기반으로 동작하기 때문에 가볍게 동시 연결을 쉽게 처리할 수 있어 많이 사용합니다.



#### 2. WSGI 서버 (Middleware)

'정적'인 웹서버를 동적으로 기능하기 위해 필요한 인터페이스입니다. 

-> 동적 : DB와 연결되어 데이터를 주고 받거나 프로그램으로 데이터 조작이 필요한 경우

또한 Python에서 웹 어플리케이션이 웹 서버와 통신하기 위한 인터페이스입니다. 웹서버(Nginx)는 python을 모르기 때문에 WSGI서버에서 HTTP요청을 python으로, Django로 부터 받은 응답을 Nginx가 알 수 있도록 변환을 하는 역할을 하게되죠. 개발 할 때 연결 형태는 아래와 같아요.

**사용자 요청 <-> 웹서버 <-> WSGI 서버 <-> WSGI를 지원하는 웹 어플리케이션(Django, flast etc..)**



이제 배포를 했을 때 전체 아키텍쳐의 흐름입니다.

![image](https://user-images.githubusercontent.com/42667951/82133716-40b6ed80-982a-11ea-9d89-b3c8a43bc170.png)

1) 웹 클라이언트가 웹 서버로 요청  전송(HTTP 프로토콜)

2) 이 때 정적파일은 Nginx 웹 서버에서 바로 처리가 가능합니다.

3) 웹 서버가 처리하지 못한 정적 파일 외의 동적파일을 처리하기 위해 요청을 웹서버 -> 웹 어플리케이션 서버로 위임합니다. 

4) HTTP를 웹 어플리케이션이 이해할 수 있도록 HTTP프로토콜의 메시지를 Python call로 변환합니다. 

5) Django 프레임 워크는 사용자의 Python 어플리케이션 코드를 실행합니다.

6) DB(ex. PostgreSQL)에서 데이터를 읽기 위해 ORM을 사용합니다.



이제 간단하게 전체 배포 순서를 알아볼까요?

1. Amazon에서 IAM 계정 생성

2. Amazon EC2 인스턴스 생성 (환경 : Ubuntu , 프리티어 사용 *) 후 접속

3. EC2 서버 환경, Python 환경 ,Django 환경설정

4. 로컬 장고에 HOST 추가 + 기타 잡다한 설정...

5. EC2 서버에 uWSGI설치

6. EC2 서버에 Nginx설치

7. uWSGI를 Nginx와 통신하도록 설정 + 기타 잡다한 설정...

8. Static 파일 S3에 배포 (by collectstatic 명령어, Nginx 설정, S3 다루기)

9. DB 따로 관리 해야하므로 RDS 설정

10. 마지막 최강자 이 모든걸 Docker위에서 하는 연습

    

하하하하하핳하하하하하핳하하하하하 원래 이번주 세션 목표는 이거였답니다.  하지만 과제에 치이고 에러에 치여 안타깝지만.. 이건 저의 다음 목표가 되었어요. 

도커를 너무 다루고 싶다! 내가 간지나게 AWS에서 하나하나 설정해서 배포하고 싶다! 하는 분들은 저와 함께 합시다. (파티원 모집 중)



### 배포 방법 2. Elastic Beanstalk

위에 방법은 지금 설명만으로도 엄청 복잡하죠? 

물론 한번쯤은 해봐야 하는 과정이지만 일단 우리는 배포 입문자이니까 Elastic Beanstalk을 이용해서 쉬운 배포를 먼저 실습해볼거에요. 

**Elastic Beanstalk이 뭔데용?**

![image](https://user-images.githubusercontent.com/42667951/82143187-f0b54680-987c-11ea-8bc9-98bc50be4e90.png)

Elastic Beanstalk은 지금까지 봤던 배포를 위한 저 복잡한 환경설정과 무지막지한 시간투자에서 벗어날 수 있는 서비스 입니다. Java, .NET, PHP, Node.js, Python, Ruby, Go, Docker를 사용해서 웹 애플리케이션을 간편하게 배포하고 조정할 수 있어요.

왜 배포가 간단하냐? Elastic Beanstalk에서는 간단하게 deploy명령어 하나로 자동으로 처리해주는 작업들이 있어요.

- amazon EC2 배포 환경 내에서 자동 설정(python, resion ...)
- EC2, RDS, S3 등의 자동 연결
- Auto Scailing으로 필요에 따라 인스턴스를 추가/제거
- 사용자 지정 : 리소스 선택 및 제어의 자유로움
- CloudWhatch 모니터링 / 관리 및 업데이트 등등



그러면 이제 실제 배포를 해보면서 왜 배포가 간단한지에 대해서 알아봅시다.

#### 1. 기본 환경설정

Elastic Beanstalk에서는 파일들의 위치, 가상환경 여부가 아주아주 중요해요!

우선 로컬에서 Elastic Beanstalk를 사용할 수 있도록 Awsebcli를 설치해 줄게요. 자료에서는 가상환경을 실행시키라 하는데, 아니에요...가상환경을 실행시키지 말아요..  개인차이 일 수 있지만 저는 이거 때문에 오류 엄청 났었습니다..그 이유는 뒤에서 설명드릴께요.

개인차이겠지만 저는 pip3로 명시해야 정상 작동이 되더라구요.

```bash
$ pip3 install awsebcli --upgrade --user 
```

이게 제대로 설치되었나 확인해보기 위해서 명령어를 쳐봅시다.

```bash
$ eb --version
```

![image](https://user-images.githubusercontent.com/42667951/82209587-74883500-9948-11ea-8a0b-10147397be43.png)

이렇게 뜨면 성공! 

여기에서 `eb command not found`오류가 나는 분들이 있을거에요. 간단한 환경 설정을 해줘야 합니다.

[Linux EB CLI 설치](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/eb-cli3-install-linux.html)

[Mac ox EB CLI 설치](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/eb-cli3-install-osx.html)

[Window EB CLI 설치](https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/eb-cli3-install-windows.html)



#### 2. 장고 프로젝트 만들기

다음은 그동안 우리 했던 것처럼 가상환경을 만들어서 장고 프로젝트를 만들어 봅시다.

여기서 주의할점...반드시 설치할 때 Django==2.1.1 버전으로 설치해야 합니다. 저는 이것때문에도 오류가 엄청났었어요..

![image](https://user-images.githubusercontent.com/42667951/82209992-34758200-9949-11ea-8def-69a20a714be6.png)

AWS공식 문서를 보면 다음과 같이 설명이 되어 있습니다. 이 때 버전을 명시를 하지 않고 배포를 하면 502error가 뜨게 됩니다. 

```bash
$ python -m venv myvenv
$ source myvenv/Scripts/activate
$ python -m pip install --upgrade pip
$ pip install django==2.1.1
$ django-admin startproject ebdeploy
$ cd ebdeploy
.... 여기는 자기가 원하는 프로젝트 잘 작성!
$ python manage.py migrate
```

##### .gitingore

이제 manage.py  가 있는 경로에 .gitignore을 만들어줄게요. .gitignore을 만들 때는 `gitignore.io`에 가서 만들면 쉽게 만들 수 있는거 다들 아시죠?

```.gitignore
# Created by https://www.gitignore.io/api/django
# Edit at https://www.gitignore.io/?templates=django

### Django ###
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
media

# Elastic Beanstalk Files
.elasticbeanstalk/*
!.elasticbeanstalk/*.cfg.yml
!.elasticbeanstalk/*.global.yml
```

.elasticbeanstalk은 eb명령어를 이용해서 배포하면 생기는 폴더에요. 필요없는건 업로드하지 말고 필요한 것만 업로드하도록 .gitignore을 작성해줍시다.

##### requirements.py

이번엔 manage.py가 있는 경로에 requirements.txt 파일을 만들어줄거에요. 

> requirements.txt란? 
>
> 패키지 목록이 나열되어 있는 텍스트 파일이에요. 우리는 설치할 때 pip을 사용하기 때문에 pip으로 설치한 패키지 목록들이 나열되는 파일입니다. 

Elastic Beanstalk에서는 이 requirements.txt를 통해 애플리케이션이 의존하는 파이썬 패키지들을 지정하게 됩니다. 그래서 스펠링이 틀려서는 안됩니다!

```bash
$ pip freeze > requirements.txt
```

이 명령어를 치면 requirements.txt가 생성되면서 pip으로 설치된 패키지들이 입력이 되는걸 확인할 수 있습니다.



이 부분을 잘못 작업했을 때 발생할 수 있는 에러 두가지가 있어요.

1. **requirements.txt 내용을 채우지 않고 배포 : 500 error**

   Elastic Beanstalk이 requirements.txt 내용을 채우지 않으면 패키지를 인식하지 못했습니다. - 개인적인 차이 일 수 있지만 pip freeze로 내용을 채우는 것을 권장합니다.

2. **가상환경이 켜져 있는 상태에서 `pip install awsebcli --upgrade --user` 명령어를 친 후 `pip freeze`를 한 경우 : 500 error**

   이부분이 가장 당황스러운 에러였습니다. Window환경 같은 경우 EB의 EC2환경, 즉 리눅스 환경과 충돌하는 환경이 많아요. Window환경에서 pip install awsebcli를 할 경우 pywin32나 pypiwin32 같은 window환경에서 python을 사용할 수 있게끔 하는 패키지도 함께 설치 됩니다. 이걸 그대로 배포할 경우 리눅스 환경에서 충돌이 생기게 되어서 에러가 생기게 되더라구요. 그렇기 때문에 가상환경으로 배포할 패키지를 분리하는 것이 중요합니다.

   

##### .ebextensions

그 다음엔 manage.py가 있는 경로에 .ebextensions폴더를 만들어 줄거에요. 그 안에 django.config 파일을 만들어줍니다.

```.config
option_settings:
    aws:elasticbeanstalk:container:python:
        WSGIPath: ebdeploy/wsgi.py
```

django.config 안에 채워줄 내용입니다. WSGIPath는 본인의 wsgi.py가 있는 경로를 적어주면 돼요.  아까 위에서 wsgi는 Python에서 웹 어플리케이션이 웹 서버와 통신하기 위한 인터페이스라고 설명 드렸죠? EB는 이 파일을 통해서 우리 어플리케이션의 wsgi가 설정되어있는 경로를 알게 됩니다. 

<details>
    <summary>.ebextensions란?</summary>
    AWS Elastic Beanstalk 구성파일을 추가하여 환경을 구성하고 환경에 있는 AWS 리소스를 사용자 지정하기 위해 필요한 폴더<br>
    스펠링을 주의해야합니다.
</details>



![image](https://user-images.githubusercontent.com/42667951/82213893-de580d00-994f-11ea-953e-c3dd98ab992f.png)

여기까지 완료했을 때 파일구조는 다음과 같아야 합니다! 이 구조 아주 중요하니깐 배포하기전에 두번 세번 확인하세요!



#### 3. 배포

배포 전에 지금까지 했던 내용들을 repository에 push해봅시다. 이 과정은 Elastic Beanstalk을 이용한 배포에서는 필수적인 과정이에요. 

> 왜 필수적이죠?

EB CLI는 로컬 commit을 push하고, eb create 또는 eb deploy를 사용할 때 이 commit을 사용하여 애플리케이션 버전을 생성합니다. 그래서 업로드할 때 프로젝트 전체를 업로드 하는 대신에, 배포 시 repository에 변경 사항만 업로드 할 수 있어요.

그래서 변경 사항을 배포 할 때 꼭 변경 사항을 commit 해야 합니다.



이제 배포를 하기 위해서 가상환경을 끕시다.

```bash
$ deactivate
```

eb init 명령어를 이용해서 Elastic Beanstalk 플랫폼, 지역, 어플리케이션 이름을 지정하여 초기화 시켜줍시다.

```bash
$ eb init -p python-3.6 {어플리케이션 이름}
```

![image](https://user-images.githubusercontent.com/42667951/82214979-9934da80-9951-11ea-9411-58e006241077.png)

이렇게 credentials를 제공하라고 뜨면 아까 저장했던 IAM credential CSV파일에 있는 id랑 key를 입력해줍니다! 

- ~/.aws/config 랑 ~/.aws/credential 파일이 이미 존재하는 사람은 user를 명시해서 init을 하거나 처음부터 `aws configure`명령어(pip install awscli 필요)를 이용해서 접속하면 됩니다. 

```
Application ebdeploy has been created.
```

이런 말이 나오면 정상적으로 어플리케이션이 생성된거에요. 이 말이 뜨지 않으면 문제가 있는거니 전 과정을 다시 살펴보길 바랍니다.



다음은 Elastic Beanstalk 환경을 생성해줄게요! 

```
$ eb create {환경 이름}
```

![image](https://user-images.githubusercontent.com/42667951/82216032-45c38c00-9953-11ea-9739-199ec8f79547.png)

```
2020-05-18 12:53:50    INFO    Successfully launched environment: ebdeploy
```

위와 같이 마지막으로 뜨면 성공적으로 환경이 생성 된겁니다.

이제 우리의 도메인 별명인 CName을 확인할게요.

```bash
$ eb status
```

![image](https://user-images.githubusercontent.com/42667951/82216432-eb76fb00-9953-11ea-8076-778fa77e455d.png)

음 상태가 초록색 건강하네요. 저기 CName을 복사해서 프로젝트의 settings.py에 있는 ALLOWED HOST에 넣어줍시다.

```python
ALLOWED_HOSTS = ['ebdeploy.eba-y2mpyp3h.us-west-2.elasticbeanstalk.com']

```



이제 수정된 사항을 github repository에 업로드하고 (commit , push하는거 절대 잊지 말기) 이제 배포를 합시다

```bash
$ eb deploy
```

![image](https://user-images.githubusercontent.com/42667951/82216959-abfcde80-9954-11ea-89bf-799d3811a7bb.png)

이렇게 뜨면 배포가 성공적으로 된겁니다!

이제 배포가 잘 되었는지 확인해봅시다. 두근두근~

```bash
$ eb open
```

![image](https://user-images.githubusercontent.com/42667951/82217052-d77fc900-9954-11ea-9881-1a19de5494c4.png)

짜잔~~~~ 많이 허접하지만...ㅋㅋㅋㅋㅋㅋ CName url로 성공적으로 배포된 것을 확인할 수 있습니다.

![image](https://user-images.githubusercontent.com/42667951/82223276-6bee2980-995d-11ea-9e6a-94f3123bff96.png)

staticfile도 별 설정 없이 이렇게 잘 배포 되는 것을 확인할 수 있습니다!



**++  시간 남으면 Amazon 에서 IAM으로 로그인 해서 내 리소스 볼 수 있는 방법 알려주기**



### 회고

참 방법은 정말 간단한데 왜 이렇게 환경에 따라 오류가 다 다르고 많이 나는지... 이렇게 정리해놓고 보니깐 진짜 간단하죠?

그럼 제가 하면서 생겼던 오류랑 오류 검색 방법을 마지막으로 정리해볼게요.

#### 1. window환경과 linux환경의 충돌

가상환경을 이용해서 pip install awsebcli로 인해 설치되는 패키지들 (window)과 EB를 이용해서 지정해줄 패키지를 구별해주기

#### 2. Django 버전과 EB 플랫폼 python 버전 맞추기

django==2.1.1, python-3.6

#### 3. 배포 문제 검색시 `eb logs`확인

```bash
$ eb logs
```

이 명령어를 치면 현재 로그들과 에러의 로그들을 확인할 수 있습니다. 에러가 어떠한 이유에서 생겼는지 확인할 수 있는 방법입니다. 



이후에 DB연결, Docker 연동 ... 등의 배포도 함께 진행해 봅시다!

### 출처

[아키텍쳐  : 초보몽키의 개발공부로그 ](https://wayhome25.github.io/django/2018/03/03/django-deploy-02-nginx-wsgi/ )

[wsgi 추천](https://brownbears.tistory.com/350)

[배포 잘 정리해놓은 사이트 추천](https://nachwon.github.io/django-deploy-1-aws/)



