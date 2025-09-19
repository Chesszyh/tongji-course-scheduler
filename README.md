# TONGJI-COURSE-SCHEDULER

## Archived(来自原作者)

不再打算开发。未来可以提升的空间是，在数据库表的属性中添加爬取编号，从而便于同步 1 系统数据库的内容。

## TODO

- [x] Dockerfile

## Preparation

Download the project, at root folder, run: 

```bash
git clone --depth=1 https://github.com/XiaLing233/tongji-course-scheduler
cd tongji-course-scheduler

# Install Python dependencies
python -m venv .venv # create a virtual environment, recommended

# Activate the virtual environment
.\.venv\Scripts\activate # On Windows
source .venv/bin/activate # On macOS/Linux

pip install -r requirements.txt

# Install frontend dependencies
cd xkFrontendts
npm install
```

to install all dependencies. 

Then, you should prepare a local mysql database. For example, if you are using Docker to run a mysql container on port 3306:

```bash
docker pull mysql
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=... \
  -e MYSQL_DATABASE=tongji_course \
  -p 127.0.0.1:3306:3306 \
  -v ~/mysql-data:/var/lib/mysql \
  mysql
```

You can also deploy mysql manually.

## Configuration

### database

First, login to MySQL:

```bash
docker exec -it mysql mysql -uroot -p
```

After logging in, you need to create the database schema for the application to work properly. [Reference schema file](./crawler/utils/sqls/1_schema.sql):

### crawler

To make login function possible, you need to add a `config.ini` file at `./crawler`, which includes your student ID and password in clear text:

```ini
# file_path: ./crawler/config.ini
[Account]
sno = your_student_id  # no need to add "" around values, e.g sno = "2365472" is WRONG
passwd = your_password

[IMAP]
server_domain = imap.qq.com
server_port = 993
qq_emailaddr = your_id@qq.com
qq_grantcode = your_grant_code # You need to enable IMAP in QQ Mail settings and get the authorization code

[Sql]
host = 127.0.0.1
user = root
password = root_password
# user and r_user should be different in production
r_user = read_only_user
r_password = read_only_user_password
database = tongji_course
port = 3306
charset = utf8mb4
```

### backend

Here's the template of `config.ini` file at `./backend`.

```ini
# file_path: ./backend/config.ini
[Sql]
host = 127.0.0.1
r_user = read_only_user
r_password = read_only_user_password
database = tongji_course
port = 3306
charset = utf8mb4

[Switch]
debug = 0
```

## Start the application

```bash
# Make sure your mysql server is running

# Start the crawler.
# This will fetch the course list from the university website. It may take a while.
cd crawler
python fetchCourseList.py

# Start the backend
cd ../backend
flask run --port=1239

# Start the frontend
cd ../xkFrontendts

# Development mode (with hot-reload)
npm run dev             # global access, start on 5173
npm run dev:localhost   # local access, start on localhost:5173

# Compile and Minify for Production
npm run build           # skip type checking to speed up build
npm run build:check     # with type checking

# Production mode
npm run serve           # will start on localhost:4173
```

Then you can access the application at `http://localhost:5173`.

## Docker Deployment

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system.

### Quick Start with Docker

First, you should also prepare the `config.ini` files(crawler and backend) as described above.

Then, you can start the entire application stack using Docker Compose:

```bash
# Start the database, backend and frontend
docker-compose up -d

# Wait for the database to initialize (about 30-60 seconds)
# Check if database is ready
docker-compose logs mysql

# Run the crawler to fetch course data (only when needed)
docker-compose --profile crawler up crawler
```

Now you can access the application:

- Frontend: http://localhost
- Backend API: http://localhost:1239

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Rebuild images after code changes
docker-compose build
docker-compose up -d

# Run crawler only
docker-compose --profile crawler up crawler

# Access database
docker-compose exec mysql mysql -utongji_user -ptongji_pass tongji_course
```

## Personal Note(Fork Author)

- branch:
  - custom: 保留了小的修改，包括config路径、手动登陆等，readme比master稍晚一点
  - master: 撤销了config修改，保留了手动登陆，readme最新
    - 直接基于原项目进行个人二次开发，详见`CHANGE_LOG.md`。

