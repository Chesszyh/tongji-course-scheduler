<template>
  <a-config-provider :locale="locale">
    <a-layout class="space-y-4">
      <!-- 所有 layout 放在了组件里, 不要嵌套! -->
      <a-spin :spinning="$store.state.isSpin" :indicator="myIndicator" tip="Loading..." size="large">  
        <MyHeader />
        <MajorInfo @changeMajor="resetSelectedRows" />
        <a-layout class="main-content-layout">
          <a-layout-content class="main-content">
            <div class="flex flex-row space-x-4 h-max m-2">
              <CourseRoughList @openOverview="handleOpen"/>
              <CourseDetailList />
            </div>
            <TimeTable @cellClick="findCourseByTime" />
          </a-layout-content>
          
          <!-- 右侧AI Chat边栏 -->
          <a-layout-sider 
            class="ai-chat-sider" 
            :width="400" 
            theme="light"
            :collapsible="false"
          >
            <AiChatSidebar />
          </a-layout-sider>
        </a-layout>
        <MyFooter />
      </a-spin>
    </a-layout>
    <a-modal
    title="选择课程"
    okText="提交"
    v-model:open="openOverview"
    @ok="stageCourses"
    @cancel="handleCancel"
    style="width: 80%"
      >
      <CourseOverview v-model:selectedRowKeys="selectedRowKeys" />
    </a-modal>

    <a-modal
      title="选修课"
      okText="提交"
      v-model:open="openOptional"
      @ok="stageCourses"
      @cancel="handleCancel"
      style="width: 80%"
    >
      <OptionalCourseTimeOverview v-model:selectedRowKeys="selectedRowKeys" v-model:optionalCourseData="optionalCourseData" />
    </a-modal>
  </a-config-provider>
</template>

<script lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import axios from 'axios';
import { LoadingOutlined } from '@ant-design/icons-vue';
import { h } from 'vue';
import { errorNotify } from './utils/errorNotify';
import { getRowSection } from './utils/timetable';
import { defineAsyncComponent } from 'vue';

dayjs.locale('zh-cn');

