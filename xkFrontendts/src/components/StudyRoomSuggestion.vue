<template>
  <div class="study-room-suggestion">
    <!-- 条件选择区域 -->
    <a-card class="mb-4">
      <template #title>
        <span class="flex items-center">
          <ReadOutlined class="mr-2" />
          自习位置建议
        </span>
      </template>
      
      <a-form layout="inline" class="suggestion-form">
        <a-form-item label="校区">
          <a-select
            v-model:value="searchCriteria.campus"
            placeholder="请选择校区"
            style="width: 150px"
            @change="onCampusChange"
          >
            <a-select-option value="四平路校区">四平路校区</a-select-option>
            <a-select-option value="嘉定校区">嘉定校区</a-select-option>
            <a-select-option value="彰武路校区">彰武路校区</a-select-option>
            <a-select-option value="沪西校区">沪西校区</a-select-option>
            <a-select-option value="沪北校区">沪北校区</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="楼宇">
          <a-select
            v-model:value="searchCriteria.building"
            placeholder="全部楼宇（可选）"
            style="width: 200px"
            allow-clear
            :loading="buildingsLoading"
            @change="onBuildingChange"
          >
            <a-select-option 
              v-for="building in buildings" 
              :key="building.building" 
              :value="building.building"
            >
              {{ building.building }} ({{ building.roomCount }}间教室)
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="具体教室" v-if="searchCriteria.building && availableRooms.length > 0">
          <a-select
            v-model:value="searchCriteria.specificRoom"
            placeholder="全部教室（可选）"
            style="width: 200px"
            allow-clear
          >
            <a-select-option 
              v-for="room in availableRooms" 
              :key="room" 
              :value="room"
            >
              {{ room === 'All' ? '全部教室' : room }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="星期">
          <a-select
            v-model:value="searchCriteria.dayOfWeek"
            placeholder="请选择星期"
            style="width: 120px"
          >
            <a-select-option :value="1">星期一</a-select-option>
            <a-select-option :value="2">星期二</a-select-option>
            <a-select-option :value="3">星期三</a-select-option>
            <a-select-option :value="4">星期四</a-select-option>
            <a-select-option :value="5">星期五</a-select-option>
            <a-select-option :value="6">星期六</a-select-option>
            <a-select-option :value="7">星期日</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="时间段">
          <a-select
            v-model:value="searchCriteria.startTime"
            placeholder="开始节次"
            style="width: 100px"
          >
            <a-select-option 
              v-for="i in 12" 
              :key="i" 
              :value="i"
            >
              第{{ i }}节
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="至">
          <a-select
            v-model:value="searchCriteria.endTime"
            placeholder="结束节次"
            style="width: 100px"
          >
            <a-select-option 
              v-for="i in 12" 
              :key="i" 
              :value="i"
              :disabled="i <= searchCriteria.startTime"
            >
              第{{ i }}节
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item>
          <a-button 
            type="primary" 
            @click="searchSuggestions"
            :loading="suggestionsLoading"
            :disabled="!canSearch"
          >
            <SearchOutlined />
            查找推荐
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 搜索结果区域 -->
    <a-card v-if="suggestions.length > 0 || suggestionsLoading">
      <template #title>
        <span class="flex items-center justify-between">
          <span>
            <EnvironmentOutlined class="mr-2" />
            推荐结果
          </span>
          <a-tag v-if="summary" color="blue">
            共{{ summary.totalRooms }}间教室，{{ summary.availableRooms }}间可用，{{ summary.fullyFreeRooms }}间完全空闲
          </a-tag>
        </span>
      </template>

      <a-spin :spinning="suggestionsLoading">
        <div v-if="suggestions.length === 0 && !suggestionsLoading" class="text-center py-8">
          <a-empty description="没有找到符合条件的自习位置" />
        </div>

        <div v-else class="suggestions-list">
          <a-row :gutter="[16, 16]">
            <a-col 
              v-for="suggestion in suggestions" 
              :key="suggestion.room"
              :xs="24" 
              :sm="12" 
              :lg="8"
            >
              <a-card 
                size="small" 
                :class="{
                  'suggestion-card': true,
                  'fully-free': suggestion.isFullyFree,
                  'partially-free': !suggestion.isFullyFree && suggestion.freePeriods.length > 0
                }"
              >
                <template #title>
                  <span class="flex items-center justify-between">
                    <span class="room-name">{{ suggestion.room }}</span>
                    <a-tag 
                      :color="suggestion.isFullyFree ? 'green' : 'orange'"
                      size="small"
                    >
                      {{ suggestion.isFullyFree ? '完全空闲' : '部分空闲' }}
                    </a-tag>
                  </span>
                </template>

                <div class="suggestion-content">
                  <div class="campus-info mb-2">
                    <EnvironmentOutlined class="mr-1" />
                    {{ suggestion.campus }}
                  </div>

                  <div class="free-periods">
                    <div class="periods-title mb-2">
                      <ClockCircleOutlined class="mr-1" />
                      可用时段：
                    </div>
                    <div class="periods-list">
                      <a-tag 
                        v-for="(period, index) in suggestion.freePeriods"
                        :key="index"
                        :color="period.duration >= getRequestedDuration() ? 'green' : 'orange'"
                        class="period-tag"
                      >
                        第{{ period.start }}-{{ period.end }}节 ({{ period.duration }}节课)
                      </a-tag>
                    </div>
                  </div>
                </div>
              </a-card>
            </a-col>
          </a-row>
        </div>
      </a-spin>
    </a-card>

    <!-- 帮助信息 -->
    <a-card v-if="suggestions.length === 0 && !suggestionsLoading && !hasSearched" class="help-card">
      <template #title>
        <span class="flex items-center">
          <QuestionCircleOutlined class="mr-2" />
          使用说明
        </span>
      </template>
      
      <div class="help-content">
        <p class="mb-2">
          <strong>如何使用自习位置建议：</strong>
        </p>
        <ul class="list-disc list-inside space-y-1 text-gray-600">
          <li>选择您所在的<strong>校区</strong>（必选）</li>
          <li>选择具体的<strong>楼宇</strong>（可选，不选择则搜索整个校区）</li>
          <li>选择您要自习的<strong>星期</strong>和<strong>时间段</strong></li>
          <li>点击"查找推荐"获取空闲教室建议</li>
        </ul>
        <p class="mt-4 text-sm text-gray-500">
          <InfoCircleOutlined class="mr-1" />
          系统会根据课程安排分析教室使用情况，为您推荐最佳的自习位置。
        </p>
      </div>
    </a-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { message } from 'ant-design-vue'
