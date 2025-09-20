<template>
  <div class="ai-chat-sidebar h-full flex flex-col">
    <!-- 上方：教师评价展示区 -->
    <div class="teacher-evaluation-section flex-shrink-0 border-b border-gray-200 p-4">
      <TeacherEvaluation :selectedCourse="currentSelectedCourse" />
    </div>

    <!-- 下方：AI对话框区域 -->
    <div class="chat-section flex-1 flex flex-col min-h-0">
      <AiChatBox />
    </div>
  </div>
</template>

<script lang="ts">
import { defineAsyncComponent } from "vue";

export default {
  name: "AiChatSidebar",
  components: {
    TeacherEvaluation: defineAsyncComponent(() => import("./TeacherEvaluation.vue")),
    AiChatBox: defineAsyncComponent(() => import("./AiChatBox.vue")),
  },
  computed: {
    currentSelectedCourse() {
      return this.$store.state.clickedCourseInfo;
    },
  },
};
</script>

<style scoped>
.ai-chat-sidebar {
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
}

.teacher-evaluation-section {
  max-height: 40%;
  overflow-y: auto;
  border-bottom: 1px solid #e8e8e8;
}

.chat-section {
  flex: 1;
  background: #fafafa;
  min-height: 0; /* 重要：确保flex布局正确工作 */
}
</style>