export default {
  name: 'App',
  components: {
    MyHeader: defineAsyncComponent(() => import('./components/MyHeader.vue')),
    MyFooter: defineAsyncComponent(() => import('./components/MyFooter.vue')),
    CourseRoughList: defineAsyncComponent(() => import('./components/CourseRoughList.vue')),
    CourseDetailList: defineAsyncComponent(() => import('./components/CourseDetailList.vue')),
    TimeTable: defineAsyncComponent(() => import('./components/TimeTable.vue')),
    MajorInfo: defineAsyncComponent(() => import('./components/MajorInfo.vue')),
    CourseOverview: defineAsyncComponent(() => import('./components/CourseOverview.vue')),
    OptionalCourseTimeOverview: defineAsyncComponent(() => import('./components/OptionalCourseTimeOverview.vue')),
    AiChatSidebar: defineAsyncComponent(() => import('./components/AiChatSidebar.vue')),
    LoadingOutlined
  },
  data() {
    return {
      locale: zhCN,
      selectedRowKeys: [] as string[],
      openOverview: false,
      openOptional: false,
      optionalCourseData: []
    }
  },
  computed: {
    myIndicator() {
      return h(LoadingOutlined, {
        style: {
          fontSize: '24px'
        },
        spin: true
      });
    }
  },
  methods: {
    handleOpen() {
      this.openOverview = true;
      // console.log("openOverview", this.openOverview);
    },
    handleCancel() {
      this.openOverview = false;
      this.selectedRowKeys = []; // 清空一下，不然动画会保持原来的状态
      // console.log("清空！", this.selectedRowKeys);
    },
    handleCancelOptional() {
      this.openOptional = false;
      this.selectedRowKeys = [];
    },
    resetSelectedRows() {
      // console.log("resetSelectedRows");
      this.selectedRowKeys = [];
    },
    async stageCourses() {
      this.openOverview = false;
      this.openOptional = false;
      this.$store.commit("setSpin", true);
      
      // 根据 selectedRowKeys 筛选出对应的课程信息
      for (const key of this.selectedRowKeys) {
        // 根据第一个字符分类
        const type = key[0];

        if (type === '必') {
          // 如果是必修课，则直接在 vuex 的状态里查找
          const _courseCode = key.split('_')[2];

          // 整合一下
          const originalCourse = this.$store.state.commonLists.compulsoryCourses.find(course => course.courseCode === _courseCode);
          
          const _courseObject = {
            courseCode: originalCourse.courseCode,
            courseName: originalCourse.courseName + '(' + originalCourse.courseCode + ')',
            courseNameReserved: originalCourse.courseName,
            credit: originalCourse.credit,
            courseType: "必",
            teacher: [],
            status: 0,
            courseDetail: originalCourse.courses.map((course: any) => ({
              ...course,
              status: 0
            }))
          }


          this.$store.commit("pushStagedCourse", _courseObject);
        }
        else if (type === '选') {
          // 如果是选修课，需要向后端请求
          // console.log('选修课', key);

          const _courseCode = key.split('_')[2];

          try {
            const res = await axios({
              url: '/api/findCourseDetailByCode',
              method: 'post',
              data: {
                courseCode: _courseCode,
                calendarId: this.$store.state.majorSelected.calendarId
              }
            });

            // 需要整合一下数据
            // 思路：先找到包含这个课程的选修课类别，然后再在这个类别中定位到这个课程
            const _roughCourse = this.$store.state.commonLists.optionalCourses
              .find(courseGroup => courseGroup.courses.some((course: { courseCode: string; }) => course.courseCode === _courseCode))
              ?.courses.find((course: { courseCode: string; }) => course.courseCode === _courseCode);
            const _detailCourse = res.data.data;

            const _courseObject = {
              courseCode: _roughCourse.courseCode,
              courseName: _roughCourse.courseName + '(' + _roughCourse.courseCode + ')',
              courseNameReserved: _roughCourse.courseName,
              credit: _roughCourse.credit,
              courseType: "选",
              teacher: [],
              status: 0,
              courseDetail: _detailCourse.map((course: any) => ({
                ...course,
                status: 0
              }))
            }

            // console.log("_courseObject", _courseObject);

            this.$store.commit("pushStagedCourse", _courseObject);
          }
          catch (error: any) {
            // console.log("error:", error);
            errorNotify(error.response.data.msg);
          }
        }
        else if (type === '查') {
          const _courseCode = key.split('_')[1];

          try {
            const res = await axios({
              url: '/api/findCourseDetailByCode',
              method: 'post',
              data: {
                courseCode: _courseCode,
                calendarId: this.$store.state.majorSelected.calendarId
              }
            });

            const _roughCourse = this.$store.state.commonLists.searchCourses
              .find(course => course.courseCode === _courseCode);
            const _detailCourse = res.data.data;

            // 需要整合一下数据
            const _courseObject = {
              courseCode: _roughCourse.courseCode,
              courseName: _roughCourse.courseName + '(' + _roughCourse.courseCode + ')',
              courseNameReserved: _roughCourse.courseName,
              credit: _roughCourse.credit,
              courseType: "查",
              teacher: [],
              status: 0,
              courseDetail: _detailCourse.map((course: any) => ({
                ...course,
                status: 0
              }))
            }

            this.$store.commit("pushStagedCourse", _courseObject);
          }
          catch (error: any) {
            // console.log("error:", error);
            errorNotify(error.response.data.msg);
          }
        }
      }

      // 清空 selectedRowKeys
      this.selectedRowKeys = [];
      this.$store.commit("setSpin", false);
    },
    async findCourseByTime(cell: { day: any; class: number; }) {
      this.$store.commit("setSpin", true);
      console.log("cell", cell);

      try {
        const res = await axios({
          url: '/api/findCourseByTime',
          method: 'post',
          data: {
            calendarId: this.$store.state.majorSelected.calendarId,
            day: cell.day,
            section: getRowSection(cell.class)
          }
        });

        // console.log("res", res.data.data);

        this.optionalCourseData = res.data.data;
        this.openOptional = true;
      }
      catch (error: any) {
        // console.log("error:", error);
        errorNotify(error.response.data.msg);
      }
      finally {
        this.$store.commit("setSpin", false);
      }
    }
  }
}
</script>

<style>
/* 主布局样式 */
.main-content-layout {
  display: flex !important;
  flex-direction: row !important;
}

.main-content {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

/* AI Chat 侧边栏样式 */
.ai-chat-sider {
  background: #ffffff !important;
  border-left: 1px solid #e8e8e8;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.06);
  height: calc(100vh - 200px); /* 根据页面头部高度调整 */
  position: sticky;
  top: 0;
}

.ai-chat-sider .ant-layout-sider-children {
  height: 100%;
  overflow: hidden;
}

/* 确保主要内容区域能够正确缩放 */
.ant-layout {
  min-height: auto;
}

/* 调整课程表的边距，避免与侧边栏重叠 */
.main-content .ant-layout-content {
  padding: 0;
  margin: 0;
}

/* 修复可能的响应式问题 */
@media (max-width: 1400px) {
  .ai-chat-sider {
    width: 350px !important;
    min-width: 350px !important;
  }
}

@media (max-width: 1200px) {
  .ai-chat-sider {
    width: 300px !important;
    min-width: 300px !important;
  }
}
</style>