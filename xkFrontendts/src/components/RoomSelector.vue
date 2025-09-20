<template>
  <div class="room-selector">
    <a-card title="教室选择" :bordered="false" class="mb-4">
      <a-form layout="inline" class="mb-4">
        <a-form-item label="学期">
          <a-select
            v-model:value="selectedCalendar"
            placeholder="请选择学期"
            style="width: 200px"
            @change="onCalendarChange"
          >
            <a-select-option
              v-for="calendar in calendarList"
              :key="calendar.calendarId"
              :value="calendar.calendarId"
            >
              {{ calendar.calendarName }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="搜索教室">
          <a-input
            v-model:value="searchKeyword"
            placeholder="输入教室名称搜索"
            style="width: 200px"
            @input="filterRooms"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
        </a-form-item>
      </a-form>

      <a-spin :spinning="loading" tip="正在加载教室列表...">
        <div v-if="filteredRooms.length > 0" class="room-grid">
          <a-card
            v-for="room in paginatedRooms"
            :key="room"
            :class="['room-card', { selected: selectedRoom === room }]"
            @click="selectRoom(room)"
            hoverable
            size="small"
          >
            <template #title>
              <HomeOutlined class="mr-1" />
              {{ room }}
            </template>
            <div class="room-info">
              <a-tag v-if="selectedRoom === room" color="blue">已选择</a-tag>
              <a-button type="link" size="small" @click.stop="viewRoomSchedule(room)">
                查看课表
              </a-button>
            </div>
          </a-card>
        </div>

        <a-empty v-else-if="!loading" description="没有找到匹配的教室" />

        <a-pagination
          v-if="filteredRooms.length > pageSize"
          v-model:current="currentPage"
          v-model:page-size="pageSize"
          :total="filteredRooms.length"
          :show-size-changer="false"
          :show-quick-jumper="true"
          class="mt-4 text-center"
          size="small"
        />
      </a-spin>
    </a-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { SearchOutlined, HomeOutlined } from "@ant-design/icons-vue";
import axios from "axios";
import { errorNotify } from "@/utils/errorNotify";

export default defineComponent({
  name: "RoomSelector",
  components: {
    SearchOutlined,
    HomeOutlined,
  },
  emits: ["room-selected", "view-schedule"],
  data() {
    return {
      calendarList: [] as Array<{ calendarId: number; calendarName: string }>,
      selectedCalendar: null as number | null,
      rooms: [] as string[],
      filteredRooms: [] as string[],
      selectedRoom: null as string | null,
      searchKeyword: "",
      loading: false,
      currentPage: 1,
      pageSize: 20,
    };
  },
  computed: {
    paginatedRooms() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredRooms.slice(start, end);
    },
  },
  async mounted() {
    await this.loadCalendarList();
    // 默认选择第一个学期
    if (this.calendarList.length > 0) {
      this.selectedCalendar = this.calendarList[0].calendarId;
      await this.loadRooms();
    }
  },
  methods: {
    async loadCalendarList() {
      try {
        const response = await axios.get("/api/getAllCalendar");
        this.calendarList = response.data.data;
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        errorNotify("加载学期列表失败: " + errorMessage);
      }
    },

    async loadRooms() {
      if (!this.selectedCalendar) return;

      this.loading = true;
      try {
        const response = await axios.post("/api/getAllRooms", {
          calendarId: this.selectedCalendar,
        });
        this.rooms = response.data.data;
        this.filterRooms();
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        errorNotify("加载教室列表失败: " + errorMessage);
      } finally {
        this.loading = false;
      }
    },

    async onCalendarChange() {
      this.selectedRoom = null;
      this.searchKeyword = "";
      this.currentPage = 1;
      await this.loadRooms();
    },

    filterRooms() {
      if (this.searchKeyword.trim() === "") {
        this.filteredRooms = [...this.rooms];
      } else {
        this.filteredRooms = this.rooms.filter((room) =>
          room.toLowerCase().includes(this.searchKeyword.toLowerCase()),
        );
      }
      this.currentPage = 1;
    },

    selectRoom(room: string) {
      this.selectedRoom = room;
      this.$emit("room-selected", {
        room,
        calendarId: this.selectedCalendar,
      });
    },

    viewRoomSchedule(room: string) {
      this.selectRoom(room);
      // 触发查看课表事件
      this.$emit("view-schedule", {
        room,
        calendarId: this.selectedCalendar,
      });
    },
  },
});
</script>

<style scoped>
.room-selector {
  width: 100%;
}

.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.room-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.room-card:hover {
  border-color: #1890ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.room-card.selected {
  border-color: #1890ff;
  background-color: #f0f8ff;
}

.room-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

:deep(.ant-card-head-title) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.ant-card-body) {
  padding: 12px;
}

/* 滚动条样式 */
.room-grid::-webkit-scrollbar {
  width: 6px;
}

.room-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.room-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.room-grid::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
