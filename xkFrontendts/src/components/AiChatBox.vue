<template>
  <div class="ai-chat-box h-full flex flex-col">
    <!-- Chat Header -->
    <div class="chat-header flex-shrink-0 p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center gap-2">
        <RobotOutlined class="text-blue-600" />
        <span class="font-medium text-gray-800">AI 排课助手</span>
        <a-badge :count="messages.length" :overflowCount="99" class="ml-auto" />
      </div>
      <div class="text-xs text-gray-500 mt-1">
        智能课程推荐 • 自动排课规划
      </div>
    </div>
    
    <!-- Chat Messages -->
    <div class="chat-messages flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="ai-message">
          <div class="message-avatar">
            <RobotOutlined class="text-blue-600" />
          </div>
          <div class="message-content bg-blue-50 border-blue-200">
            <div class="message-text">
              👋 您好！我是AI排课助手，可以帮您：
              <ul class="mt-2 ml-4 space-y-1">
                <li>• 根据课程评价推荐优秀教师</li>
                <li>• 智能规避时间冲突</li>
                <li>• 自动生成最优排课方案</li>
              </ul>
              <div class="mt-3 text-xs text-gray-600">
                💡 试试问我："帮我推荐高等数学的好老师" 或 "帮我自动排课"
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        class="message-item"
        :class="message.type"
      >
        <div v-if="message.type === 'user'" class="user-message">
          <div class="message-content bg-blue-600 text-white">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
          <div class="message-avatar">
            <UserOutlined class="text-gray-600" />
          </div>
        </div>
        
        <div v-else class="ai-message">
          <div class="message-avatar">
            <RobotOutlined class="text-blue-600" />
          </div>
          <div class="message-content bg-gray-50 border-gray-200">
            <div v-if="message.loading" class="message-loading">
              <div class="flex items-center gap-2">
                <a-spin size="small" />
                <span class="text-gray-500">AI正在思考...</span>
              </div>
            </div>
            <div v-else class="message-text">
              <div v-html="formatAiMessage(message.content)"></div>
              <div class="message-time mt-2">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Chat Input -->
    <div class="chat-input flex-shrink-0 p-4 border-t border-gray-200 bg-white">
      <div class="flex gap-2">
        <a-input
          v-model:value="inputMessage"
          placeholder="问我关于课程推荐或排课的问题..."
          @press-enter="sendMessage"
          :disabled="isLoading"
          class="flex-1"
        />
        <a-button 
          type="primary" 
          :loading="isLoading"
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
        >
          <template #icon>
            <SendOutlined />
          </template>
        </a-button>
      </div>
      
      <!-- 快捷操作按钮 -->
      <div class="quick-actions mt-3 flex gap-2 flex-wrap">
        <a-button 
          size="small" 
          type="text"
          @click="sendQuickMessage('帮我推荐优秀的教师')"
        >
          📚 推荐优秀教师
        </a-button>
        <a-button 
          size="small" 
          type="text"
          @click="sendQuickMessage('帮我自动排课')"
        >
          🤖 自动排课
        </a-button>
        <a-button 
          size="small" 
          type="text"
          @click="sendQuickMessage('检查课程冲突')"
        >
          ⚠️ 检查冲突
        </a-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { RobotOutlined, UserOutlined, SendOutlined } from '@ant-design/icons-vue';
import { nextTick } from 'vue';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  loading?: boolean;
}

