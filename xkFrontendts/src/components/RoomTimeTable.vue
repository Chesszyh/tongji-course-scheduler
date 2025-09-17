<template>
  <div class="room-timetable">
    <a-card 
      :title="roomInfo.room ? `${roomInfo.room} 教室课表` : '教室课表'"
      :bordered="false"
      class="mb-4"
    >
      <template #extra>
        <a-space>
          <a-tag v-if="roomInfo.room" color="blue">{{ roomInfo.room }}</a-tag>
          <a-button @click="refreshSchedule" :loading="loading" size="small">
            <template #icon>
              <ReloadOutlined />
            </template>
            刷新
          </a-button>
        </a-space>
      </template>

      <a-spin :spinning="loading" tip="正在加载课表...">
        <div v-if="!roomInfo.room" class="empty-state">
          <a-empty description="请先选择教室" />
        </div>
        
        <div v-else class="timetable-container">
          <table class="w-full border-collapse border border-gray-300 table-fixed">
            <thead>
              <tr class="bg-gray-200">
                <th class="border-collapse border border-gray-300 p-1">节次/周次</th>
                <th v-for="day in ['一', '二', '三', '四', '五', '六', '日']" :key="day" class="border-collapse border border-gray-300 p-1">周{{ day }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in timeTable" :key="index" :class="getRowClass(index)">
                <td class="border-collapse border border-gray-300 text-center h-[26px] p-1" :class="index == 11 ? 'text-red-500' : ''">第{{ index + 1 }}节课</td>
                <template v-for="(courses, dayIndex) in row">
                  <td 
                    v-if="!occupied[index][dayIndex]"
                    :key="dayIndex"
                    class="border-collapse border border-gray-300 align-top text-center p-1"
                    :rowspan="maxSpans[index][dayIndex]"
                  >
                    <div v-if="courses.length > 0" class="bg-indigo-700/90 text-white p-1 h-full rounded-b-xs overflow-x-hidden" :style="{ height: (maxSpans[index][dayIndex] * 45) + 'px' }">
                      <div v-for="(course, courseIndex) in courses" :key="course.code" class="text-xs h-full cursor-pointer" :class="{ 'border-b border-dashed border-white pb-1 mb-1': courseIndex !== courses.length - 1 }" @click="showCourseDetail(course)">
                        <div class="course-content">
                          <div class="font-semibold">{{ course.courseName }}</div>
                          <div class="text-xs opacity-90">{{ course.code }}</div>
                          <div v-if="course.teachers && course.teachers.length > 0" class="text-xs opacity-80">
                            {{ course.teachers.map(t => t.teacherName).join(', ') }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </a-spin>
    </a-card>

    <!-- 课程详情抽屉 -->
    <a-drawer
      v-model:open="courseDetailVisible"
      title="课程详情"
      width="500"
      placement="right"
    >
      <div v-if="selectedCourse" class="course-detail">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="课程名称">
            {{ selectedCourse.courseName }}
          </a-descriptions-item>
          <a-descriptions-item label="课程代码">
            {{ selectedCourse.courseCode }}
          </a-descriptions-item>
          <a-descriptions-item label="班级代码">
            {{ selectedCourse.code }}
          </a-descriptions-item>
          <a-descriptions-item label="学分">
            {{ selectedCourse.credit }}
          </a-descriptions-item>
          <a-descriptions-item label="开课学院">
            {{ selectedCourse.faculty }}
          </a-descriptions-item>
          <a-descriptions-item label="校区">
            {{ selectedCourse.campus }}
          </a-descriptions-item>
          <a-descriptions-item label="授课教师">
            <a-space direction="vertical" size="small">
              <a-tag v-for="teacher in selectedCourse.teachers" :key="teacher.teacherCode" color="blue">
                {{ teacher.teacherName }} ({{ teacher.teacherCode }})
              </a-tag>
            </a-space>
          </a-descriptions-item>
          <a-descriptions-item label="上课安排">
            <a-space direction="vertical" size="small">
              <a-tag v-for="arrangement in selectedCourse.arrangementInfo" :key="arrangement.arrangementText" color="green" class="whitespace-normal">
                {{ arrangement.arrangementText }}
              </a-tag>
            </a-space>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { ReloadOutlined } from '@ant-design/icons-vue';
import axios from 'axios';
import { errorNotify } from '@/utils/errorNotify';

interface Teacher {
  teacherCode: string;
  teacherName: string;
}

interface ArrangementInfo {
  arrangementText: string;
  occupyDay: number;
  occupyTime: number[];
  occupyWeek: number[];
  occupyRoom: string;
  teacherAndCode: string;
}

interface Course {
  courseCode: string;
  courseName: string;
  code: string;
  faculty: string;
  credit: number;
  campus: string;
  teachers: Teacher[];
  arrangementInfo: ArrangementInfo[];
}

interface CourseOnTable {
  courseCode: string;
  courseName: string;
  code: string;
  faculty: string;
  credit: number;
  campus: string;
  teachers: Teacher[];
  arrangementInfo: ArrangementInfo[];
  occupyDay: number;
  occupyTime: number[];
  showText: string;
}

export default defineComponent({
  name: 'RoomTimeTable',
  components: {
    ReloadOutlined
  },
  props: {
    roomInfo: {
      type: Object,
      default: () => ({ room: null, calendarId: null })
    }
  },
  data() {
    return {
      loading: false,
      courses: [] as Course[],
      timeTable: Array(12).fill(null).map(() => Array(7).fill(undefined).map(() => [])) as CourseOnTable[][][],
      maxSpans: Array.from({ length: 12 }, () => Array(7).fill(1)),
      occupied: Array.from({ length: 12 }, () => Array(7).fill(false)),
      courseDetailVisible: false,
      selectedCourse: null as Course | null
    };
  },
  watch: {
    roomInfo: {
      handler(newVal) {
        if (newVal.room && newVal.calendarId) {
          this.loadRoomSchedule();
        } else {
          this.clearSchedule();
        }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    async loadRoomSchedule() {
      if (!this.roomInfo.room || !this.roomInfo.calendarId) return;
      
      this.loading = true;
      try {
        const response = await axios.post('/api/getCoursesByRoom', {
          room: this.roomInfo.room,
          calendarId: this.roomInfo.calendarId
        });
        
        this.courses = response.data.data;
        this.updateTimeTable();
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        errorNotify('加载教室课表失败: ' + errorMessage);
      } finally {
        this.loading = false;
      }
    },

    clearSchedule() {
      this.courses = [];
      this.timeTable = Array(12).fill(null).map(() => Array(7).fill(undefined).map(() => []));
      this.maxSpans = Array.from({ length: 12 }, () => Array(7).fill(1));
      this.occupied = Array.from({ length: 12 }, () => Array(7).fill(false));
    },

    updateTimeTable() {
      // 初始化数据结构
      const newTimeTable = Array(12).fill(null).map(() => Array(7).fill(undefined).map(() => [])) as CourseOnTable[][][];
      const newMaxSpans = Array.from({ length: 12 }, () => Array(7).fill(1));
      const newOccupied = Array.from({ length: 12 }, () => Array(7).fill(false));

      // 处理每个课程的所有安排信息
      this.courses.forEach((course: Course) => {
        course.arrangementInfo.forEach((arrangement: ArrangementInfo) => {
          const dayIndex = arrangement.occupyDay - 1; // 转换为0索引
          const timeSlots = arrangement.occupyTime;
          
          if (dayIndex >= 0 && dayIndex < 7 && timeSlots.length > 0) {
            const startRow = timeSlots[0] - 1; // 转换为0索引
            
            if (startRow >= 0 && startRow < 12) {
              // 创建课程显示对象
              const courseOnTable: CourseOnTable = {
                ...course,
                occupyDay: arrangement.occupyDay,
                occupyTime: timeSlots,
                showText: `${course.courseName}\n${course.code}`
              };
              
              newTimeTable[startRow][dayIndex].push(courseOnTable);
            }
          }
        });
      });

      // 计算最大跨度
      for (let row = 0; row < 12; row++) {
        for (let col = 0; col < 7; col++) {
          const courses = newTimeTable[row][col];
          if (courses.length > 0) {
            newMaxSpans[row][col] = Math.max(...courses.map(c => c.occupyTime.length));
          }
        }
      }

      // 标记被占用的单元格
      for (let row = 0; row < 12; row++) {
        for (let col = 0; col < 7; col++) {
          const span = newMaxSpans[row][col];
          if (span > 1) {
            for (let i = 1; i < span; i++) {
              if (row + i < 12) {
                newOccupied[row + i][col] = true;
              }
            }
          }
        }
      }

      // 更新响应式数据
      this.timeTable = newTimeTable;
      this.maxSpans = newMaxSpans;
      this.occupied = newOccupied;
    },

    getRowClass(index: number) {
      if (index === 11) return 'bg-red-50';
      return Math.floor(index / 2) % 2 === 0 ? 'bg-white' : 'bg-gray-50';
    },

    showCourseDetail(course: CourseOnTable) {
      this.selectedCourse = course;
      this.courseDetailVisible = true;
    },

    refreshSchedule() {
      this.loadRoomSchedule();
    }
  }
});
</script>

<style scoped>
.room-timetable {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.timetable-container {
  width: 100%;
  overflow-x: auto;
}

.course-content {
  word-wrap: break-word;
  word-break: break-all;
  line-height: 1.2;
}

.course-content .font-semibold {
  font-weight: 600;
  margin-bottom: 2px;
}

.whitespace-normal {
  white-space: normal !important;
  word-wrap: break-word;
}

/* 调整表格样式使其更紧凑 */
table {
  min-width: 800px;
}

td, th {
  vertical-align: top;
  min-height: 45px;
}

/* 课程卡片悬停效果 */
.text-xs.cursor-pointer:hover {
  opacity: 0.8;
  transform: scale(1.02);
  transition: all 0.2s ease;
}

/* 滚动条样式 */
.timetable-container::-webkit-scrollbar {
  height: 8px;
}

.timetable-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.timetable-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.timetable-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>