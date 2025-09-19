import mysql.connector
import configparser

# 读取配置文件
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini", encoding="utf-8")

# 设置数据库连接
DB_HOST = CONFIG["Sql"]["host"]
DB_USER = CONFIG["Sql"]["user"]
DB_PASSWORD = CONFIG["Sql"]["password"]
DB_DATABASE = CONFIG["Sql"]["database"]
DB_PORT = int(CONFIG["Sql"]["port"])
DB_CHARSET = CONFIG["Sql"]["charset"]


class tjSql:
    """
    A class for handling MySQL database
    """

    def __init__(self):
        """
        Initialize the database connection
        """
        self.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            port=DB_PORT,
            charset=DB_CHARSET,
        )
        self.cursor = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
        self.db.close()

    def insertCalendar(self, course):
        """
        Insert calendar into database
        """
        # if exists, return
        sql = "SELECT * FROM calendar WHERE calendarId = %s"

        val = (course["calendarId"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = "INSERT INTO calendar (calendarId, calendarIdI18n) VALUES (%s, %s)"

        val = (course["calendarId"], course["calendarIdI18n"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertCourseLabel(self, course):
        """
        Insert courseLabel into database
        """
        # if none, return
        if course["courseLabelId"] is None:
            return

        # if exists, return
        sql = "SELECT * FROM coursenature WHERE courseLabelId = %s"

        val = (course["courseLabelId"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = (
            "INSERT INTO coursenature (courseLabelId, courseLabelName) VALUES (%s, %s)"
        )

        val = (course["courseLabelId"], course["courseLabelName"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertAssessmentMode(self, course):
        """
        Insert assessmentMode into database
        """
        # if none, return
        if course["assessmentMode"] is None:
            return

        # if exists, return
        sql = "SELECT * FROM assessment WHERE assessmentMode = %s"

        val = (course["assessmentMode"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = "INSERT INTO assessment (assessmentMode, assessmentModeI18n) VALUES (%s, %s)"

        val = (course["assessmentMode"], course["assessmentModeI18n"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertCampus(self, course):
        """
        Insert campus into database
        """
        # if none, return
        if course["campus"] is None:
            return

        # if exists, return
        sql = "SELECT * FROM campus WHERE campus = %s"

        val = (course["campus"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = "INSERT INTO campus (campus, campusI18n) VALUES (%s, %s)"

        val = (course["campus"], course["campusI18n"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertFaculty(self, course):
        """
        Insert faculty into database
        """
        # if exists, return
        sql = "SELECT * FROM faculty WHERE faculty = %s"

        val = (course["faculty"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = "INSERT INTO faculty (faculty, facultyI18n) VALUES (%s, %s)"

        val = (course["faculty"], course["facultyI18n"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertMajors(self, majors):
        """
        Insert major into database,
        majors is an array
        """
        # if majors is empty, return
        if majors is None:
            return

        for major in majors:
            # process major
            processedMajor = {
                "code": major.split("(")[1].split(" ")[0],
                "grade": major[:4],  # first four characters of major is grade
                "name": major,
            }

            # if exists, skip
            sql = "SELECT * FROM major WHERE code = %s AND grade = %s"

            val = (processedMajor["code"], processedMajor["grade"])

            self.cursor.execute(sql, val)

            if self.cursor.fetchone() is not None:
                continue

            # Insert
            sql = "INSERT INTO major (code, grade, name) VALUES (%s, %s, %s)"

            val = (
                processedMajor["code"],
                processedMajor["grade"],
                processedMajor["name"],
            )

            self.cursor.execute(sql, val)

        self.db.commit()

    def insertTeachers(self, teachers, arrangeInfo):
        """
        Insert teachers into database,
        no need to check if exists,
        because schedule is unique
        """
        # split arrangeInfo to array by '\n'
        arrangeInfo = arrangeInfo.split("\n")

        for teacher in teachers:
            # Grep arrangeInfo for this teacher
            teacherSchedule = ""

            for info in arrangeInfo:
                if teacher["teacherName"] in info:
                    teacherSchedule += info + "\n"

            # Insert teacher
            sql = "INSERT INTO teacher (id, teachingClassId, teacherCode, teacherName, arrangeInfoText) VALUES (%s, %s, %s, %s, %s)"

            val = (
                teacher["id"],
                teacher["teachingClassId"],
                teacher["teacherCode"],
                teacher["teacherName"],
                teacherSchedule,
            )

            self.cursor.execute(sql, val)

        self.db.commit()

    def insertMajorAndCourse(self, majors, courseId):
        """
        Insert major and course into database
        """
        # if majors is empty, return
        if majors is None:
            return

        for major in majors:
            # Get majorId
            sql = "SELECT id FROM major WHERE name = %s"

            val = (major,)

            self.cursor.execute(sql, val)

            majorId = self.cursor.fetchone()[0]

            # Insert
            sql = "INSERT INTO majorandcourse (majorId, courseId) VALUES (%s, %s)"

            val = (majorId, courseId)

            self.cursor.execute(sql, val)

        self.db.commit()

    def insertLanguage(self, course):
        """
        Insert language into database
        """
        # if exists, return
        sql = "SELECT * FROM language WHERE teachingLanguage = %s"

        val = (course["teachingLanguage"],)

        self.cursor.execute(sql, val)

        if self.cursor.fetchone() is not None:
            return

        # Insert
        sql = "INSERT INTO language (teachingLanguage, teachingLanguageI18n) VALUES (%s, %s)"

        val = (course["teachingLanguage"], course["teachingLanguageI18n"])

        self.cursor.execute(sql, val)

        self.db.commit()

    def insertCourseList(self, courses):
        """
        Insert course list into database
        """
        for course in courses:  # The courses array contains 20 courses
            # Handle Foreign Key Constraint First

            self.insertLanguage(course)  # Insert language

            self.insertCourseLabel(course)  # Insert courseLabel

            self.insertAssessmentMode(course)  # Insert assessmentMode

            self.insertCampus(course)  # Insert campus

            self.insertFaculty(course)  # Insert faculty

            self.insertCalendar(course)  # Insert calendar

            self.insertMajors(course["majorList"])  # Insert major

            sql = (
                "INSERT INTO coursedetail ("
                "id, "
                "code, "
                "name, "
                "courseLabelId, "
                "assessmentMode, "
                "period, "
                "weekHour, "
                "campus, "
                "number, "
                "elcNumber, "
                "startWeek, "
                "endWeek, "
                "courseCode, "
                "courseName, "
                "credit, "
                "teachingLanguage, "
                "faculty, "
                "calendarId"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )

            val = (
                course["id"],
                course["code"],
                course["name"],
                course["courseLabelId"],
                course["assessmentMode"],
                course["period"],
                course["weekHour"],
                course["campus"],
                course["number"],
                course["elcNumber"],
                course["startWeek"],
                course["endWeek"],
                course["courseCode"],
                course["courseName"],
                course["credits"],
                course["teachingLanguage"],
                course["faculty"],
                course["calendarId"],
            )

            try:
                self.cursor.execute(sql, val)

                self.db.commit()
            except Exception as e:
                print(e)
                print(val)
                print("\n\n\n插入数据发生异常\n\n\n")

            try:
                self.insertTeachers(
                    course["teacherList"], course["arrangeInfo"]
                )
                self.insertMajorAndCourse(
                    course["majorList"], course["id"]
                )
            except Exception as e:
                print(e)
                print("\n\n\n插入教师数据发生异常\n\n\n")

    def summarizeClassroomsSchedule(self):
        """
        Summarize classrooms course schedule based on teacher `arrangeInfoText`, for feature: `Classroom Schedule`
        You need to fill out the table: `classroom_info` and `classroom_schedule`
        """
        import re

        print("开始分析并填充教室课表数据...")

        try:
            self.cursor.execute("DELETE FROM classroom_schedule")
            self.cursor.execute("DELETE FROM classroom_info")
            self.db.commit()
            print("已清空现有的教室数据表")
        except Exception as e:
            print(f"清空教室数据表时出错: {e}")

        # 获取所有有效的课程和教师安排信息
        query = """
        SELECT DISTINCT 
            t.arrangeInfoText,
            cd.id as courseId,
            cd.courseName,
            cd.campus,
            cd.calendarId,
            t.teacherName,
            t.teacherCode
        FROM teacher t 
        JOIN coursedetail cd ON t.teachingClassId = cd.id
        WHERE t.arrangeInfoText IS NOT NULL 
        AND t.arrangeInfoText != ''
        AND t.arrangeInfoText != 'null'
        """

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        classroom_info_dict = {}  # 用于去重教室信息并生成ID映射
        classroom_schedules = []  # 存储课表信息

        weekday_map = {
            '星期一': 1, '星期二': 2, '星期三': 3, '星期四': 4,
            '星期五': 5, '星期六': 6, '星期日': 7
        }

        campus_map = {'1': '四平路校区', '3': '嘉定校区', '4': '沪西校区'}  # 校区映射

        processed_count = 0

        for row in results:
            arrange_text, course_id, course_name, campus, calendar_id, teacher_name, teacher_code = row

            # 确保arrange_text是字符串类型
            if not arrange_text or not isinstance(arrange_text, str):
                continue

            # 解析arrange_text中的每一行
            lines = str(arrange_text).strip().split('\n')

            for line in lines:
                line = str(line).strip()
                if not line:
                    continue

                # 使用正则表达式解析格式: "教师名(工号) 星期X节次 [周次] 教室"
                pattern = r'(.+?)\((\d+)\)\s+(星期[一二三四五六日])(\d+-?\d*)节\s+\[(\d+-?\d*)\]\s+(.+?)(?:\s|$)'
                match = re.search(pattern, str(line))

                if match:
                    teacher, teacher_id, weekday, periods, weeks, classroom = match.groups()

                    # 解析教室信息并确定校区
                    classroom = str(classroom).strip()
                    if not classroom:
                        continue

                    # 根据教室名称确定校区和楼宇
                    classroom_campus = None
                    building = ""

                    if re.match(r'[ABGF]\d{3}', classroom):  # 嘉定校区
                        classroom_campus = '嘉定校区'
                        building_code = classroom[0]
                        if building_code == 'A':
                            building = '安楼'
                        elif building_code == 'B':
                            building = '博楼'
                        elif building_code == 'G':
                            building = '广楼'
                        elif building_code == 'F':
                            building = '复楼'
                    elif re.match(r'[南北]\d{3}', classroom):  # 四平路校区
                        classroom_campus = '四平路校区'
                        if classroom.startswith('南'):
                            building = '南楼'
                        elif classroom.startswith('北'):
                            building = '北楼'
                    elif '沪西二教' in classroom:  # 沪西校区
                        classroom_campus = '沪西校区'
                        building = '二教'
                    else:
                        # 默认使用课程的校区
                        classroom_campus = campus_map.get(str(campus), '四平路校区')
                        building = '未知楼宇'

                    # 添加教室信息到字典中（去重）
                    if classroom not in classroom_info_dict:
                        classroom_info_dict[classroom] = {
                            'building': building,
                            'campus': classroom_campus
                        }

                    # 解析时间段
                    if '-' in periods:
                        start_period, end_period = map(int, periods.split('-'))
                    else:
                        start_period = end_period = int(periods)

                    # 解析周次
                    if '-' in weeks:
                        start_week, end_week = map(int, weeks.split('-'))
                    else:
                        start_week = end_week = int(weeks)

                    # 获取星期几的数字
                    weekday_num = weekday_map.get(weekday, 1)

                    # 为每个时间段创建课表记录
                    for period in range(start_period, end_period + 1):
                        classroom_schedules.append({
                            'classroom_name': classroom,
                            'calendar_id': calendar_id,
                            'course_id': course_id,
                            'day_of_week': weekday_num,
                            'time_slot': period,
                            'week_start': start_week,
                            'week_end': end_week,
                            'teacher_name': teacher_name,
                            'course_name': course_name
                        })

            processed_count += 1
            if processed_count % 100 == 0:
                print(f"已处理 {processed_count} 条课程记录...")

        # 插入教室信息
        print(f"准备插入 {len(classroom_info_dict)} 个教室...")
        classroom_info_sql = "INSERT INTO classroom_info (classroom_name, building, campus) VALUES (%s, %s, %s)"
        classroom_id_map = {}  # 教室名称到ID的映射

        for classroom_name, info in classroom_info_dict.items():
            try:
                self.cursor.execute(
                    classroom_info_sql, (classroom_name, info['building'], info['campus']))
                classroom_id = self.cursor.lastrowid
                classroom_id_map[classroom_name] = classroom_id
            except Exception as e:
                print(f"插入教室信息失败 {classroom_name}: {e}")

        self.db.commit()
        print(f"成功插入 {len(classroom_info_dict)} 个教室信息")

        # 插入课表信息
        print(f"准备插入 {len(classroom_schedules)} 条课表记录...")
        schedule_sql = """
        INSERT INTO classroom_schedule 
        (classroom_id, calendar_id, day_of_week, time_slot, week_start, week_end, course_id, course_name, teacher_name) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        batch_size = 1000
        successful_inserts = 0

        for i in range(0, len(classroom_schedules), batch_size):
            batch = classroom_schedules[i:i + batch_size]
            batch_values = []

            for schedule in batch:
                classroom_id = classroom_id_map.get(schedule['classroom_name'])
                if classroom_id:
                    batch_values.append((
                        classroom_id,
                        schedule['calendar_id'],
                        schedule['day_of_week'],
                        schedule['time_slot'],
                        schedule['week_start'],
                        schedule['week_end'],
                        schedule['course_id'],
                        schedule['course_name'],
                        schedule['teacher_name']
                    ))

            if batch_values:
                try:
                    self.cursor.executemany(schedule_sql, batch_values)
                    self.db.commit()
                    successful_inserts += len(batch_values)
                    print(
                        f"已插入 {successful_inserts} / {len(classroom_schedules)} 条课表记录")
                except Exception as e:
                    print(f"插入课表记录批次失败: {e}")
                    # 尝试逐条插入以找出问题记录
                    for values in batch_values:
                        try:
                            self.cursor.execute(schedule_sql, values)
                            successful_inserts += 1
                        except Exception as e2:
                            print(f"单条记录插入失败: 教室ID={values[0]} - {e2}")
                    self.db.commit()

        print("教室课表数据汇总完成！")
        print(f"总共处理了 {processed_count} 条课程记录")
        print(f"生成了 {len(classroom_info_dict)} 个教室信息")
        print(f"成功插入了 {successful_inserts} 条课表记录")

    # NOTE 删除了增量更新函数
    # 上游教务信息每学期基本不会变，所以备份之后整个重新拉取一遍数据是比较省事的
