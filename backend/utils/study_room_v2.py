"""
基于现有 arrangeInfoText 的自习室推荐实现
使用现有的解析工具，避免重复数据存储
"""


def getStudyRoomSuggestions_v2(self, campus, building, dayOfWeek, startTime, endTime, calendarId, specificRoom=None):
    """
    Get study room suggestions based on existing arrangeInfoText parsing
    基于现有的 arrangeInfoText 解析机制实现自习室推荐
    """
    # 导入现有的解析工具和配置
    from .bckndTools import arrangementTextToObj, splitEndline
    from study_room_config import is_valid_study_area, filter_study_area_classrooms

    # 构建校区查询条件
    campus_map = {'四平路校区': '1', '嘉定校区': '3', '沪西校区': '4'}
    campus_code = campus_map.get(campus, '1')

    # 查询该校区的所有课程安排
    base_query = """
    SELECT DISTINCT 
        t.arrangeInfoText,
        cd.courseName,
        t.teacherName
    FROM teacher t 
    JOIN coursedetail cd ON t.teachingClassId = cd.id
    WHERE cd.campus = %s 
    AND cd.calendarId = %s
    AND t.arrangeInfoText IS NOT NULL 
    AND t.arrangeInfoText != ''
    """

    params = [campus_code, calendarId]

    # 如果指定了楼宇，添加模糊查询条件
    if building:
        base_query += " AND t.arrangeInfoText LIKE %s"
        params.append(f"%{building}%")

    # 如果指定了具体教室
    if specificRoom:
        base_query += " AND t.arrangeInfoText LIKE %s"
        params.append(f"%] {specificRoom}%")

    self.cursor.execute(base_query, params)
    results = self.cursor.fetchall()

    # 解析所有排课信息，按教室分组
    classroom_occupancy = {}  # {classroom_name: {day_slot: [course_info]}}

    for arrange_text, course_name, teacher_name in results:
        if not arrange_text:
            continue

        try:
            # 使用现有的解析工具
            for arrangement_line in splitEndline(arrange_text):
                arrangement_info = arrangementTextToObj(arrangement_line)

                room_name = arrangement_info.get('occupyRoom')
                occupy_day = arrangement_info.get('occupyDay')
                occupy_times = arrangement_info.get('occupyTime', [])
                occupy_weeks = arrangement_info.get('occupyWeek', [])

                if room_name and occupy_day and occupy_times:
                    # 确定教室的楼宇信息
                    room_building = extract_building_from_room(room_name)

                    # 检查是否是有效的自习区域
                    if not is_valid_study_area(campus, room_building, room_name):
                        continue

                    # 如果指定了楼宇，进行过滤
                    if building and room_building != building:
                        continue

                    # 初始化教室占用信息
                    if room_name not in classroom_occupancy:
                        classroom_occupancy[room_name] = {
                            'building': room_building,
                            'campus': campus,
                            'occupancy': {}  # {day: {time_slot: course_info}}
                        }

                    # 记录占用信息
                    if occupy_day not in classroom_occupancy[room_name]['occupancy']:
                        classroom_occupancy[room_name]['occupancy'][occupy_day] = {
                        }

                    for time_slot in occupy_times:
                        classroom_occupancy[room_name]['occupancy'][occupy_day][time_slot] = {
                            'course_name': course_name,
                            'teacher_name': teacher_name,
                            'weeks': occupy_weeks
                        }

        except Exception as e:
            # 解析失败的记录跳过
            continue

    # 分析每个教室在指定时间段的空闲情况
    suggestions = []

    for room_name, room_info in classroom_occupancy.items():
        # 分析指定时间段的占用情况
        occupied_slots = set()
        day_occupancy = room_info['occupancy'].get(dayOfWeek, {})

        for time_slot in range(startTime, endTime + 1):
            if time_slot in day_occupancy:
                occupied_slots.add(time_slot)

        # 计算空闲时段
        free_periods = calculate_free_periods(
            startTime, endTime, occupied_slots)

        # 计算可用性分数
        total_requested = endTime - startTime + 1
        total_free = sum(period['duration'] for period in free_periods)
        is_fully_free = total_free == total_requested
        availability_score = total_free / total_requested if total_requested > 0 else 0

        suggestion = {
            'room': room_name,
            'building': room_info['building'],
            'campus': room_info['campus'],
            'freePeriods': free_periods,
            'isFullyFree': is_fully_free,
            'availabilityScore': availability_score
        }

        suggestions.append(suggestion)

    # 应用配置过滤并排序
    suggestions = filter_study_area_classrooms(suggestions)
    suggestions.sort(
        key=lambda x: (-int(x['isFullyFree']), -x['availabilityScore'], x['room']))

    return suggestions


def extract_building_from_room(room_name):
    """从教室名称提取楼宇信息"""
    if not room_name:
        return "未知楼宇"

    # 嘉定校区楼宇
    if room_name.startswith('A'):
        return "安楼"
    elif room_name.startswith('B'):
        return "博楼"
    elif room_name.startswith('G'):
        return "广楼"
    elif room_name.startswith('F'):
        return "复楼"
    # 四平路校区楼宇
    elif room_name.startswith('南'):
        return "南楼"
    elif room_name.startswith('北'):
        return "北楼"
    # 沪西校区楼宇
    elif '沪西二教' in room_name or '二教' in room_name:
        return "二教"
    else:
        return "其他楼宇"


def calculate_free_periods(start_time, end_time, occupied_slots):
    """计算空闲时段"""
    free_periods = []
    current_start = None

    for slot in range(start_time, end_time + 1):
        if slot not in occupied_slots:
            if current_start is None:
                current_start = slot
        else:
            if current_start is not None:
                free_periods.append({
                    'start': current_start,
                    'end': slot - 1,
                    'duration': slot - current_start
                })
                current_start = None

    # 处理最后一个空闲时段
    if current_start is not None:
        free_periods.append({
            'start': current_start,
            'end': end_time,
            'duration': end_time - current_start + 1
        })

    return free_periods
