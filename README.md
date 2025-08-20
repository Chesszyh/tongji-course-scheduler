# TONGJI-COURSE-SCHEDULER

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

Then, you should prepare a local mysql database. For example if you are using Docker to run a mysql container on 3306:

```bash
docker pull mysql
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=test \
  -p 3306:3306 \
  -v ~/mysql-data:/var/lib/mysql \
  mysql
```

You can also deploy mysql manually.

## Configuration

### database

First, login to MySQL:

```bash
docker exec -it mysql mysql -uroot -p your_password
```

After logging in, you need to create the database schema for the application to work properly.

```sql
CREATE DATABASE tongji_course;
use tongji_course;

-- 课程性质表
CREATE TABLE `coursenature` (
  `courseLabelId` INT NOT NULL,
  `courseLabelName` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`courseLabelId`)
);

-- 校区表
CREATE TABLE `campus` (
  `campus` VARCHAR(255) NOT NULL,
  `campusI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`campus`)
);

-- 学院表
CREATE TABLE `faculty` (
  `faculty` VARCHAR(255) NOT NULL,
  `facultyI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`faculty`)
);

-- 学期表
CREATE TABLE `calendar` (
  `calendarId` INT NOT NULL,
  `calendarIdI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`calendarId`)
);

-- 授课语言表
CREATE TABLE `language` (
  `teachingLanguage` VARCHAR(255) NOT NULL,
  `teachingLanguageI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`teachingLanguage`)
);

-- 考核方式表
CREATE TABLE `assessment` (
  `assessmentMode` VARCHAR(255) NOT NULL,
  `assessmentModeI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`assessmentMode`)
);

-- 专业表
CREATE TABLE `major` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(255) DEFAULT NULL,
  `grade` VARCHAR(255) DEFAULT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `major_code_grade` (`code`,`grade`)
);

-- 课程详情表
CREATE TABLE `coursedetail` (
  `id` VARCHAR(255) NOT NULL,
  `code` VARCHAR(255) DEFAULT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  `courseLabelId` INT DEFAULT NULL,
  `assessmentMode` VARCHAR(255) DEFAULT NULL,
  `period` VARCHAR(255) DEFAULT NULL,
  `weekHour` INT DEFAULT NULL,
  `campus` VARCHAR(255) DEFAULT NULL,
  `number` INT DEFAULT NULL,
  `elcNumber` INT DEFAULT NULL,
  `startWeek` INT DEFAULT NULL,
  `endWeek` INT DEFAULT NULL,
  `courseCode` VARCHAR(255) DEFAULT NULL,
  `courseName` VARCHAR(255) DEFAULT NULL,
  `credit` FLOAT DEFAULT NULL,
  `teachingLanguage` VARCHAR(255) DEFAULT NULL,
  `faculty` VARCHAR(255) DEFAULT NULL,
  `calendarId` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `courseCode` (`courseCode`),
  KEY `calendarId` (`calendarId`),
  KEY `courseLabelId` (`courseLabelId`),
  CONSTRAINT `coursedetail_ibfk_1` FOREIGN KEY (`courseLabelId`) REFERENCES `coursenature` (`courseLabelId`),
  CONSTRAINT `coursedetail_ibfk_2` FOREIGN KEY (`campus`) REFERENCES `campus` (`campus`),
  CONSTRAINT `coursedetail_ibfk_3` FOREIGN KEY (`faculty`) REFERENCES `faculty` (`faculty`),
  CONSTRAINT `coursedetail_ibfk_4` FOREIGN KEY (`calendarId`) REFERENCES `calendar` (`calendarId`),
  CONSTRAINT `coursedetail_ibfk_5` FOREIGN KEY (`teachingLanguage`) REFERENCES `language` (`teachingLanguage`),
  CONSTRAINT `coursedetail_ibfk_6` FOREIGN KEY (`assessmentMode`) REFERENCES `assessment` (`assessmentMode`)
);

-- 教师表
CREATE TABLE `teacher` (
  `id` VARCHAR(255) NOT NULL,
  `teachingClassId` VARCHAR(255) DEFAULT NULL,
  `teacherCode` VARCHAR(255) DEFAULT NULL,
  `teacherName` VARCHAR(255) DEFAULT NULL,
  `arrangeInfoText` TEXT,
  PRIMARY KEY (`id`),
  KEY `teachingClassId` (`teachingClassId`),
  CONSTRAINT `teacher_ibfk_1` FOREIGN KEY (`teachingClassId`) REFERENCES `coursedetail` (`id`)
);

-- 专业与课程关联表
CREATE TABLE `majorandcourse` (
  `majorId` INT NOT NULL,
  `courseId` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`majorId`,`courseId`),
  KEY `courseId` (`courseId`),
  CONSTRAINT `majorandcourse_ibfk_1` FOREIGN KEY (`majorId`) REFERENCES `major` (`id`),
  CONSTRAINT `majorandcourse_ibfk_2` FOREIGN KEY (`courseId`) REFERENCES `coursedetail` (`id`)
);

-- 抓取日志表
CREATE TABLE `fetchlog` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fetchTime` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
);
```

### crawler

To make login function possible, you need to add a `config.ini` file at `./crawler`, which includes your student ID and password in clear text:

> TODO: Is qq email still needed?

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
manual_login = True

[Sql]
host = 127.0.0.1
user = root
password = your_password
database = tongji_course
port = 3306
charset = utf8mb4
```

### backend

You also need to configure the backend. NOTE that `r_user` should only have read access to the database. You can still use root for simplicity.

```ini
# file_path: ./backend/config.ini
[Sql]
host = 127.0.0.1
r_user = root
r_password = your_password
database = tongji_course
port = 3306
charset = utf8mb4

[Switch]
debug = 0
```

## Start the application

```bash
# Start the crawler.
# This will fetch the course list from the university website. It may take a while.
python crawler/fetchCourseList.py

# Start the backend
python backend/app.py # default on 5000

# Start the frontend
cd xkFrontendts
npm run dev # default on 5173
```

Then you can access the application at `http://localhost:5173`.