export default {
  name: 'AiChatBox',
  components: {
    RobotOutlined,
    UserOutlined,
    SendOutlined
  },
  data() {
    return {
      messages: [] as ChatMessage[],
      inputMessage: '',
      isLoading: false
    }
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return;
      
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'user',
        content: this.inputMessage.trim(),
        timestamp: new Date()
      };
      
      this.messages.push(userMessage);
      const messageContent = this.inputMessage.trim();
      this.inputMessage = '';
      this.isLoading = true;
      
      // 添加AI加载消息
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '',
        timestamp: new Date(),
        loading: true
      };
      this.messages.push(aiMessage);
      
      await this.scrollToBottom();
      
      try {
        // 模拟AI响应
        const response = await this.generateAiResponse(messageContent);
        
        // 更新AI消息
        const messageIndex = this.messages.findIndex(m => m.id === aiMessage.id);
        if (messageIndex !== -1) {
          this.messages[messageIndex] = {
            ...aiMessage,
            content: response,
            loading: false,
            timestamp: new Date()
          };
        }
      } catch (error) {
        console.error('AI响应失败:', error);
        // 错误处理
        const messageIndex = this.messages.findIndex(m => m.id === aiMessage.id);
        if (messageIndex !== -1) {
          this.messages[messageIndex] = {
            ...aiMessage,
            content: '抱歉，AI服务暂时不可用，请稍后再试。',
            loading: false,
            timestamp: new Date()
          };
        }
      } finally {
        this.isLoading = false;
        await this.scrollToBottom();
      }
    },
    
    async sendQuickMessage(message: string) {
      this.inputMessage = message;
      await this.sendMessage();
    },
    
    async generateAiResponse(userMessage: string): Promise<string> {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      // 简单的消息匹配逻辑 - 将来替换为真实的AI API
      const message = userMessage.toLowerCase();
      
      if (message.includes('推荐') && (message.includes('教师') || message.includes('老师'))) {
        return this.generateTeacherRecommendation();
      } else if (message.includes('自动排课') || message.includes('排课')) {
        return this.generateScheduleRecommendation();
      } else if (message.includes('冲突')) {
        return this.generateConflictCheck();
      } else {
        return this.generateGeneralResponse();
      }
    },
    
    generateTeacherRecommendation(): string {
      const currentCourse = this.$store.state.clickedCourseInfo;
      if (currentCourse && currentCourse.courseName) {
        return `
          <div class="ai-response">
            <h4>📚 ${currentCourse.courseName} 教师推荐</h4>
            <div class="recommendation-card">
              <div class="teacher-recommendation">
                <strong>🌟 张教授</strong> (评分: 4.5/5.0)
                <ul>
                  <li>• 教学清晰，深入浅出</li>
                  <li>• 作业量适中，反馈及时</li>
                  <li>• 学生评价: "非常棒的老师！"</li>
                </ul>
              </div>
              <div class="teacher-recommendation">
                <strong>✨ 李老师</strong> (评分: 4.2/5.0)
                <ul>
                  <li>• 课程内容丰富</li>
                  <li>• 注重实践应用</li>
                  <li>• 学生评价: "学到很多实用知识"</li>
                </ul>
              </div>
            </div>
            <p class="mt-3 text-sm text-gray-600">💡 建议优先选择张教授的课程，时间安排也更灵活。</p>
          </div>
        `;
      } else {
        return `
          请先选择一门课程，我就能为您推荐该课程的优秀教师了！
          
          您可以：
          1. 点击左侧课程列表中的任意课程
          2. 我会分析该课程所有教师的评价数据
          3. 为您推荐评分最高、学生评价最好的教师
        `;
      }
    },
    
    generateScheduleRecommendation(): string {
      const stagedCourses = this.$store.state.commonLists.stagedCourses;
      if (stagedCourses.length > 0) {
        return `
          <div class="ai-response">
            <h4>🤖 智能排课建议</h4>
            <p>基于您当前选择的 ${stagedCourses.length} 门课程，我为您生成了最优排课方案：</p>
            
            <div class="schedule-recommendation">
              <h5>📅 推荐方案 A</h5>
              <ul>
                <li>• 周一上午：高等数学 (张教授班)</li>
                <li>• 周二下午：英语 (李老师班)</li>
                <li>• 周三上午：物理 (王教授班)</li>
              </ul>
              
              <div class="benefits">
                <strong>✅ 优势：</strong>
                <ul>
                  <li>• 无时间冲突</li>
                  <li>• 选择了评分最高的教师</li>
                  <li>• 课程分布均匀，学习压力平衡</li>
                </ul>
              </div>
            </div>
            
            <p class="mt-3 text-sm text-blue-600">💡 是否应用此排课方案？我可以帮您自动选择对应的课程班级。</p>
          </div>
        `;
      } else {
        return `
          您还没有添加待选课程。请先：
          
          1. 📚 在左侧选择您想要的课程
          2. ➕ 将课程添加到待选列表
          3. 🤖 然后我就能为您智能生成最优排课方案了！
          
          我会考虑：
          • ⏰ 时间冲突避免
          • 👨‍🏫 优秀教师推荐  
          • 📊 课程负载平衡
        `;
      }
    },
    
    generateConflictCheck(): string {
      return `
        <div class="ai-response">
          <h4>⚠️ 课程冲突检查</h4>
          <div class="conflict-check">
            <div class="no-conflict">
              <strong>✅ 检查完成</strong>
              <p>当前您的课程安排没有时间冲突！</p>
            </div>
            
            <div class="schedule-tips">
              <h5>📝 排课建议：</h5>
              <ul>
                <li>• 建议在周一、三、五安排主要课程</li>
                <li>• 周二、四可安排较轻松的选修课</li>
                <li>• 避免连续4节课以上的安排</li>
              </ul>
            </div>
          </div>
        </div>
      `;
    },
    
    generateGeneralResponse(): string {
      return `
        我是您的AI排课助手，可以帮助您：
        
        🎯 **主要功能：**
        • 📚 **教师推荐** - 基于学生评价推荐优秀教师
        • 🤖 **智能排课** - 自动生成无冲突的最优课表
        • ⚠️ **冲突检测** - 实时检查时间冲突
        • 📊 **数据分析** - 分析课程难度和工作量
        
        💡 **使用提示：**
        您可以问我具体问题，比如：
        • "推荐高等数学的好老师"
        • "帮我检查课程冲突"
        • "自动为我排课"
        
        或者点击下方的快捷按钮开始！
      `;
    },
    
    formatAiMessage(content: string): string {
      // 简单的HTML格式化
      return content.replace(/\n/g, '<br>');
    },
    
    formatTime(timestamp: Date): string {
      return timestamp.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    async scrollToBottom() {
      await nextTick();
      const container = this.$refs.messagesContainer as HTMLElement;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }
}
</script>

