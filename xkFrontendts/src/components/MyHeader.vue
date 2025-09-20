<template>
  <a-layout-header
    class="flex flex-row justify-between items-center"
    style="background-color: #f6f8fa"
  >
    <div class="flex flex-row items-center space-x-4">
      <div class="bg-[url(../assets/myLogo.png)] bg-cover bg-center h-10 w-50"></div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="horizontal"
        style="background: transparent; border: none"
        @select="onMenuSelect"
      >
        <a-menu-item key="schedule">
          <CalendarOutlined />
          个人课表
        </a-menu-item>
        <a-menu-item key="classroom">
          <HomeOutlined />
          教室课表
        </a-menu-item>
      </a-menu>
    </div>
    <div class="float-right flex flex-row space-x-4">
      <div>
        <a-dropdown>
          <template #overlay>
            <a-menu class="text-center">
              <a-menu-item key="wakeUp" @click="wakeUpCSV">
                <div class="flex flex-row space-x-2 items-center">
                  <p>WakeUp 课程表支持的 csv 格式</p>
                  <p><a href="https://www.wakeup.fun/" target="_blank">[官网]</a></p>
                </div>
              </a-menu-item>
              <a-menu-item key="excel" @click="helpExcel">
                <p>辅助选课的 xls 文件</p>
              </a-menu-item>
            </a-menu>
          </template>
          <a-button>
            <div class="flex flex-row space-x-2 items-center">
              <p>导出为</p>
              <div><ExportOutlined /></div>
            </div>
          </a-button>
        </a-dropdown>
      </div>
      <div>
        <a-button @click="readTheDocs">
          <div class="flex flex-row space-x-2 items-center">
            <p>帮助文档</p>
            <div><ReadOutlined /></div>
          </div>
        </a-button>
      </div>
      <div>
        <a-dropdown>
          <template #overlay>
            <a-menu class="text-center">
              <a-menu-item key="tongji">
                <a href="https://1.tongji.edu.cn" target="_blank">1 系统</a>
              </a-menu-item>
              <a-menu-item key="wlc">
                <a href="https://1.tongji.icu" target="_blank">乌龙茶</a>
              </a-menu-item>
              <a-menu-item key="github">
                <div class="flex flex-row space-x-2 items-center">
                  <div><GithubOutlined /></div>
                  <div>
                    <a
                      href="https://github.com/XiaLing233/tongji-course-scheduler"
                      target="_blank"
                      style="color: inherit"
                      >项目仓库</a
                    >
                  </div>
                </div>
              </a-menu-item>
            </a-menu>
          </template>
          <a-button>
            <div class="flex flex-row space-x-2 items-center">
              <p>友情链接</p>
              <div><LinkOutlined /></div>
            </div>
          </a-button>
        </a-dropdown>
      </div>
    </div>
  </a-layout-header>
</template>

<script lang="ts">
import {
  ExportOutlined,
  GithubOutlined,
  CalendarOutlined,
  LinkOutlined,
  ReadOutlined,
  HomeOutlined,
} from "@ant-design/icons-vue";
import { codesToJsonForCSV, jsonToCSV, downloadCSV } from "@/utils/csvRelated";
import { codesToJsonForXLS, jsonToXLS, downloadXLS } from "@/utils/xlsRelated";
import { errorNotify } from "@/utils/errorNotify";

export default {
  components: {
    ExportOutlined,
    GithubOutlined,
    ReadOutlined,
    LinkOutlined,
    CalendarOutlined,
    HomeOutlined,
  },
  emits: ["menu-change"],
  data() {
    return {
      selectedKeys: ["schedule"] as string[],
    };
  },
  methods: {
    onMenuSelect({ key }: { key: string }) {
      this.selectedKeys = [key];
      this.$emit("menu-change", key);
    },
    wakeUpCSV() {
      const csv = codesToJsonForCSV(
        this.$store.state.commonLists.selectedCourses,
        this.$store.state.commonLists.stagedCourses,
      );
      const csvString = jsonToCSV(csv);
      downloadCSV(csvString);
    },
    helpExcel() {
      const xls = codesToJsonForXLS(
        this.$store.state.commonLists.selectedCourses,
        this.$store.state.commonLists.stagedCourses,
      );
      const xlsBlob = jsonToXLS(xls);
      downloadXLS(xlsBlob);
    },
    readTheDocs() {
      errorNotify("敬请期待");
    },
  },
};
</script>
