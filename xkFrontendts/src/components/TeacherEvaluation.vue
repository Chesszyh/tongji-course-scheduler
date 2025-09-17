<template>
  <div class="teacher-evaluation">
    <div class="section-title flex items-center gap-2 mb-3">
      <UserOutlined />
      <span class="font-medium text-gray-700">教师评价</span>
    </div>
    
    <!-- 当前选中课程信息 -->
    <div v-if="selectedCourse && selectedCourse.courseCode" class="current-course mb-3">
      <div class="course-info bg-blue-50 p-3 rounded-lg">
        <div class="course-name font-medium text-blue-900">
          {{ selectedCourse.courseName || '未知课程' }}
        </div>
        <div class="course-code text-sm text-blue-600">
          课程代码: {{ selectedCourse.courseCode }}
        </div>
      </div>
    </div>
    
    <!-- 教师评价列表 -->
    <div v-if="teacherEvaluations.length > 0" class="evaluations-list">
      <div 
        v-for="evaluation in teacherEvaluations" 
        :key="evaluation.teacherId"
        class="evaluation-card mb-3 p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
      >
        <div class="teacher-info mb-2">
          <div class="teacher-name font-medium text-gray-800">
            {{ evaluation.teacherName }}
          </div>
          <div class="teacher-code text-xs text-gray-500">
            {{ evaluation.teacherCode }}
          </div>
        </div>
        
        <div class="rating-info mb-2">
          <div class="flex items-center gap-2">
            <a-rate 
              :value="evaluation.rating" 
              :disabled="true"
              :allowHalf="true"
              class="text-sm"
            />
            <span class="text-sm text-gray-600">
              {{ evaluation.rating.toFixed(1) }}
            </span>
          </div>
          <div class="text-xs text-gray-500">
            基于 {{ evaluation.reviewCount }} 条评价
          </div>
        </div>
        
        <div v-if="evaluation.latestComment" class="latest-comment">
          <div class="text-xs text-gray-500 mb-1">最新评价：</div>
          <div class="text-sm text-gray-700 p-2 bg-gray-50 rounded italic">
            "{{ evaluation.latestComment }}"
          </div>
        </div>
        
        <div class="evaluation-link mt-2">
          <a 
            :href="evaluation.wulongchaUrl" 
            target="_blank"
            class="text-xs text-blue-500 hover:text-blue-700"
          >
            在乌龙茶查看详情 →
          </a>
        </div>
      </div>
    </div>
    
    <!-- 无评价数据时的显示 -->
    <div v-else-if="selectedCourse && selectedCourse.courseCode" class="no-evaluation">
      <a-empty 
        :image="simpleImage" 
        description="暂无教师评价数据"
        class="py-6"
      >
        <template #description>
          <span class="text-gray-500 text-sm">
            该课程的教师评价数据暂未收录
          </span>
        </template>
      </a-empty>
    </div>
    
    <!-- 未选择课程时的显示 -->
    <div v-else class="no-selection">
      <a-empty 
        :image="simpleImage"
        description="请选择课程查看教师评价"
        class="py-6"
      >
        <template #description>
          <span class="text-gray-500 text-sm">
            点击左侧课程可查看相关教师评价
          </span>
        </template>
      </a-empty>
    </div>
    
    <!-- 数据来源说明 -->
    <div class="data-source mt-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
      <InfoCircleOutlined class="mr-1" />
      数据来源：同济大学乌龙茶教师评价平台 (1.tongji.icu)
    </div>
  </div>
</template>

<script lang="ts">
import { UserOutlined, InfoCircleOutlined } from '@ant-design/icons-vue';
import { Empty } from 'ant-design-vue';

export default {
  name: 'TeacherEvaluation',
  components: {
    UserOutlined,
    InfoCircleOutlined
  },
  props: {
    selectedCourse: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      teacherEvaluations: [] as {
        teacherId: string;
        teacherName: string;
        teacherCode: string;
        rating: number;
        reviewCount: number;
        latestComment: string;
        wulongchaUrl: string;
      }[],
      loading: false,
      simpleImage: Empty.PRESENTED_IMAGE_SIMPLE
    }
  },
  watch: {
    'selectedCourse.courseCode': {
      handler(newCourseCode) {
        if (newCourseCode) {
          this.fetchTeacherEvaluations(newCourseCode);
        } else {
          this.teacherEvaluations = [];
        }
      },
      immediate: true
    }
  },
  methods: {
    async fetchTeacherEvaluations(courseCode: string) {
      this.loading = true;
      try {
        // TODO: 这里将来需要调用实际的API来获取乌龙茶数据
        // 目前使用模拟数据
        await this.mockFetchEvaluations(courseCode);
      } catch (error) {
        console.error('获取教师评价失败:', error);
        this.teacherEvaluations = [];
      } finally {
        this.loading = false;
      }
    },
    
    async mockFetchEvaluations(_courseCode: string) {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 模拟数据 - 将来替换为真实的乌龙茶API调用
      // 使用courseCode参数来决定是否返回数据
      const shouldReturnData = _courseCode && Math.random() > 0.3;
      const mockEvaluations = [
        {
          teacherId: '001',
          teacherName: '张教授',
          teacherCode: 'T001',
          rating: 4.5,
          reviewCount: 23,
          latestComment: '讲课很清晰，作业量适中，推荐选择。',
          wulongchaUrl: 'https://1.tongji.icu/teacher/001'
        },
        {
          teacherId: '002', 
          teacherName: '李老师',
          teacherCode: 'T002',
          rating: 3.8,
          reviewCount: 15,
          latestComment: '课程内容丰富，但进度较快，需要跟上。',
          wulongchaUrl: 'https://1.tongji.icu/teacher/002'
        }
      ];
      
      // 随机决定是否返回数据（模拟某些课程没有评价数据的情况）
      this.teacherEvaluations = shouldReturnData ? mockEvaluations : [];
    }
  }
}
</script>

<style scoped>
.teacher-evaluation {
  font-size: 14px;
}

.section-title {
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.evaluation-card {
  transition: all 0.2s ease;
}

.evaluation-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.rating-info .ant-rate {
  font-size: 12px;
}

.latest-comment {
  line-height: 1.4;
}

.data-source {
  font-style: italic;
}
</style>