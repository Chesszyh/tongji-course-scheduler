CREATE DATABASE IF NOT EXISTS tongji_course;
USE tongji_course;

-- 课程性质表
CREATE TABLE IF NOT EXISTS `coursenature` (
  `courseLabelId` INT NOT NULL,
  `courseLabelName` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`courseLabelId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 校区表
CREATE TABLE IF NOT EXISTS `campus` (
  `campus` VARCHAR(255) NOT NULL,
  `campusI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`campus`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 学院表
CREATE TABLE IF NOT EXISTS `faculty` (
  `faculty` VARCHAR(255) NOT NULL,
  `facultyI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`faculty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 学期表
CREATE TABLE IF NOT EXISTS `calendar` (
  `calendarId` INT NOT NULL,
  `calendarIdI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`calendarId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 授课语言表
CREATE TABLE IF NOT EXISTS `language` (
  `teachingLanguage` VARCHAR(255) NOT NULL,
  `teachingLanguageI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`teachingLanguage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 考核方式表
CREATE TABLE IF NOT EXISTS `assessment` (
  `assessmentMode` VARCHAR(255) NOT NULL,
  `assessmentModeI18n` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`assessmentMode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 专业表
CREATE TABLE IF NOT EXISTS `major` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(255) DEFAULT NULL,
  `grade` INT DEFAULT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 课程详情表
CREATE TABLE IF NOT EXISTS `coursedetail` (
  `id` BIGINT NOT NULL,
  `code` VARCHAR(255) DEFAULT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  `courseLabelId` INT DEFAULT NULL,
  `assessmentMode` VARCHAR(255) DEFAULT NULL,
  `period` INT DEFAULT NULL,
  `weekHour` INT DEFAULT NULL,
  `campus` VARCHAR(255) DEFAULT NULL,
  `number` INT DEFAULT NULL,
  `elcNumber` INT DEFAULT NULL,
  `startWeek` INT DEFAULT NULL,
  `endWeek` INT DEFAULT NULL,
  `courseCode` VARCHAR(255) DEFAULT NULL,
  `courseName` VARCHAR(255) DEFAULT NULL,
  `credit` DOUBLE DEFAULT NULL,
  `teachingLanguage` VARCHAR(255) DEFAULT NULL,
  `faculty` VARCHAR(255) DEFAULT NULL,
  `calendarId` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `courseCode` (`courseCode`),
  KEY `nature_idx` (`courseLabelId`),  
  KEY `assess_idx` (`assessmentMode`),  
  KEY `campusKey_idx` (`campus`),  
  KEY `facultyKey_idx` (`faculty`),  
  KEY `calendarKey_idx` (`calendarId`),  
  KEY `langKey_idx` (`teachingLanguage`),  

  CONSTRAINT `coursedetail_ibfk_1` FOREIGN KEY (`courseLabelId`) REFERENCES `coursenature` (`courseLabelId`),
  CONSTRAINT `coursedetail_ibfk_2` FOREIGN KEY (`campus`) REFERENCES `campus` (`campus`),
  CONSTRAINT `coursedetail_ibfk_3` FOREIGN KEY (`faculty`) REFERENCES `faculty` (`faculty`),
  CONSTRAINT `coursedetail_ibfk_4` FOREIGN KEY (`calendarId`) REFERENCES `calendar` (`calendarId`),
  CONSTRAINT `coursedetail_ibfk_5` FOREIGN KEY (`teachingLanguage`) REFERENCES `language` (`teachingLanguage`),
  CONSTRAINT `coursedetail_ibfk_6` FOREIGN KEY (`assessmentMode`) REFERENCES `assessment` (`assessmentMode`),

  CONSTRAINT `natureKey` FOREIGN KEY (`courseLabelId`) REFERENCES `coursenature` (`courseLabelId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `campusKey` FOREIGN KEY (`campus`) REFERENCES `campus` (`campus`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `facultyKey` FOREIGN KEY (`faculty`) REFERENCES `faculty` (`faculty`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `calendarKey` FOREIGN KEY (`calendarId`) REFERENCES `calendar` (`calendarId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `langKey` FOREIGN KEY (`teachingLanguage`) REFERENCES `language` (`teachingLanguage`),
  CONSTRAINT `assessKey` FOREIGN KEY (`assessmentMode`) REFERENCES `assessment` (`assessmentMode`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 教师表
CREATE TABLE IF NOT EXISTS `teacher` (
  `id` BIGINT NOT NULL,
  `teachingClassId` BIGINT DEFAULT NULL,
  `teacherCode` VARCHAR(255) DEFAULT NULL,
  `teacherName` VARCHAR(255) DEFAULT NULL,
  `arrangeInfoText` MEDIUMTEXT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teachingClassId` (`teachingClassId`),
  CONSTRAINT `teacher_ibfk_1` FOREIGN KEY (`teachingClassId`) REFERENCES `coursedetail` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 专业与课程关联表
CREATE TABLE IF NOT EXISTS `majorandcourse` (
  `id` INT NOT NULL AUTO_INCREMENT,  
  `majorId` INT NOT NULL,
  `courseId` BIGINT NOT NULL,
  PRIMARY KEY (`id`),  
    KEY `courseKey_idx` (`courseId`),  
    KEY `majorKeyForMajor_idx` (`majorId`),  
    CONSTRAINT `courseKeyForMajor` FOREIGN KEY (`courseId`) REFERENCES `coursedetail` (`id`),  
    CONSTRAINT `majorKeyForMajor` FOREIGN KEY (`majorId`) REFERENCES `major` (`id`),
  CONSTRAINT `majorandcourse_ibfk_1` FOREIGN KEY (`majorId`) REFERENCES `major` (`id`),
  CONSTRAINT `majorandcourse_ibfk_2` FOREIGN KEY (`courseId`) REFERENCES `coursedetail` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 抓取日志表
CREATE TABLE IF NOT EXISTS `fetchlog` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fetchTime` DATETIME DEFAULT NULL,
  `msg` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 教室信息表(新增，用于自习室推荐功能)
CREATE TABLE IF NOT EXISTS `classroom_info` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `classroom_name` VARCHAR(150) NOT NULL COMMENT '教室名称，如A101, 南208等',
    `building` VARCHAR(20) NOT NULL COMMENT '楼宇名称，如安楼、南楼等',
    `campus` VARCHAR(50) NOT NULL COMMENT '校区名称',
    `course_schedule` TEXT DEFAULT NULL COMMENT '课程安排，格式：星期(节数1,节数2)[周次],如：1(5-6,9-11)[1-16],2(1-4)[2-16双],3(7-8)[3-7]',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_classroom` (`classroom_name`),
    KEY `idx_building` (`building`),
    KEY `idx_campus` (`campus`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 教室课表详细时间段表(新增)，存储每个教室每个时间段的占用情况
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

