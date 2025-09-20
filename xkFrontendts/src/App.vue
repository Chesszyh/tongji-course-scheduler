<template>
  <a-config-provider :locale="locale">
    <a-layout class="space-y-4">
      <!-- 所有 layout 放在了组件里, 不要嵌套! -->
      <a-spin
        :spinning="$store.state.isSpin"
        :indicator="myIndicator"
        tip="Loading..."
        size="large"
      >
        <MyHeader @menu-change="onMenuChange" />

        <!-- 个人课表视图 -->
        <template v-if="currentView === 'schedule'">
          <MajorInfo @changeMajor="resetSelectedRows" />
          <a-layout class="main-content-layout">
            <a-layout-content class="main-content">
              <div class="flex flex-row space-x-4 h-max m-2">
                <CourseRoughList @openOverview="handleOpen" />
                <CourseDetailList />
              </div>
              <TimeTable @cellClick="findCourseByTime" />
            </a-layout-content>

            <!-- 右侧AI Chat边栏 -->
            <a-layout-sider
              v-model:collapsed="aiSidebarCollapsed"
              class="ai-chat-sider"
              :width="aiSidebarWidth"
              :collapsed-width="0"
              theme="light"
              :collapsible="true"
              :trigger="null"
              :breakpoint="breakpoint"
              @breakpoint="onBreakpoint"
            >
              <AiChatSidebar v-if="!aiSidebarCollapsed" />
            </a-layout-sider>
          </a-layout>

          <!-- AI侧边栏切换按钮 -->
          <a-button
            class="ai-sidebar-toggle"
            :class="{ 'sidebar-open': !aiSidebarCollapsed }"
            type="primary"
            @click="toggleAiSidebar"
            :title="aiSidebarCollapsed ? '显示AI助手' : '隐藏AI助手'"
          >
            <RobotOutlined v-if="aiSidebarCollapsed" />
            <CloseOutlined v-else />
            <span v-if="!aiSidebarCollapsed" class="ml-1">AI</span>
          </a-button>
        </template>

        <!-- 教室课表视图 -->
        <template v-else-if="currentView === 'classroom'">
          <ClassroomSchedulePage />
        </template>

        <MyFooter />
      </a-spin>
    </a-layout>

    <!-- 选课相关弹窗 -->
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
      <OptionalCourseTimeOverview
        v-model:selectedRowKeys="selectedRowKeys"
        v-model:optionalCourseData="optionalCourseData"
      />
    </a-modal>
  </a-config-provider>
</template>

<script lang="ts">
import zhCN from "ant-design-vue/es/locale/zh_CN";
import dayjs from "dayjs";
import "dayjs/locale/zh-cn";
import axios from "axios";
import { LoadingOutlined, RobotOutlined, CloseOutlined } from "@ant-design/icons-vue";
import { h } from "vue";
import { errorNotify } from "./utils/errorNotify";
import { getRowSection } from "./utils/timetable";
import { defineAsyncComponent } from "vue";

dayjs.locale("zh-cn");

