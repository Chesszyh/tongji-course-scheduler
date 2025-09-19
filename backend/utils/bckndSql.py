import mysql.connector
import configparser
import json

# 读取配置文件
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini", encoding="utf-8")

# 设置数据库连接
DB_HOST = CONFIG["Sql"]["host"]
DB_USER = CONFIG["Sql"]["r_user"]  # 只读用户
DB_PASSWORD = CONFIG["Sql"]["r_password"]  # 只读用户密码
DB_DATABASE = CONFIG["Sql"]["database"]
DB_PORT = int(CONFIG["Sql"]["port"])
DB_CHARSET = CONFIG["Sql"]["charset"]


class bckndSql:
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

    def getAllCalendar(self):
        """
        Get all calendar data
        """
        self.cursor.execute(
            f'SELECT JSON_OBJECT("calendarId", calendarId, "calendarName", calendarIdI18n) FROM calendar ORDER BY calendarId DESC'
        )

        result = self.cursor.fetchall()

        # json str result to json
        return [json.loads(calendar[0]) for calendar in result]

    def getAllCampus(self):
        """
        Get all campus data
        """
        self.cursor.execute(
            f'SELECT JSON_OBJECT("campusId", campus, "campusName", campusI18n) FROM campus'
        )

        result = self.cursor.fetchall()

        # json str result to json
        return [json.loads(campus[0]) for campus in result]

    def getAllFaculty(self):
        """
        Get all faculty data
        """
        self.cursor.execute(
            f'SELECT JSON_OBJECT("facultyId", faculty, "facultyName", facultyI18n) FROM faculty'
        )

        result = self.cursor.fetchall()

        # json str result to json
        return [json.loads(faculty[0]) for faculty in result]

    def findGradeByCalendarId(self, calendarId):
        """
        Find grade by calendarId
        """

        query = (
            f"SELECT DISTINCT m.grade FROM major AS m"
            f" JOIN majorandcourse AS mac ON mac.majorId = m.id"
            f" JOIN coursedetail AS c ON c.id = mac.courseId"
            f" WHERE c.calendarId = %s"
            f" ORDER BY m.grade DESC"
        )

        self.cursor.execute(query, (calendarId,))

        result = self.cursor.fetchall()

        # Convert to list
        return [grade[0] for grade in result]

    def findMajorByGrade(self, grade):
        """
        Find major by grade
        """

        query = (
            "SELECT JSON_OBJECT("
            " 'code', m.code,"
            " 'name', m.name"
            " )"
            " FROM major AS m"
            " WHERE m.grade = %s"
            " ORDER BY m.code ASC"
        )

        self.cursor.execute(query, (grade,))

        result = self.cursor.fetchall()

        # json str result to json
        return [json.loads(major[0]) for major in result]

    def findCourseByMajor(self, grade, code, calendarId):
        """
        Find course by major, maybe exists duplicate courses
        """
        query = f"""
        SELECT
            JSON_OBJECT(
                'courseCode', c.courseCode,
                'courseName', c.courseName,
                'faculty', f.facultyI18n,
                'credit', c.credit,
                'grade', codes.grade,
                'courseNature', CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(n.courseLabelName)), ']') AS JSON),  -- 去重
                'courses',
                    JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'code', c.code,
                            'teachers', teachers.teachers,
                            'campus', ca.campusI18n,
                            'locations', locations.locations,
                            'teachingLanguage', l.teachingLanguageI18n,
                            'isExclusive', 
                                -- 判断是否存在关联的专业课程记录
                                IF(mac_exclusive.majorId IS NOT NULL, TRUE, FALSE)
                        )
                    )
            )
        FROM coursedetail as c
        JOIN faculty as f ON f.faculty = c.faculty
        JOIN coursenature as n ON n.courseLabelId = c.courseLabelId
        JOIN campus as ca ON c.campus = ca.campus
        JOIN language as l ON l.teachingLanguage = c.teachingLanguage
        -- 获取教师信息
        JOIN (
            SELECT t.teachingClassid, 
                   JSON_ARRAYAGG(
                       JSON_OBJECT(
                           'teacherCode', t.teacherCode,
                           'teacherName', t.teacherName
                       )
                   ) AS teachers
            FROM teacher AS t
            GROUP BY t.teachingClassid
        ) AS teachers ON c.id = teachers.teachingClassid
        -- 获取地点信息
        JOIN (
            SELECT t.teachingClassid, 
                   t.arrangeInfoText AS locations
            FROM teacher AS t
        ) AS locations ON c.id = locations.teachingClassid
        -- 获取筛选条件和grade，并关联专业课程关系
        JOIN (
            SELECT DISTINCT 
                c.courseCode as myCode,
                m.grade,
                m.id as targetMajorId  -- 新增：获取目标专业ID
            FROM major AS m
            JOIN majorandcourse AS mac ON m.id = mac.majorId
            JOIN coursedetail as c ON mac.courseid = c.id
            WHERE 
                m.grade <= %s
                AND m.code = %s
                AND c.calendarId = %s
        ) AS codes ON c.courseCode = codes.myCode
        -- 检查是否属于专属专业（新增LEFT JOIN）
        LEFT JOIN majorandcourse AS mac_exclusive 
            ON mac_exclusive.courseid = c.id 
            AND mac_exclusive.majorId = codes.targetMajorId  -- 关联目标专业ID
        WHERE c.calendarId = %s
        GROUP BY c.courseCode, c.courseName, f.facultyI18n, codes.grade, c.credit
        """
        self.cursor.execute(query, (grade, code, calendarId, calendarId))

        result = self.cursor.fetchall()

        result = [json.loads(course[0]) for course in result]

        return result

    def findOptionalCourseType(self, labelList, calendarId):
        """
        Find optional course type
        """

        query = (
            f"SELECT DISTINCT"
            f" n.courseLabelId,"
            f" n.courseLabelName"
            f" FROM coursenature AS n"
            f" JOIN coursedetail AS c ON n.courseLabelId = c.courseLabelId"
            f" WHERE n.courseLabelName IN ({','.join(['%s' for _ in labelList])})"
            f" AND c.calendarId = %s"
            f" ORDER BY n.courseLabelId DESC"
        )

        self.cursor.execute(query, tuple(labelList + [calendarId]))

        result = self.cursor.fetchall()

        # 添加头部
        result = [
            {"courseLabelId": course[0], "courseLabelName": course[1]}
            for course in result
        ]

        return result

    def findCourseByNatureId(self, natureIds, calendarId):
        """
        Find course by natureId
        """

        query = f"""
        SELECT
            JSON_OBJECT(
                'courseLabelId', courseLabelId,
                'courseLabelName', courseLabelName,
                'courses', JSON_ARRAYAGG(
                            JSON_OBJECT(
                                'courseCode', courseCode,
                                'courseName', courseName,
                                'faculty', facultyI18n,
                                'credit', credit,
                                'campus', campus_list
                            )
                        )
            )
        FROM (
            SELECT
                c.courseLabelId,
                n.courseLabelName,
                c.courseCode,
                c.courseName,
                c.credit,
                f.facultyI18n,
                CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(ca.campusI18n) ORDER BY ca.campusI18n), ']') AS JSON) AS campus_list  -- 去重校区列表，并按校区名排序
            FROM coursedetail as c
            JOIN faculty as f ON f.faculty = c.faculty
            JOIN coursenature as n ON n.courseLabelId = c.courseLabelId
            JOIN campus as ca ON c.campus = ca.campus
            JOIN calendar as cal ON c.calendarId = cal.calendarId
            WHERE c.courseLabelId IN ({','.join(['%s' for _ in natureIds])})
            AND c.calendarId = %s
            GROUP BY 
                c.courseLabelId,
                c.courseCode,  -- 按课程代码分组
                c.courseName,
                c.credit,
                f.facultyI18n
        ) AS grouped_courses
        GROUP BY courseLabelId, courseLabelName
        ORDER BY courseLabelId DESC;
        """

        self.cursor.execute(query, tuple(natureIds + [calendarId]))

        result = self.cursor.fetchall()

        # json
        result = [json.loads(res[0]) for res in result]

        # 再对courses字段进行json解析
        # for res in result:
        #     print(res["courses"])
        #     res["courses"] = json.loads(res["courses"])

        return result

    def findCourseDetailByCode(self, code, calendarId):
        """
        Find course detail by code
        """
        3
        query = f"""
        SELECT
            JSON_OBJECT(
            'code', c.code,
            'teachers', teachers.teachers,
            'campus', ca.campusI18n,
            'locations', locations.locations,
            'teachingLanguage', l.teachingLanguageI18n
            )
        FROM coursedetail as c
        JOIN faculty as f ON f.faculty = c.faculty
        JOIN coursenature as n ON n.courseLabelId = c.courseLabelId
        JOIN campus as ca ON c.campus = ca.campus
        JOIN language as l ON l.teachingLanguage = c.teachingLanguage
        -- 获取教师信息
        JOIN (
            SELECT t.teachingClassid, 
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'teacherCode', t.teacherCode,
                        'teacherName', t.teacherName
                    )
                ) AS teachers
            FROM teacher AS t
            GROUP BY t.teachingClassid
        ) AS teachers ON c.id = teachers.teachingClassid
        -- 获取地点信息
        JOIN (
            SELECT t.teachingClassid, 
                t.arrangeInfoText AS locations
            FROM teacher AS t
        ) AS locations ON c.id = locations.teachingClassid
        WHERE c.courseCode = %s
        AND c.calendarId = %s
        """

        self.cursor.execute(query, (code, calendarId))

        result = self.cursor.fetchall()

        # json
        result = [json.loads(res[0]) for res in result]

        # print(result)

        return result

    def findCourseBySearch(self, searchBody, sizeLimit=50):
        """
        Find course by search.
        Search Body should be an object, look like this:
        ```json
        {
            "calendarId": 119,
            "courseName": "上海",
            "courseCode": "",
            "teacherCode": "",
            "teacherName": "",
            "campus": "四平路校区",
            "faculty": "",
        }
        ```
        calendarId must exist, others should appear at least once.
        But fortunately, this logic would be done by backend, so
        we don't need to worry about this here.
        """

        condition = ""

        # Generate condition using parameterized query
        query_params = []
        condition = ""
        if searchBody["courseName"] != "":
            condition += " AND c.courseName LIKE %s"
            query_params.append("%" + searchBody["courseName"] + "%")
        if searchBody["courseCode"] != "":
            condition += " AND (c.courseCode = %s OR c.code = %s)"
            query_params.extend([searchBody["courseCode"], searchBody["courseCode"]])
        if searchBody["teacherCode"] != "":
            condition += " AND t.teacherCode = %s"
            query_params.append(searchBody["teacherCode"])
        if searchBody["teacherName"] != "":
            condition += " AND t.teacherName = %s"
            query_params.append(searchBody["teacherName"])
        if searchBody["campus"] != "":
            condition += " AND ca.campusI18n = %s"
            query_params.append(searchBody["campus"])
        if searchBody["faculty"] != "":
            condition += " AND f.facultyI18n = %s"
            query_params.append(searchBody["faculty"])

        sql = f"""
        SELECT DISTINCT
            JSON_OBJECT(
                'courseCode', c.courseCode,
                'courseName', c.courseName,
                'faculty', f.facultyI18n,
                'credit', c.credit,
                'courseNature', CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(n.courseLabelName)), ']') AS JSON),  -- 去重
                'campus', CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(ca.campusI18n) ORDER BY ca.campusI18n), ']') AS JSON) -- 去重校区列表，并按校区名排序
            )
        FROM coursedetail as c
        JOIN faculty AS f ON f.faculty = c.faculty
        JOIN campus as ca ON ca.campus = c.campus
        JOIN coursenature as n ON c.courseLabelId = n.courseLabelId
        JOIN teacher as t ON t.teachingClassid = c.id
        WHERE c.calendarId = %s
        {condition}
        GROUP BY c.courseCode, c.courseName, f.facultyI18n, c.credit
        LIMIT %s;
        """

        query_params.insert(0, searchBody["calendarId"])
        query_params.append(sizeLimit)

        self.cursor.execute(sql, tuple(query_params))

        result = self.cursor.fetchall()

        # json
        result = [json.loads(res[0]) for res in result]

        return result

    def findCourseByTime(self, strSet, labelList, calendarId):
        """
        Find course by time
        """
        query = f"""
        SELECT
            JSON_OBJECT(
                'courseCode', c.courseCode,
                'courseName', c.courseName,
                'faculty', f.facultyI18n,
                'credit', c.credit,
                'courseNature', CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(n.courseLabelName)), ']') AS JSON),  -- 去重
                'campus', CAST(CONCAT('[', GROUP_CONCAT(DISTINCT JSON_QUOTE(ca.campusI18n) ORDER BY ca.campusI18n), ']') AS JSON) -- 去重校区列表，并按校区名排序
            )
        FROM coursedetail as c
        JOIN faculty AS f ON f.faculty = c.faculty
        JOIN campus as ca ON ca.campus = c.campus
        JOIN coursenature as n ON c.courseLabelId = n.courseLabelId
        JOIN teacher as t ON t.teachingClassid = c.id
        WHERE c.calendarId = %s
        AND ({' OR '.join(['t.arrangeInfoText LIKE %s' for _ in strSet])})
        AND n.courseLabelId IN ({','.join(['%s' for _ in labelList])})
        GROUP BY c.courseCode, c.courseName, f.facultyI18n, n.courseLabelName, c.credit
        ORDER BY courseCode desc
        """

        print(strSet)

        self.cursor.execute(query, (calendarId, *strSet, *labelList))

        result = self.cursor.fetchall()

        # json
        result = [json.loads(res[0]) for res in result]

        return result

    def getLatestUpdateTime(self):
        """
        Get the latest update time
        """
        self.cursor.execute(
            f"SELECT fetchTime FROM fetchlog ORDER BY fetchTime DESC LIMIT 1"
        )

        result = self.cursor.fetchall()

        return result[0][0]

    def getAllRooms(self, calendarId):
        """
        Get all rooms from teacher arrangeInfoText
        """
        query = """
        SELECT DISTINCT 
            TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) as room
        FROM teacher AS t
        JOIN coursedetail AS c ON t.teachingClassid = c.id
        WHERE c.calendarId = %s
        AND t.arrangeInfoText IS NOT NULL 
        AND t.arrangeInfoText != ''
        AND TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) != ''
        ORDER BY room
        """

        self.cursor.execute(query, (calendarId,))
        result = self.cursor.fetchall()

        # 过滤掉无效教室名称（只包含换行符等）
        rooms = []
        for room_tuple in result:
            room = room_tuple[0].strip()
            if room and room != "\n":
                rooms.append(room)

        return rooms

    def getCoursesByRoom(self, room, calendarId):
        """
        Get courses by room name
        """
        query = """
        SELECT DISTINCT
            JSON_OBJECT(
                'courseCode', c.courseCode,
                'courseName', c.courseName,
                'code', c.code,
                'faculty', f.facultyI18n,
                'credit', c.credit,
                'campus', ca.campusI18n,
                'teachers', teachers.teachers,
                'arrangementInfo', teachers.arrangementInfo
            )
        FROM coursedetail as c
        JOIN faculty as f ON f.faculty = c.faculty
        JOIN campus as ca ON c.campus = ca.campus
        JOIN (
            SELECT 
                t.teachingClassid,
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'teacherCode', t.teacherCode,
                        'teacherName', t.teacherName
                    )
                ) AS teachers,
                t.arrangeInfoText AS arrangementInfo
            FROM teacher AS t
            WHERE t.arrangeInfoText LIKE %s
            GROUP BY t.teachingClassid, t.arrangeInfoText
        ) AS teachers ON c.id = teachers.teachingClassid
        WHERE c.calendarId = %s
        """

        room_pattern = f"%] {room}%"
        self.cursor.execute(query, (room_pattern, calendarId))

        result = self.cursor.fetchall()

        # 解析JSON结果
        courses = []
        for course_json in result:
            course_data = json.loads(course_json[0])

            # 解析排课信息
            arrangement_info = []
            if course_data["arrangementInfo"]:
                # 处理arrangeInfoText字符串
                from .bckndTools import arrangementTextToObj, splitEndline

                for location in splitEndline(course_data["arrangementInfo"]):
                    try:
                        arrangement_info.append(arrangementTextToObj(location))
                    except:
                        pass

            course_data["arrangementInfo"] = arrangement_info
            courses.append(course_data)

        return courses

    def getStudyRoomSuggestions(
        self,
        campus,
        building=None,
        dayOfWeek=None,
        startTime=None,
        endTime=None,
        calendarId=None,
        specificRoom=None,
    ):
        """
        Get study room suggestions based on criteria
        Updated for NOTE2: Only returns allowed study areas
        """
        from study_room_config import (
            CAMPUS_MAPPING,
            CAMPUS_ID_TO_NAME,
            is_allowed_classroom,
            filter_study_area_classrooms,
        )

        # 将campus参数转换为校区ID（如果需要）
        campus_id = None
        if campus in CAMPUS_ID_TO_NAME:
            campus_id = campus
        else:
            # 通过名称查找ID
            for cid, cname in CAMPUS_ID_TO_NAME.items():
                if cname == campus:
                    campus_id = cid
                    break

        campus_condition = "AND c.campus = %s" if campus_id else ""
        building_condition = ""
        specific_room_condition = ""

        # 如果指定了楼宇，添加模糊匹配条件
        if building:
            building_condition = (
                "AND (TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) LIKE %s)"
            )

        # 如果指定了具体教室且不是"All"，添加精确匹配条件
        if specificRoom and specificRoom != "All":
            specific_room_condition = (
                "AND TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) = %s"
            )

        # 查询所有在指定校区的教室
        rooms_query = f"""
        SELECT DISTINCT 
            TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) as room,
            c.campus as campus_id
        FROM teacher AS t
        JOIN coursedetail AS c ON t.teachingClassId = c.id
        WHERE c.calendarId = %s
        AND t.arrangeInfoText IS NOT NULL 
        AND t.arrangeInfoText != ''
        AND TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) != ''
        {campus_condition}
        {building_condition}
        {specific_room_condition}
        ORDER BY room
        """

        params = [calendarId]
        if campus_id:
            params.append(campus_id)
        if building:
            params.append(f"{building}%")
        if specificRoom and specificRoom != "All":
            params.append(specificRoom)

        self.cursor.execute(rooms_query, tuple(params))
        rooms_result = self.cursor.fetchall()

        all_rooms_data = []
        for room_row in rooms_result:
            room_name = room_row[0]
            room_campus_id = str(room_row[1])
            all_rooms_data.append(
                {"classroom_name": room_name, "campus_id": room_campus_id}
            )

        # 调试输出
        print(
            f"[DEBUG] getStudyRoomSuggestions: Found {len(all_rooms_data)} rooms before filtering"
        )

        # 使用新配置过滤出允许的自习区域教室
        filtered_rooms_data = []
        for room_data in all_rooms_data:
            room_name = room_data["classroom_name"]
            room_campus_id = room_data["campus_id"]

            # 检查是否属于允许的自习区域
            validation_result = is_allowed_classroom(room_name, room_campus_id)
            if validation_result["is_allowed"]:
                room_data.update(
                    {
                        "campus_name": validation_result["campus"],
                        "building_name": validation_result["building"],
                        "building_code": validation_result["building_code"],
                    }
                )
                filtered_rooms_data.append(room_data)

        print(
            f"[DEBUG] After study area filtering: {len(filtered_rooms_data)} allowed rooms"
        )

        # 分析每个教室的占用情况
        room_suggestions = []

        for room_data in filtered_rooms_data:
            room_name = room_data["classroom_name"]

            occupied_times = self._getRoomOccupiedTimes(
                room_name, dayOfWeek, calendarId
            )
            free_periods = self._calculateFreePeriods(
                occupied_times, startTime, endTime
            )

            if free_periods:
                room_suggestions.append(
                    {
                        "room": room_name,
                        "campus": room_data.get(
                            "campus_name",
                            CAMPUS_ID_TO_NAME.get(room_data["campus_id"], "Unknown"),
                        ),
                        "building": room_data.get("building_name", ""),
                        "building_code": room_data.get("building_code", ""),
                        "freePeriods": free_periods,
                        "isFullyFree": len(free_periods) == 1
                        and free_periods[0]["start"] == startTime
                        and free_periods[0]["end"] == endTime,
                        "totalFreeDuration": sum(
                            period["duration"] for period in free_periods
                        ),
                    }
                )

        # 按总空闲时长和教室名称排序（不再使用优先级）
        room_suggestions.sort(key=lambda x: (-x["totalFreeDuration"], x["room"]))

        print(f"[DEBUG] Final suggestions: {len(room_suggestions)} rooms")

        return room_suggestions

    def _getRoomOccupiedTimes(self, room, dayOfWeek, calendarId):
        """
        Get occupied time periods for a specific room on a specific day
        """
        query = """
        SELECT DISTINCT t.arrangeInfoText
        FROM teacher AS t
        JOIN coursedetail AS c ON t.teachingClassid = c.id
        WHERE c.calendarId = %s
        AND t.arrangeInfoText LIKE %s
        """

        room_pattern = f"%] {room}%"
        self.cursor.execute(query, (calendarId, room_pattern))
        arrangements = self.cursor.fetchall()

        occupied_times = []

        for arrangement in arrangements:
            arrangement_text = arrangement[0]
            if arrangement_text:
                # 解析排课信息
                from .bckndTools import arrangementTextToObj, splitEndline

                for location in splitEndline(arrangement_text):
                    try:
                        parsed = arrangementTextToObj(location)
                        # 检查是否是指定的星期
                        if parsed["occupyDay"] == dayOfWeek:
                            occupied_times.extend(parsed["occupyTime"])
                    except:
                        pass

        # 去重并排序
        return sorted(list(set(occupied_times)))

    def _calculateFreePeriods(self, occupied_times, start_time, end_time):
        """
        Calculate free periods based on occupied times
        """
        # 创建完整的时间段列表
        all_periods = list(range(start_time, end_time + 1))

        # 移除被占用的时间段
        free_periods_list = [
            period for period in all_periods if period not in occupied_times
        ]

        if not free_periods_list:
            return []

        # 合并连续的时间段
        free_periods = []
        current_start = free_periods_list[0]
        current_end = free_periods_list[0]

        for i in range(1, len(free_periods_list)):
            if free_periods_list[i] == current_end + 1:
                current_end = free_periods_list[i]
            else:
                free_periods.append(
                    {
                        "start": current_start,
                        "end": current_end,
                        "duration": current_end - current_start + 1,
                    }
                )
                current_start = free_periods_list[i]
                current_end = free_periods_list[i]

        # 添加最后一个时间段
        free_periods.append(
            {
                "start": current_start,
                "end": current_end,
                "duration": current_end - current_start + 1,
            }
        )

        return free_periods

    def getAllBuildings(self, campus, calendarId):
        """
        Get all buildings in a specific campus with room grouping
        Updated for NOTE2: Only returns allowed study areas
        Returns a hierarchical structure: building -> rooms
        """
        from study_room_config import (
            CAMPUS_MAPPING,
            CAMPUS_ID_TO_NAME,
            filter_study_area_classrooms,
            get_campus_buildings,
            is_allowed_classroom,
        )

        # 将campus参数转换为校区ID（如果需要）
        campus_id = None
        if campus in CAMPUS_ID_TO_NAME:
            campus_id = campus
        else:
            # 通过名称查找ID
            for cid, cname in CAMPUS_ID_TO_NAME.items():
                if cname == campus:
                    campus_id = cid
                    break

        query = """
        SELECT DISTINCT 
            TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) as full_room_info
        FROM teacher AS t
        JOIN coursedetail AS c ON t.teachingClassId = c.id
        WHERE c.calendarId = %s
        AND c.campus = %s
        AND t.arrangeInfoText IS NOT NULL 
        AND t.arrangeInfoText != ''
        AND TRIM(SUBSTRING_INDEX(t.arrangeInfoText, '] ', -1)) != ''
        ORDER BY full_room_info
        """

        self.cursor.execute(query, (calendarId, campus_id or campus))
        result = self.cursor.fetchall()

        # 调试输出：原始查询结果
        print(
            f"[DEBUG] getAllBuildings for campus '{campus}' (ID: {campus_id}), calendarId {calendarId}"
        )
        print(f"[DEBUG] Raw query returned {len(result)} rooms")

        # 提取教室名称列表
        all_classrooms = []
        for row in result:
            full_room_info = str(row[0]).strip() if row[0] else ""
            if full_room_info and len(full_room_info) <= 50:  # 过滤异常数据
                all_classrooms.append(full_room_info)

        print(f"[DEBUG] After filtering, got {len(all_classrooms)} classrooms")

        # 使用新配置过滤出允许的自习区域教室
        filtered_classrooms = filter_study_area_classrooms(all_classrooms)

        print(
            f"[DEBUG] After study area filtering, got {len(filtered_classrooms)} allowed classrooms"
        )

        # 按楼宇分组
        building_rooms = {}

        for classroom_data in filtered_classrooms:
            classroom_name = classroom_data["classroom_name"]
            building_name = classroom_data["building_name"]
            building_code = classroom_data["building_code"]

            if building_name not in building_rooms:
                building_rooms[building_name] = {
                    "building": building_name,
                    "building_code": building_code,
                    "rooms": set(),  # 使用set避免重复
                    "campus_name": classroom_data["campus_name"],
                }
            building_rooms[building_name]["rooms"].add(classroom_name)

        # 转换为最终格式并排序
        buildings = []
        for building_name, building_info in building_rooms.items():
            rooms_list = sorted(list(building_info["rooms"]))
            # 在每个楼宇的教室列表开头添加"All"选项
            rooms_with_all = ["All"] + rooms_list

            buildings.append(
                {
                    "building": building_name,
                    "building_code": building_info["building_code"],
                    "rooms": rooms_with_all,
                    "roomCount": len(rooms_list),  # 不包括"All"的实际教室数量
                    "campus_name": building_info["campus_name"],
                }
            )

        # 按楼宇名称排序（不再使用优先级）
        buildings.sort(key=lambda x: x["building"])

        # 调试输出：处理后的结果
        print(f"[DEBUG] Final result: {len(buildings)} allowed study buildings:")
        for building in buildings:
            print(
                f"[DEBUG]   {building['building']} ({building['building_code']}): {building['roomCount']} rooms"
            )
            if building["roomCount"] <= 5:  # 如果教室数量少，显示具体教室
                # 跳过"All"
                print(f"[DEBUG]     Rooms: {', '.join(building['rooms'][1:])}")

        return buildings

    def _extractBuildingName(self, raw_building):
        """
        Extract clean building name from raw building string
        Deprecated: Use normalize_building_name from config instead
        """
        from study_room_config import normalize_building_name

        return normalize_building_name(raw_building)

    def _getBuildingPriority(self, building_name):
        """
        Get priority for building (lower number = higher priority for study)
        Deprecated: Use get_building_priority from config instead
        """
        from study_room_config import get_building_priority

        return get_building_priority(building_name)

    def getAllBuildingsWithRooms(self, campus, calendarId):
        """
        Get detailed building and room information for frontend
        Returns: List of buildings with room details
        """
        buildings = self.getAllBuildings(campus, calendarId)

        # 为每个楼宇添加 "All" 选项
        for building in buildings:
            building["rooms"] = ["All"] + building["rooms"]

        return buildings


# debug
if __name__ == "__main__":
    testObject = {
        "calendarId": 119,
        "courseName": "上海",
        "courseCode": "",
        "teacherCode": "",
        "teacherName": "",
        "campus": "",
        "faculty": "",
    }
    with bckndSql() as db:
        print(db.findCourseDetailByCode("124004", 119))
        print(db.findCourseByMajor(2023, "10065", 119))  # ok
        print(db.findGradeByCalendarId(119))
        print(db.findMajorByGrade(2023))
        print(db.findCourseBySearch(testObject))  # ok
        print(db.findCourseDetailByCode("124004", 119))  # ok
        print(db.findCourseByNatureId([955, 956, 957, 958, 947], 119))
        print(db.findOptionalCourseType([955, 956, 957, 958, 947], 119))
        print(len(db.findCourseByTime("星期五", [955, 956, 957, 958, 947], 119)))
