<template>
  <div class="classroom-schedule-page">
    <a-layout class="min-h-screen">
      <a-layout-content class="p-4">
        <a-tabs v-model:activeKey="activeTab" type="card" class="classroom-tabs">
          <!-- 教室课表标签页 -->
          <a-tab-pane key="schedule" tab="教室课表">
            <template #tab>
              <span>
                <ScheduleOutlined />
                教室课表
              </span>
            </template>
            
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
          </a-tab-pane>

          <!-- 自习位置建议标签页 -->
          <a-tab-pane key="study-suggestion" tab="自习位置建议">
            <template #tab>
              <span>
                <ReadOutlined />
                自习位置建议
              </span>
            </template>
            
            <StudyRoomSuggestion />
          </a-tab-pane>
        </a-tabs>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { ScheduleOutlined, ReadOutlined } from '@ant-design/icons-vue';
import RoomSelector from './RoomSelector.vue';
import RoomTimeTable from './RoomTimeTable.vue';
import StudyRoomSuggestion from './StudyRoomSuggestion.vue';

interface RoomInfo {
  room: string | null;
  calendarId: number | null;
}

export default defineComponent({
  name: 'ClassroomSchedulePage',
  components: {
    RoomSelector,
    RoomTimeTable,
    StudyRoomSuggestion,
    ScheduleOutlined,
    ReadOutlined
  },
  data() {
    return {
      activeTab: 'schedule', // 默认显示教室课表标签页
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

.classroom-tabs {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.classroom-tabs :deep(.ant-tabs-content-holder) {
  padding-top: 16px;
}

.classroom-tabs :deep(.ant-tabs-tab) {
  font-weight: 500;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .classroom-schedule-page :deep(.ant-col) {
    margin-bottom: 16px;
  }
  
  .classroom-tabs {
    margin: 0;
    border-radius: 0;
  }
}

/* 确保在小屏幕上教室选择器不会太高 */
@media (max-width: 1200px) {
  .classroom-schedule-page :deep(.room-grid) {
    max-height: 400px;
  }
}
</style>