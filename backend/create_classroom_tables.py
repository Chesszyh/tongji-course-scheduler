#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建教室课表数据库表结构
基于数据分析结果设计新的SQL表结构用于存储预处理的教室课表数据
"""

import sys
import os
import mysql.connector
import configparser

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 读取配置文件
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini", encoding="utf-8")

# 设置数据库连接
DB_HOST = CONFIG["Sql"]["host"]
DB_USER = CONFIG["Sql"]["w_user"]  # 可写用户
DB_PASSWORD = CONFIG["Sql"]["w_password"]
DB_DATABASE = CONFIG["Sql"]["database"]
DB_PORT = int(CONFIG["Sql"]["port"])
DB_CHARSET = CONFIG["Sql"]["charset"]


def create_classroom_schedule_tables():
    """
    创建教室课表相关的数据库表
    """
    print("=" * 60)
    print("开始创建教室课表数据库表...")
    print("=" * 60)

    # 连接数据库
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            port=DB_PORT,
            charset=DB_CHARSET,
        )
        cursor = db.cursor()

        # 1. 创建教室基础信息表
        print("1. 创建教室基础信息表 (classroom_info)...")
        classroom_info_ddl = """
        CREATE TABLE IF NOT EXISTS `classroom_info` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `classroom_name` VARCHAR(50) NOT NULL COMMENT '教室名称，如A101, 南208等',
          `building` VARCHAR(20) NOT NULL COMMENT '楼宇名称，如安楼、南楼等',
          `building_code` VARCHAR(10) NOT NULL COMMENT '楼宇代码，如A、南、沪西二教等',
          `campus` VARCHAR(50) NOT NULL COMMENT '校区名称',
          `floor` INT DEFAULT NULL COMMENT '楼层',
          `room_number` VARCHAR(10) DEFAULT NULL COMMENT '房间号码部分',
          `is_study_area` BOOLEAN DEFAULT FALSE COMMENT '是否为允许的自习区域',
          `capacity` INT DEFAULT NULL COMMENT '教室容量（如果有的话）',
          `room_type` VARCHAR(20) DEFAULT NULL COMMENT '教室类型，如普通教室、阶梯教室等',
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_classroom` (`classroom_name`),
          KEY `idx_building` (`building`),
          KEY `idx_campus` (`campus`),
          KEY `idx_study_area` (`is_study_area`),
          KEY `idx_building_code` (`building_code`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
        COMMENT='教室基础信息表，存储所有教室的详细信息';
        """

        cursor.execute(classroom_info_ddl)
        print("   ✓ classroom_info 表创建成功")

        # 2. 创建教室课表时间段表
        print("2. 创建教室课表时间段表 (classroom_schedule)...")
        classroom_schedule_ddl = """
        CREATE TABLE IF NOT EXISTS `classroom_schedule` (
          `id` BIGINT NOT NULL AUTO_INCREMENT,
          `classroom_id` INT NOT NULL COMMENT '教室ID，关联classroom_info表',
          `calendar_id` INT NOT NULL COMMENT '学期ID，关联calendar表',
          `day_of_week` TINYINT NOT NULL COMMENT '星期几，1=周一，7=周日',
          `time_slot` TINYINT NOT NULL COMMENT '时间段，1-12表示第1-12节课',
          `week_start` TINYINT DEFAULT NULL COMMENT '开始周次',
          `week_end` TINYINT DEFAULT NULL COMMENT '结束周次',
          `course_id` BIGINT DEFAULT NULL COMMENT '课程ID，关联coursedetail表',
          `course_name` VARCHAR(255) DEFAULT NULL COMMENT '课程名称',
          `teacher_name` VARCHAR(100) DEFAULT NULL COMMENT '教师名称',
          `is_occupied` BOOLEAN DEFAULT TRUE COMMENT '是否被占用',
          `occupation_type` VARCHAR(20) DEFAULT 'course' COMMENT '占用类型：course=课程，exam=考试，maintenance=维护等',
          `notes` TEXT DEFAULT NULL COMMENT '备注信息',
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_schedule` (`classroom_id`, `calendar_id`, `day_of_week`, `time_slot`, `week_start`, `week_end`),
          KEY `idx_classroom_calendar` (`classroom_id`, `calendar_id`),
          KEY `idx_time_query` (`calendar_id`, `day_of_week`, `time_slot`),
          KEY `idx_week_range` (`week_start`, `week_end`),
          KEY `idx_course` (`course_id`),
          CONSTRAINT `fk_classroom_schedule_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classroom_info` (`id`) ON DELETE CASCADE,
          CONSTRAINT `fk_classroom_schedule_calendar` FOREIGN KEY (`calendar_id`) REFERENCES `calendar` (`calendarId`) ON DELETE CASCADE,
          CONSTRAINT `fk_classroom_schedule_course` FOREIGN KEY (`course_id`) REFERENCES `coursedetail` (`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
        COMMENT='教室课表详细时间段表，存储每个教室每个时间段的占用情况';
        """

        cursor.execute(classroom_schedule_ddl)
        print("   ✓ classroom_schedule 表创建成功")

        # 3. 创建楼宇汇总表（可选，用于快速查询）
        print("3. 创建楼宇汇总表 (building_summary)...")
        building_summary_ddl = """
        CREATE TABLE IF NOT EXISTS `building_summary` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `building` VARCHAR(20) NOT NULL COMMENT '楼宇名称',
          `building_code` VARCHAR(10) NOT NULL COMMENT '楼宇代码',
          `campus` VARCHAR(50) NOT NULL COMMENT '校区名称',
          `total_classrooms` INT DEFAULT 0 COMMENT '总教室数量',
          `study_area_classrooms` INT DEFAULT 0 COMMENT '自习区域教室数量',
          `is_study_building` BOOLEAN DEFAULT FALSE COMMENT '是否为自习楼宇',
          `display_order` INT DEFAULT 0 COMMENT '显示顺序',
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_building` (`building`, `campus`),
          KEY `idx_campus` (`campus`),
          KEY `idx_study_building` (`is_study_building`),
          KEY `idx_display_order` (`display_order`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
        COMMENT='楼宇汇总信息表，用于快速查询楼宇统计信息';
        """

        cursor.execute(building_summary_ddl)
        print("   ✓ building_summary 表创建成功")

        # 4. 创建视图用于快速查询空闲教室
        print("4. 创建空闲教室查询视图...")
        free_classroom_view = """
        CREATE OR REPLACE VIEW `v_free_classrooms` AS
        SELECT 
            ci.id as classroom_id,
            ci.classroom_name,
            ci.building,
            ci.building_code,
            ci.campus,
            cs.calendar_id,
            cs.day_of_week,
            cs.time_slot,
            cs.week_start,
            cs.week_end,
            CASE WHEN cs.id IS NULL THEN TRUE ELSE NOT cs.is_occupied END as is_free
        FROM classroom_info ci
        CROSS JOIN calendar cal
        CROSS JOIN (SELECT 1 as day_of_week UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7) days
        CROSS JOIN (SELECT 1 as time_slot UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 
                   UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12) times
        LEFT JOIN classroom_schedule cs ON ci.id = cs.classroom_id 
            AND cal.calendarId = cs.calendar_id 
            AND days.day_of_week = cs.day_of_week 
            AND times.time_slot = cs.time_slot
        WHERE ci.is_study_area = TRUE;
        """

        cursor.execute(free_classroom_view)
        print("   ✓ v_free_classrooms 视图创建成功")

        # 5. 创建更新时间戳的触发器
        print("5. 创建数据同步触发器...")

        # 教室信息更新触发器
        trigger_classroom_info = """
        CREATE TRIGGER IF NOT EXISTS `tr_classroom_info_update`
        AFTER UPDATE ON `classroom_info`
        FOR EACH ROW
        BEGIN
            UPDATE building_summary 
            SET total_classrooms = (
                SELECT COUNT(*) FROM classroom_info 
                WHERE building = NEW.building AND campus = NEW.campus
            ),
            study_area_classrooms = (
                SELECT COUNT(*) FROM classroom_info 
                WHERE building = NEW.building AND campus = NEW.campus AND is_study_area = TRUE
            ),
            updated_at = CURRENT_TIMESTAMP
            WHERE building = NEW.building AND campus = NEW.campus;
        END
        """

        try:
            cursor.execute(trigger_classroom_info)
            print("   ✓ 教室信息更新触发器创建成功")
        except mysql.connector.Error as e:
            print(f"   ⚠ 触发器创建可能失败: {e}")

        # 提交所有更改
        db.commit()
        print("\n" + "=" * 60)
        print("所有表和视图创建完成！")
        print("=" * 60)

        # 显示表结构信息
        print("\n创建的表结构摘要:")
        tables_info = [
            ("classroom_info", "教室基础信息表", "存储所有教室的详细信息"),
            ("classroom_schedule", "教室课表时间段表", "存储每个教室每个时间段的占用情况"),
            ("building_summary", "楼宇汇总表", "楼宇统计信息，用于快速查询"),
            ("v_free_classrooms", "空闲教室查询视图", "用于快速查询指定时间的空闲教室")
        ]

        for table_name, display_name, description in tables_info:
            print(f"  • {display_name} ({table_name}): {description}")

        return True

    except mysql.connector.Error as e:
        print(f"数据库操作失败: {e}")
        return False

    except Exception as e:
        print(f"创建表结构时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    success = create_classroom_schedule_tables()
    if success:
        print("\n✅ 数据库表结构创建成功！")
        print("\n下一步:")
        print("1. 运行数据预处理脚本填充教室基础信息")
        print("2. 运行课表数据导入脚本")
        print("3. 更新API接口使用新的表结构")
    else:
        print("\n❌ 数据库表结构创建失败！")
        print("请检查数据库连接和权限设置")