<style scoped>
.ai-chat-box {
  background: #ffffff;
}

.chat-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.chat-messages {
  background: #fafafa;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.user-message {
  justify-content: flex-end;
  display: flex;
  gap: 8px;
}

.ai-message {
  justify-content: flex-start;
  display: flex;
  gap: 8px;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid;
  position: relative;
}

.user-message .message-content {
  border-radius: 12px 12px 4px 12px;
}

.ai-message .message-content {
  border-radius: 12px 12px 12px 4px;
}

.message-text {
  line-height: 1.5;
  font-size: 14px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}

.welcome-message .message-content {
  max-width: 90%;
}

.ai-response h4 {
  color: #1f2937;
  margin-bottom: 12px;
  font-weight: 600;
}

.ai-response h5 {
  color: #374151;
  margin: 12px 0 8px 0;
  font-weight: 500;
}

.ai-response ul {
  margin: 8px 0;
  padding-left: 16px;
}

.ai-response li {
  margin: 4px 0;
  line-height: 1.4;
}

.recommendation-card, .schedule-recommendation, .conflict-check {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
}

.teacher-recommendation {
  background: white;
  padding: 10px;
  border-radius: 6px;
  margin: 8px 0;
  border-left: 3px solid #3b82f6;
}

.benefits, .schedule-tips {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
}

.no-conflict {
  text-align: center;
  padding: 16px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  color: #166534;
}

.quick-actions {
  max-width: 100%;
}

.quick-actions .ant-btn {
  font-size: 12px;
  height: 28px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.quick-actions .ant-btn:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}
</style>