<template>
  <div class="classroom-schedule-page">
    <a-layout class="min-h-screen">
      <a-layout-content class="p-4">
        <a-row :gutter="[16, 16]">
          <!-- 左侧：教室选择器 -->
          <a-col :xs="24" :lg="8" :xl="6">
            <RoomSelector 
              @room-selected="onRoomSelected"
              @view-schedule="onViewSchedule"
            />
          </a-col>
          
          <!-- 右侧：教室课表 -->
          <a-col :xs="24" :lg="16" :xl="18">
            <RoomTimeTable :room-info="selectedRoomInfo" />
          </a-col>
        </a-row>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import RoomSelector from './RoomSelector.vue';
import RoomTimeTable from './RoomTimeTable.vue';

interface RoomInfo {
  room: string | null;
  calendarId: number | null;
}

export default defineComponent({
  name: 'ClassroomSchedulePage',
  components: {
    RoomSelector,
    RoomTimeTable
  },
  data() {
    return {
      selectedRoomInfo: {
        room: null,
        calendarId: null
      } as RoomInfo
    };
  },
  methods: {
    onRoomSelected(roomInfo: RoomInfo) {
      this.selectedRoomInfo = { ...roomInfo };
    },

    onViewSchedule(roomInfo: RoomInfo) {
      this.selectedRoomInfo = { ...roomInfo };
    }
  }
});
</script>

<style scoped>
.classroom-schedule-page {
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .classroom-schedule-page :deep(.ant-col) {
    margin-bottom: 16px;
  }
}

/* 确保在小屏幕上教室选择器不会太高 */
@media (max-width: 1200px) {
  .classroom-schedule-page :deep(.room-grid) {
    max-height: 400px;
  }
}
</style>