import {
  SearchOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  ReadOutlined,
  QuestionCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'

// 类型定义
interface SearchCriteria {
  campus: string
  building?: string
  specificRoom?: string
  dayOfWeek: number
  startTime: number
  endTime: number
}

interface FreePeriod {
  start: number
  end: number
  duration: number
}

interface StudyRoomSuggestion {
  room: string
  campus: string
  freePeriods: FreePeriod[]
  isFullyFree: boolean
}

interface SuggestionSummary {
  totalRooms: number
  availableRooms: number
  fullyFreeRooms: number
}

interface BuildingInfo {
  building: string
  rooms: string[]
  roomCount: number
  priority: number
}

interface RequestData {
  campus: string
  building?: string
  specificRoom?: string
  dayOfWeek: number
  startTime: number
  endTime: number
  calendarId: number
}

export default defineComponent({
  name: 'StudyRoomSuggestion',
  components: {
    SearchOutlined,
    EnvironmentOutlined,
    ClockCircleOutlined,
    ReadOutlined,
    QuestionCircleOutlined,
    InfoCircleOutlined
  },
  data() {
    return {
      suggestions: [] as StudyRoomSuggestion[],
      buildings: [] as BuildingInfo[],
      summary: null as SuggestionSummary | null,
      suggestionsLoading: false,
      buildingsLoading: false,
      hasSearched: false,
      searchCriteria: {
        campus: '四平路校区',
        building: undefined,
        specificRoom: undefined,
        dayOfWeek: 1,
        startTime: 6,
        endTime: 11
      } as SearchCriteria
    }
  },
  computed: {
    canSearch() {
      return this.searchCriteria.campus && 
             this.searchCriteria.dayOfWeek && 
             this.searchCriteria.startTime && 
             this.searchCriteria.endTime &&
             this.searchCriteria.startTime < this.searchCriteria.endTime
    },
    availableRooms() {
      if (!this.searchCriteria.building) return []
      const selectedBuilding = this.buildings.find(b => b.building === this.searchCriteria.building)
      return selectedBuilding ? selectedBuilding.rooms : []
    }
  },
  watch: {
    'searchCriteria.campus'() {
      this.searchCriteria.building = undefined
      this.searchCriteria.specificRoom = undefined
      this.buildings = []
      if (this.searchCriteria.campus) {
        this.loadBuildings()
      }
    }
  },
  mounted() {
    this.loadBuildings()
  },
  methods: {
    getRequestedDuration() {
      return this.searchCriteria.endTime - this.searchCriteria.startTime + 1
    },

    onCampusChange() {
      // 校区变化时清除楼宇和教室选择
      this.searchCriteria.building = undefined
      this.searchCriteria.specificRoom = undefined
    },

    onBuildingChange() {
      // 楼宇变化时清除具体教室选择
      this.searchCriteria.specificRoom = undefined
    },

    async loadBuildings() {
      if (!this.searchCriteria.campus) return
      
      this.buildingsLoading = true
      try {
        const response = await fetch('/api/getAllBuildings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            campus: this.searchCriteria.campus,
            calendarId: this.$store.state.majorSelected?.calendarId || 119
          })
        })

        const result = await response.json()
        if (result.code === 200) {
          this.buildings = result.data
        } else {
          message.error(result.msg || '获取楼宇信息失败')
        }
      } catch (error) {
        console.error('Load buildings error:', error)
        message.error('网络错误，请稍后重试')
      } finally {
        this.buildingsLoading = false
      }
    },

    async searchSuggestions() {
      if (!this.canSearch) {
        message.warning('请完善搜索条件')
        return
      }

      this.suggestionsLoading = true
      this.hasSearched = true
      
      try {
        const requestData: RequestData = {
          campus: this.searchCriteria.campus,
          dayOfWeek: this.searchCriteria.dayOfWeek,
          startTime: this.searchCriteria.startTime,
          endTime: this.searchCriteria.endTime,
          calendarId: this.$store.state.majorSelected?.calendarId || 119
        }

        // 如果选择了楼宇，添加到请求中
        if (this.searchCriteria.building) {
          requestData.building = this.searchCriteria.building
        }

        // 如果选择了具体教室，添加到请求中
        if (this.searchCriteria.specificRoom && this.searchCriteria.specificRoom !== 'All') {
          requestData.specificRoom = this.searchCriteria.specificRoom
        }

        const response = await fetch('/api/getStudyRoomSuggestions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
        })

        const result = await response.json()
        if (result.code === 200) {
          this.suggestions = result.data.suggestions
          this.summary = result.data.summary
          
          if (this.suggestions.length === 0) {
            message.info('没有找到符合条件的自习位置，请尝试调整搜索条件')
          } else {
            message.success(`找到 ${this.summary?.availableRooms} 个可用的自习位置`)
          }
        } else {
          message.error(result.msg || '搜索失败')
          this.suggestions = []
          this.summary = null
        }
      } catch (error) {
        console.error('Search suggestions error:', error)
        message.error('网络错误，请稍后重试')
        this.suggestions = []
        this.summary = null
      } finally {
        this.suggestionsLoading = false
      }
    }
  }
})
</script>

<style scoped>
.study-room-suggestion {
  min-height: 400px;
}

.suggestion-form {
  flex-wrap: wrap;
  gap: 16px;
}

.suggestion-form .ant-form-item {
  margin-bottom: 16px;
}

.suggestions-list {
  min-height: 200px;
}

.suggestion-card {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.suggestion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-card.fully-free {
  border-left: 4px solid #52c41a;
}

.suggestion-card.partially-free {
  border-left: 4px solid #faad14;
}

.room-name {
  font-weight: 600;
  font-size: 14px;
}

.suggestion-content {
  font-size: 13px;
}

.campus-info {
  color: #666;
  display: flex;
  align-items: center;
}

.periods-title {
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
}

.periods-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.period-tag {
  margin: 2px;
  font-size: 12px;
}

.help-card {
  margin-top: 16px;
}

.help-content {
  line-height: 1.6;
}

.help-content ul {
  padding-left: 20px;
}

.help-content li {
  margin-bottom: 4px;
}

@media (max-width: 768px) {
  .suggestion-form {
    flex-direction: column;
  }
  
  .suggestion-form .ant-form-item {
    width: 100%;
  }
  
  .suggestion-form .ant-select {
    width: 100% !important;
  }
}
</style>