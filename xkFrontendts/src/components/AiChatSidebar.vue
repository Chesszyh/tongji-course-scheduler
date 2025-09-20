<template>
  <div class="ai-chat-sidebar h-full flex flex-col">
    <!-- 上方：教师评价展示区 -->
    <div class="teacher-evaluation-section flex-shrink-0 border-b p-4"
         :class="$store.state.theme.isDark ? 'border-gray-600' : 'border-gray-200'">
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
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s ease;
}

.teacher-evaluation-section {
  max-height: 40%;
  overflow-y: auto;
}

.chat-section {
  flex: 1;
  background: var(--bg-secondary);
  min-height: 0;
  transition: background-color 0.3s ease;
}
</style>
