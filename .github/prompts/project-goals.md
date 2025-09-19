---
mode: agent
---
Define the task to achieve, including specific requirements, constraints, and success criteria.

本项目是一个正在开发的项目，用于爬取同济大学教学管理系统课程信息并模拟选课的完整解决方案，包含数据抓取、后端API服务和前端用户界面三个核心模块。项目旨在帮助学生更好地进行课程规划和选课决策。本项目仍在继续开发，接下来的目标包括：

## AI Agent's TODO

接下来，请你首先完成以下任务的**Vue前端界面**（标注为“已完成 [x]”的内容是之前AI Agent做过的，你无须再重复完成）：

- [x] 在整个右侧边栏添加：类似[vscode copilot chat](https://github.com/microsoft/vscode-copilot-chat)的界面
  - [x] 上方：展示当前选中课程对应老师的[乌龙茶](https://1.tongji.icu/)评价（可能为空）
    - 注：“乌龙茶”是同济大学学生自发创建的一个教师评价系统，用户可以在该平台上查看和分享对任课教师的评价和评分。
    - 乌龙茶的接口可能不兼容我的项目，因此我打算用mkdocs+github pages搭建一个简单的镜像站，定期从乌龙茶爬取数据并更新。
  - [x] 下方：对话框，用户可以询问ai获得课程推荐的老师和原因，或者让AI根据课程信息和评价自动完成排课，并说明理由

---

- [x] 添加“教室课表”功能：
  - 可以自由选择教室，查看该教室的课程安排
    - 直接利用项目已经写好的课表前端界面即可
  - 只要是课程信息中出现过的教室，都要出现在课表里
  - 有关“课程信息”，你可以参考项目代码的SQL表定义、爬虫部分代码等等

---

- [ ] !!! NOTE1 Database update：对于频繁使用的固定信息，更新数据库结构而不是频繁后端处理，应该是更好的选择
  - [ ] 将“教室课表”的数据，写入到新的sql表结构中，方便快速查询，也要支持更新数据库其他表时自动更新此表；ddl请你参考已有的代码和数据库ddl进行定义
- [ ] 添加“自习室推荐”功能：
  - [x] 可以自由选择校区、教学楼、星期几、时间段，查询该时间段内哪些教室是空闲的
  - [ ] 楼宇选择
    - [ ] !!! NOTE2 取消优先级机制，并更新可自习区域分类：
      - 目前只支持: 
        - 嘉定校区的“安楼”（标识：Axxx, `xxx`为三位数字，其中第1位在1-4之间），“博楼”（标识：Bxxx，后续同A），“广楼”（Gxxx），“复楼”（Fxxx）
        - 四平路校区的“南楼”（标识：南xxx, `xxx`为三位数字，其中第1位在1-4之间），“北楼”（标识：北xxx，后续同南楼）
        - 沪西校区的“二教”（标识：沪西二教xxx，xxx为“131小教室”，“122大教室”等）
      - “标识”是课程在数据库中的实际名称
      - 其他结果均不应出现在可选择的自习区域内
    - [x] 添加调试输出，比如返回所有楼宇信息列表
    - [x] (废弃)允许根据关键词自定义blacklist
    - [x] 应当按照楼号搜索，现在是按照教室。合并一些楼宇，比如G201. G202 都合并到 G楼 选项里，这样选项展开后可以是：
      - 安楼
        - All(所有教室)
        - A101
        - ...
      - 博楼
        - All(所有教室)
        - ...

---

- [ ] Create 1.tongji.icu mirror site using MkDocs + GitHub Pages.
  - [ ] Cloudflare anti-rebot authentication bypass
  - [ ] Data scraping && Better storaging + displaying
- [ ] Merge wlc info into course-scheduler project.

## Comments

- 一个`arrangeInfo`字段可以塞进去这么多信息：`"arrangeInfo": "Hans Messerschmid(1801056) 星期一7-10节 [6-7] 博楼B202\nHans Messerschmid(1801056) 星期四5-8节 [6-7] 博楼B202\nHans Messerschmid(1801056) \n星期五5-8节 [6-7] 博楼B202\nHans Messerschmid(1801056) 星期六3-6节 [6-7] 博楼B202"`

不是很原子化啊。