export default {
  name: "App",
  components: {
    MyHeader: defineAsyncComponent(() => import("./components/MyHeader.vue")),
    MyFooter: defineAsyncComponent(() => import("./components/MyFooter.vue")),
    CourseRoughList: defineAsyncComponent(() => import("./components/CourseRoughList.vue")),
    CourseDetailList: defineAsyncComponent(() => import("./components/CourseDetailList.vue")),
    TimeTable: defineAsyncComponent(() => import("./components/TimeTable.vue")),
    MajorInfo: defineAsyncComponent(() => import("./components/MajorInfo.vue")),
    CourseOverview: defineAsyncComponent(() => import("./components/CourseOverview.vue")),
    OptionalCourseTimeOverview: defineAsyncComponent(
      () => import("./components/OptionalCourseTimeOverview.vue"),
    ),
    AiChatSidebar: defineAsyncComponent(() => import("./components/AiChatSidebar.vue")),
    ClassroomSchedulePage: defineAsyncComponent(
      () => import("./components/ClassroomSchedulePage.vue"),
    ),
    LoadingOutlined,
    RobotOutlined,
    CloseOutlined,
  },
  data() {
    return {
      locale: zhCN,
      selectedRowKeys: [] as string[],
      openOverview: false,
      openOptional: false,
      optionalCourseData: [],
      // AI侧边栏相关
      aiSidebarCollapsed: false,
      aiSidebarWidth: 400,
      breakpoint: "lg" as const,
      // 当前视图
      currentView: "schedule" as "schedule" | "classroom",
    };
  },
  computed: {
    myIndicator() {
      return h(LoadingOutlined, {
        style: {
          fontSize: "24px",
        },
        spin: true,
      });
    },
  },
  methods: {
    // 视图切换方法
    onMenuChange(view: string) {
      this.currentView = view as "schedule" | "classroom";
    },

    // AI侧边栏控制方法
    toggleAiSidebar() {
      this.aiSidebarCollapsed = !this.aiSidebarCollapsed;
    },

    onBreakpoint(broken: boolean) {
      if (broken) {
        this.aiSidebarWidth = 300;
      } else {
        this.aiSidebarWidth = 400;
      }
    },
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

        if (type === "必") {
          // 如果是必修课，则直接在 vuex 的状态里查找
          const _courseCode = key.split("_")[2];

          // 整合一下
          const originalCourse = this.$store.state.commonLists.compulsoryCourses.find(
            (course) => course.courseCode === _courseCode,
          );

          const _courseObject = {
            courseCode: originalCourse.courseCode,
            courseName: originalCourse.courseName + "(" + originalCourse.courseCode + ")",
            courseNameReserved: originalCourse.courseName,
            credit: originalCourse.credit,
            courseType: "必",
            teacher: [],
            status: 0,
            courseDetail: originalCourse.courses.map((course: any) => ({
              ...course,
              status: 0,
            })),
          };

          this.$store.commit("pushStagedCourse", _courseObject);
        } else if (type === "选") {
          // 如果是选修课，需要向后端请求
          // console.log('选修课', key);

          const _courseCode = key.split("_")[2];

          try {
            const res = await axios({
              url: "/api/findCourseDetailByCode",
              method: "post",
              data: {
                courseCode: _courseCode,
                calendarId: this.$store.state.majorSelected.calendarId,
              },
            });

            // 需要整合一下数据
            // 思路：先找到包含这个课程的选修课类别，然后再在这个类别中定位到这个课程
            const _roughCourse = this.$store.state.commonLists.optionalCourses
              .find((courseGroup) =>
                courseGroup.courses.some(
                  (course: { courseCode: string }) => course.courseCode === _courseCode,
                ),
              )
              ?.courses.find((course: { courseCode: string }) => course.courseCode === _courseCode);
            const _detailCourse = res.data.data;

            const _courseObject = {
              courseCode: _roughCourse.courseCode,
              courseName: _roughCourse.courseName + "(" + _roughCourse.courseCode + ")",
              courseNameReserved: _roughCourse.courseName,
              credit: _roughCourse.credit,
              courseType: "选",
              teacher: [],
              status: 0,
              courseDetail: _detailCourse.map((course: any) => ({
                ...course,
                status: 0,
              })),
            };

            // console.log("_courseObject", _courseObject);

            this.$store.commit("pushStagedCourse", _courseObject);
          } catch (error: any) {
            // console.log("error:", error);
            errorNotify(error.response.data.msg);
          }
        } else if (type === "查") {
          const _courseCode = key.split("_")[1];

          try {
            const res = await axios({
              url: "/api/findCourseDetailByCode",
              method: "post",
              data: {
                courseCode: _courseCode,
                calendarId: this.$store.state.majorSelected.calendarId,
              },
            });

            const _roughCourse = this.$store.state.commonLists.searchCourses.find(
              (course) => course.courseCode === _courseCode,
            );
            const _detailCourse = res.data.data;

            // 需要整合一下数据
            const _courseObject = {
              courseCode: _roughCourse.courseCode,
              courseName: _roughCourse.courseName + "(" + _roughCourse.courseCode + ")",
              courseNameReserved: _roughCourse.courseName,
              credit: _roughCourse.credit,
              courseType: "查",
              teacher: [],
              status: 0,
              courseDetail: _detailCourse.map((course: any) => ({
                ...course,
                status: 0,
              })),
            };

            this.$store.commit("pushStagedCourse", _courseObject);
          } catch (error: any) {
            // console.log("error:", error);
            errorNotify(error.response.data.msg);
          }
        }
      }

      // 清空 selectedRowKeys
      this.selectedRowKeys = [];
      this.$store.commit("setSpin", false);
    },
    async findCourseByTime(cell: { day: any; class: number }) {
      this.$store.commit("setSpin", true);
      console.log("cell", cell);

      try {
        const res = await axios({
          url: "/api/findCourseByTime",
          method: "post",
          data: {
            calendarId: this.$store.state.majorSelected.calendarId,
            day: cell.day,
            section: getRowSection(cell.class),
          },
        });

        // console.log("res", res.data.data);

        this.optionalCourseData = res.data.data;
        this.openOptional = true;
      } catch (error: any) {
        // console.log("error:", error);
        errorNotify(error.response.data.msg);
      } finally {
        this.$store.commit("setSpin", false);
      }
    },
  },
};
</script>

<style>
/* 主布局样式 */
.main-content-layout {
  display: flex !important;
  flex-direction: row !important;
  position: relative;
}

.main-content {
  flex: 1;
  overflow: hidden;
  padding: 0;
  transition: margin-right 0.3s ease;
}

/* AI Chat 侧边栏样式 */
.ai-chat-sider {
  background: #ffffff !important;
  border-left: 1px solid #e8e8e8;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.06);
  height: calc(100vh - 200px);
  position: sticky;
  top: 0;
  z-index: 10;
  transition: all 0.3s ease;
}

.ai-chat-sider .ant-layout-sider-children {
  height: 100%;
  overflow: hidden;
}

/* AI侧边栏切换按钮 */
.ai-sidebar-toggle {
  position: fixed;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  z-index: 1000;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  overflow: hidden;
}

.ai-sidebar-toggle.sidebar-open {
  border-radius: 8px;
  width: auto;
  padding: 0 16px;
  min-width: 72px;
}

.ai-sidebar-toggle:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.ai-sidebar-toggle .anticon {
  font-size: 18px;
  transition: all 0.3s ease;
}

.ai-sidebar-toggle .ml-1 {
  margin-left: 8px;
  font-size: 14px;
  font-weight: 500;
}

/* 当侧边栏展开时，调整按钮位置 */
.ai-sidebar-toggle.sidebar-open {
  right: 420px;
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

/* 响应式设计 */
@media (max-width: 1600px) {
  .ai-chat-sider {
    width: 350px !important;
    min-width: 350px !important;
  }
  .ai-sidebar-toggle.sidebar-open {
    right: 370px;
  }
}

@media (max-width: 1400px) {
  .ai-chat-sider {
    width: 320px !important;
    min-width: 320px !important;
  }
  .ai-sidebar-toggle.sidebar-open {
    right: 340px;
  }
}

@media (max-width: 1200px) {
  .ai-chat-sider {
    width: 300px !important;
    min-width: 300px !important;
  }
  .ai-sidebar-toggle.sidebar-open {
    right: 320px;
  }

  .ai-sidebar-toggle {
    width: 48px;
    height: 48px;
    right: 15px;
  }
}

@media (max-width: 768px) {
  .ai-chat-sider {
    position: fixed !important;
    right: 0;
    top: 0;
    height: 100vh !important;
    z-index: 1001;
    width: 90vw !important;
    min-width: 90vw !important;
  }

  .ai-sidebar-toggle {
    right: 10px;
    width: 44px;
    height: 44px;
  }
}

/* 侧边栏动画效果 */
.ai-chat-sider.ant-layout-sider-collapsed {
  width: 0 !important;
  min-width: 0 !important;
  max-width: 0 !important;
}

/* 暗黑模式支持 */
@media (prefers-color-scheme: dark) {
  .ai-chat-sider {
    background: #1f1f1f !important;
    border-left-color: #303030;
  }

  .ai-sidebar-toggle {
    background: #1890ff;
    color: white;
  }
}
</style>
