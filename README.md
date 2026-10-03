# PandaPal - 对对对你说的都队

PandaPal（熊猫管家）—— 孩子的终身陪伴成长管家

> "从小用到大，最懂你的那个人"

**在线 Demo：[https://xustalis.site/pandapal/](https://xustalis.site/pandapal/)**（评委可直接访问；演示账号见「快速开始」）｜ 本仓库全部代码为比赛期间原创，完整提交历史见 Git log

## 一、项目简介

教育行业 · **家校协同与学员成长服务环节**：绑定单个孩子的 AI 成长管家——记住孩子的一切、听懂孩子的意图、主动把事办了。

**定位一句话**：管家是教育行业的**服务层，不是内容层**——不做任何一节课，只管课外所有"要办的事"（准备、规划、沟通、跟进、记忆）；受雇于家长，服务于孩子，对家庭整体利益负责。

形态是**事务驱动的主动管家**，不是聊天机器人：打开就在汇报"这几天替你盯着的事"，每件事务从发现 → 规划 → 执行 → 等确认 → 跟进 → 结案，全程写进日志、挂回记忆；孩子的隐私边界是结构而不是承诺。解决三方沟通断层（学校德育处/家校沟通岗、教培机构教务与学员服务部门每天耗在"学情翻译"上的人力成本）与"孩子没人做通盘规划"的普遍痛点。

与通用 AI（豆包等）的差异：**双层记忆**（活跃关注点块每轮必注入 + 主题图谱检索）实现"持续知晓"；**事件驱动的任务拆解与执行**（LLM→DAG→并行执行→结构化卡片）；**记忆驱动的主动问候与晨间巡检**；**三层权限膜**（事务层三方透明 / 陪伴层只对孩子 / 安全层唯一刺破）。

本仓库全部代码为比赛期间原创。**架构设计参考了团队开源项目 [OpenPanda](https://github.com/Xustalis/OpenPanda)（MIT License，仅作设计参考，未引入其代码）**：意图分类入口、结构化 plan spec 输出约定、文件式记忆布局（MEMORY.md / topics / daily）与注入策略。

## 二、系统架构与 Agent 工作流

![PandaButler 系统架构](docs/architecture.svg)

**三视角前端**（孩子 3D 竹林小屋 / 家长白天视角 / admin 验真后台，零构建 + PWA）→ **FastAPI 单进程服务端**（鉴权、对话管线、记忆图谱、事务家庭侧、语音、工具、LLM 客户端）→ **文件系统存储**（数据即文件，无数据库）→ **外部服务**（LLM 双协议 / 小米 MiMo 语音 / 天气 / 搜索，Key 只在服务端）。

![PandaButler Agent 工作流](docs/agent_workflow.svg)

一条消息的完整旅程：轮前记忆注入（统一围栏）→ FastTriage 快速路 → router 分类 → 闲聊/讲懂（含工具轮）或 plan 管线（planner：信息不够先反问 / 够则出 DAG → executor 并行 → synth 卡片 → 判官自检）→ 轮后抽取沉淀；右侧是 SSE 事件流与三条"降级不降真"路径。

![PandaButler 记忆与隐私边界](docs/memory_privacy.svg)

记忆双层落盘（文件层人可读 + 图谱层结构化），悄悄话只进图谱 private 节点、不落文件层；三个注入出口统一围栏；视角过滤在服务端强制（家长视角 leaked_private = 0，导出只给孩子）。

## 三、技术栈

- 前端：原生 ES Modules 单页（零构建步骤，部署最稳）——3D「竹林小屋」场景与低多边形熊猫管家（three.js r160 + OrbitControls + CSS2DRenderer 本地托管在 `web/vendor/`，WebGL 不可用自动降级 2D SVG）、SSE 流渲染、任务树、结构化卡片、记忆星球、自托管字体（DM Sans / Source Serif 4）
- 后端：Python FastAPI + asyncio（SSE 用 StreamingResponse）
- AI/大模型：OpenAI 兼容协议 与 Anthropic Messages 协议双支持，`env` 一键切换；主备 Key + 异构兜底端点
- 语音：小米 MiMo TTS（音色设计/合成）+ ASR（浏览器 SpeechRecognition 优先、服务端兜底）
- 存储：文件系统（markdown 记忆 + JSON 图谱/事务 + index.json），单写锁 + tmp→rename 原子写，无数据库依赖

## 四、快速开始

### 环境要求

- Python 3.10+

### 安装步骤

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # 仅运行服务可用 requirements.txt
cp .env.example .env   # 然后填入你的 LLM_API_KEY 等
```

### 运行方式

```bash
.venv/bin/python -m server.main          # 或 .venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000
# 打开 http://localhost:8000
```

演示档案：登录名输入 **小豆**（预置了记忆数据的演示孩子）；输入任意其他名字会自动新建空白档案，评委互不影响。

### 登录与权限（用户名 + 密码）

| 账号     | 密码                                           | 角色 | 能用什么                                                             |
| -------- | ---------------------------------------------- | ---- | -------------------------------------------------------------------- |
| `小豆`   | `panda123`                                     | 孩子 | 聊天 / 悄悄话 / 梦想 / 星球 / 事务 / 记忆本 / 成长（自己的完整档案） |
| `豆豆妈` | `mama123`                                      | 家长 | 收件箱确认、传话筒 + 孩子档案的只读视图（悄悄话服务端强制过滤）      |
| `admin`  | `admin123`（登录页不再提供一键入口，手动输入） | 评委 | 全部能力 +`/api/logs` 调用留痕 + 孩子/家长视角切换                   |

输入未注册的用户名会自动创建「孩子」账号并绑定同名空白档案。登录卡还有**注册**（选孩子/家长身份，家长需填孩子登录名绑定档案）与**忘记密码**（答对注册时设的密保问题即可重置，旧 token 全部作废）两个面板；孩子/家长演示账号预置密保「熊猫最爱吃什么？/ 竹子」，开箱可演找回流程（admin 不挂密保、也不允许走密保找回；用环境变量改过口令的种子账号同样不挂公开密保）。注册家长账号除了孩子的登录名，还要输入**孩子账号的密码**作为绑定凭证。所有调用大模型的接口共用一份额度（每账号 + 每 IP，5 分钟窗口），问候/晨报超额时退回本地兜底文案；未知名字自动注册按 IP 每小时限 10 个，新号密码至少 4 位。种子账号口令可用 `PANDA_CHILD/PARENT/ADMIN_PASSWORD` 覆盖（仅首次生成 users.json 时生效，线上部署务必改掉）；`data/aliases.seed.json` 可配登录名别名（如 `xiaodou`→`小豆`），别名只解析到已存在的账号、照常校验密码，绝不会绕过密码或蹭到别人的档案。除 `/api/health`、`/api/auth/*` 与静态页外，全部接口要求 `Authorization: Bearer <token>`；非 admin 只能访问自己绑定的孩子档案，越权一律 403；家长账号是孩子档案的只读视图（收件箱确认与传话筒除外）。密码与密保答案 PBKDF2 加盐存 `data/users.json`，token 仅以 SHA-256 哈希落 `data/tokens.json`（均不入库），默认 7 天有效、重启不掉登录。

### 部署说明（线上形态）

线上演示跑在自有云服务器上：**[https://xustalis.site/pandapal/](https://xustalis.site/pandapal/)**

- 形态：uvicorn 单进程绑 `127.0.0.1:8017`（systemd 单元 `pandapal.service`），nginx 443 把 `/pandapal/` 反代过去并剥离前缀；前端静态资源由 FastAPI 挂载在 `/static`
- 一键部署：`./deploy.sh` —— rsync 同步代码 → 服务端安装依赖 → 重启服务 → `curl /api/health` 健康检查
- 密钥与运行数据不入库、不同步：`.env`（LLM/TTS Key）、`data/users.json`、`data/tokens.json`、`data/settings.json` 均在 rsync 排除列表；服务端 `.env` 必须显式设置三个演示口令，缺一拒绝启动（防默认口令上线）
- 无数据库、无中间件依赖：任意能跑 Python 3.10+ 的机器都可部署；迁移 = 拷代码 + 拷 `data/` + 填 `.env`
- 环境变量清单与说明见 [`.env.example`](.env.example)（LLM 双协议与兜底、搜索、TTS/ASR、演示口令、上传限额等）

## 五、核心功能

### 对话与 Agent 执行

| 功能                                                                                                                                     | 模块                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 记忆驱动开场问候 · 晨间巡检（事务 + 临近截止 + 确定性"反复提起"建议）                                                                    | `GET /api/greeting` · `GET /api/briefing`                   |
| 闲聊通道（人设 + 活跃记忆注入 + 历史尾部 → 流式回复）                                                                                    | `server/main.py` `_chat_stream`                             |
| 意图分类（chat/explain/plan/relay/affair_update + 情绪）· FastTriage 免 LLM 快速路 · 分类结果缓存（同一句话 + 同一份简报 300s 内不重问） | `server/router.py`                                          |
| 讲懂（explain）：用孩子自己的经历打比方讲知识，类比素材来自记忆图谱                                                                      | `server/prompts.py` `EXPLAIN_RULE`                          |
| 任务拆解：LLM 输出 JSON DAG，校验去环重试                                                                                                | `server/planner.py`                                         |
| 按依赖并行执行 + SSE 实时状态                                                                                                            | `server/executor.py`                                        |
| 结构化卡片合成 + 出卡前判官自检（"实质回应孩子了吗"，不过带意见重出一次，原卡保底）                                                      | `server/synth.py` + `server/main.py` `_supervise_card`      |
| 先问清楚再动手：需求缺关键信息 → planner 输出`{"clarify": …}` 反问；原请求挂 `pending_clarify`，下一句合并重走完整管线                   | `server/planner.py` + `server/main.py`                      |
| 代办文书（"帮我写份自我介绍/发言稿"→LLM 真写全文→文稿卡+落盘挂回事务）                                                                   | `server/actions.py` `draft`                                 |
| 长文稿管线（论文/报告/作文）：提纲定结构 → 各节并行生成 → 拼 markdown（单节失败如实标缺）                                                | `server/actions.py` `_write_paper` + `prompts.py` `PAPER_*` |
| 交付物落盘：draft 同时落成`files/` 里的 .docx 真文件（失败退 .md），卡片一键下载                                                         | `_draft_to_file` + `GET /api/files/{id}/content?download=1` |
| 文稿修订环："把结尾改改/帮我重写"对着 48h 内的稿子就地改写（不重走规划管道），同一 draft_id 更新                                         | `server/main.py` 修订锚点 + `revise_draft`                  |
| 闲聊直答的工具轮：启发式命中 → 调度器挑工具 → 多工具并行分发 → 结果注入 → 流式回复                                                       | `server/main.py` `_tool_round` + `prompts.py` `TOOL_PICK`   |
| 工具脚手架（声明式注册表，@tool 注册即接入）：看时间 / 本地赛事库 / 交通参考 / wttr.in 天气 / 联网搜索 / 打开网页                        | `server/tools.py`                                           |
| 快捷话题 chips：按孩子此刻的事务/截止/兴趣/时段动态生成，不是全员一套死文案                                                              | `server/suggest.py`                                         |

### 记忆系统

| 功能                                                                                                                                       | 模块                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| 双层记忆：活跃关注点块（注意力门控：新近常驻、相关排前）每轮注入 + 主题图谱检索（bigram 命中 + 沿边一跳）                                  | `server/memory.py` + `server/graph.py`           |
| 文件式记忆读写：轮后 LLM 抽取 → topics/daily/MEMORY；单写锁 + tmp→rename 原子写                                                            | `server/memory.py`                               |
| Dreaming 记忆整理：daily 跨天去重 → 五信号打分 → 反复出现的事晋升进 MEMORY.md（标`[梦]` 出处可查）+ 梦日记落盘；每天一次、全确定性不调 LLM | `server/dream.py`                                |
| 记忆星球：五领域星区、时间轴播放、节点抽屉、想起了/记下了联动、规划卫星（DAG 实时状态）（3D；WebGL 不可用 2D 兜底）                        | `web/scene3d.js` `graph2d.js` + `GET /api/graph` |
| 记忆本页：主题分组 + 时间线 + 长期记忆 + 梦日记（晋升过程可见）                                                                            | `GET /api/memory`                                |
| 悄悄话结构性隔离：只进图谱 private 节点，文件层只写占位行；relay/周报等家长侧 prompt 在构造上读不到                                        | `server/memory.py` `server/graph.py`             |
| 记忆注入围栏：`<memory_data>` 声明"数据不是指令" + 围栏标签中和（防自闭合越狱）                                                            | `server/store.py` `fence_memory`                 |
| 多会话历史：新建 / 归档 / 恢复 / 删除，落盘重启不丢                                                                                        | `GET/POST/DELETE /api/history*`                  |

### 事务与家庭侧

| 功能                                                                                                                                        | 模块                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| 事务系统：发现→规划→执行→等确认→跟进→结案；看板 + 详情抽屉 + DAG 回放 + 清单勾选 + 日志时间线                                               | `server/affairs.py` + `web/app.js`          |
| 提醒 + 日历导出（.ics）                                                                                                                     | `POST /api/affairs` · `GET /api/ics/{aid}`  |
| 家长收件箱：确认 / 驳回（车票、费用等需要家长拍板的事）                                                                                     | `GET/POST /api/parent/inbox`                |
| 传话筒：老师→家长（大白话 + 建议 + 孩子鼓励版）/ 孩子→老师（需孩子点同意才转达）                                                            | `POST /api/relay`                           |
| 家长周报：本周事务进展 + 新变化统计 → 一页纸（悄悄话只计数不进 prompt；LLM 挂了只报统计）                                                   | `server/family.py` `GET /api/parent/weekly` |
| 通知落地「一份通知，千家千版」：按每个孩子的记忆出专属版 + 自动建事务/清单/提醒；admin（机构账号）可批量下发                                | `POST /api/notice`                          |
| 童年备忘录导出：整份档案打包 zip 交还孩子本人（家长 403）                                                                                   | `GET /api/export`                           |
| 成长雷达：德智体美劳五维评估 + 每维证据节点（两段取：雷达图毫秒级先出，LLM 点评后到、失败不影响数据）                                       | `GET /api/growth`                           |
| 梦想频道：接住孩子说的梦想并落成记忆                                                                                                        | `POST /api/dream`                           |
| 多模态附件：上传图片/PDF/Word/Excel/PPT/文本（拖拽、点选或粘贴），图片走视觉、扫描件 PDF 渲染成图、文档抽取正文进上下文；跨轮可追问、可管理 | `server/files.py` + `POST /api/files`       |

### 界面与形态

| 功能                                                                                                                               | 模块                                     |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| 3D「竹林小屋」+ 低多边形熊猫管家（呼吸/眨眼/写字/开心等状态动画），全部用基础几何体拼装、无外部素材版权问题                        | `web/scene3d.js` `panda3d.js`            |
| 降级：WebGL 不可用或场景初始化失败 → 自动切 2D 图谱与 SVG 熊猫，数据与交互不变                                                     | `web/graph2d.js` `panda.js`              |
| 家长视角：白天配色、悄悄话节点整体隐藏、收件箱/传话筒/周报                                                                         | `web/app.js`                             |
| PWA：可添加到主屏幕；断网时记忆本/事务/星球用缓存撑起，AI 端点不缓存（断网如实停答）                                               | `web/sw.js` + `web/manifest.webmanifest` |
| 语音链路：管家朗读（口播稿先洗成口语、限长收尾）+ 音色档案 voice.json（可对话调整）+ 语音识别双路径（浏览器优先、服务端 ASR 兜底） | `server/tts.py` `stt.py` `voice.py`      |
| admin 后台：调用留痕校验 / API 配置（改完即生效）/ 用户管理 / 档案内容 / 数据文件                                                  | `server/admin.py`                        |
| 自托管字体 + 双栈排版（UI 无衬线、管家的话衬线）                                                                                   | `web/fonts/` + `style.css`               |

### 可靠性与验真

| 功能                                                                                                                                                                           | 模块                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ |
| LLM 三层可靠性：错误分级退避重试（429 换 Key、5xx/断网指数退避）、双口径熔断（Key 级 / 端点级分开记账）、异构兜底端点（可切另一家服务商）；流式只在未吐 token 前重试防回复重复 | `server/llm.py`                |
| 调用留痕防篡改：`llm_calls.jsonl` 每行带前一行 sha256 哈希链，`GET /api/logs/verify` 逐行校验改/删/换序                                                                        | `server/llm.py` `verify_chain` |
| 鉴权与权限矩阵：PBKDF2 加盐、token 只存哈希、非 admin 越权 403、限频                                                                                                           | `server/auth.py`               |
| **降级不降真**：DAG 规划失败 → 单 LLM 直出卡片（只跳拆解展示，绝不跳生成）；节点失败 → 标记后继续；工具失败/没搜到 → 如实告诉孩子"没查到"，不编造                              | 全链路                         |

## 六、大模型使用说明

- 模型：由 `.env` 中 `LLM_MODEL` 指定（演示环境当前为 `deepseek-flash`，走 OpenAI 兼容端点；兼容任意 OpenAI 协议端点，也支持 Anthropic Messages 协议）
- 调用方式：`server/llm.py` 统一封装双协议客户端；一轮规划型对话是 分类→拆解→执行→整理 四段，闲聊可能多一轮联网工具调用，加上轮后的记忆抽取，最多七八次调用
- 可靠性：瞬时错误（断网/超时/5xx）同候选指数退避重试；429 优先换 Key；连续失败熔断 30s 跳过死端点；`LLM_API_KEY3`+`LLM_BASE_URL2`/`LLM_MODEL2`/`LLM_PROTOCOL2` 可配异构兜底服务商，主端点整体停服也能活。留痕里逐次尝试可见，并记录 provider 回报的真实 token 用量与截断标记
- 单轮耗时提示：`planner` 与 `synth` 是最重的两段（各自几十秒），界面会在这两段显示「正在拆解要办的事…」「快好了，正在整理成方案…」，属正常等待
- **赞助商 API 使用清单**：LLM API（见 `.env`，OpenAI 兼容/Anthropic 兼容）、语音合成与识别 [小米 MiMo](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5)（`TTS_API_KEY`，可在 admin 后台「API 配置」里改、立即生效；Key 限时免费；留空则整条语音链路静默跳过）、天气 [wttr.in](https://wttr.in)（免费无需 Key）、联网搜索（配置 `SEARCH_API_KEY`+`SEARCH_BASE_URL` 走 Tavily 兼容端点；未配置时用必应网页结果解析，无需 Key）

## 七、项目结构

```
├── server/          # FastAPI 后端（auth/sessions/router/planner/executor/synth/actions/memory/graph/affairs/family/files/dream/llm/tts/stt/voice/tools/suggest/admin 等模块）
├── web/             # 零构建前端（app.js / scene3d.js / graph2d.js / panda3d.js / panda.js / admin.js / splash.js / style.css / sw.js + vendor/ + fonts/）
├── data/            # 文件式存储：child_xiaodou/ 演示档案 + race_db.json / transport_db.json + logs/
├── docs/            # 赛道方案、PRD、设计方案与契约、排查报告、三张架构图（SVG）
├── tests/           # 测试套件 + RESULTS.md 通过记录 + results/ 原始输出
└── README.md
```

## 八、测试说明

**最近一次全量运行记录（场景 / 输入 / 预期 / 实际 + 真实 LLM 调用留痕 + 断网验真）见 [`tests/RESULTS.md`](tests/RESULTS.md)**，原始输出在 `tests/results/`。

```bash
# 不花 Key 的离线自检（monkeypatch LLM，指向临时沙箱，不碰真实 data/）：
.venv/bin/python tests/test_offline.py

# 记忆层自检：不联网不起服务，直接打 MemoryStore 读写
.venv/bin/python tests/test_memory.py

# 家庭侧服务离线自检：周报/通知落地/批量下发/导出 + 悄悄话不进 prompt + 越权 403
.venv/bin/python tests/test_family.py

# LLM 可靠性层自检：错误分级/退避/熔断/兜底/usage 记账（全离线 mock）
.venv/bin/python tests/test_llm_resilience.py

# 前端静态一致性：id/图标/括号配平，暂停键与断网条等关键钩子是否接上
.venv/bin/python tests/test_web_static.py

# 暂停键布局实测：本机 Chrome 无头模式量桌面/窄屏下输入栏按钮的矩形
.venv/bin/python tests/test_pause_layout.py

# 续写指令路由 + FastTriage 快速路：暂停后点「继续」必须走闲聊，
# 零信号短闲聊不花 LLM 第一跳，办事信号 veto 回 LLM
.venv/bin/python tests/test_router.py

# Dreaming 记忆整理：跨天重复事实晋升 MEMORY.md、梦日记、幂等、空档案
.venv/bin/python tests/test_dream.py

# 多模态附件：类型识别/内容抽取/配额/提示注入围栏/两种协议的图片消息/上传接口
.venv/bin/python tests/test_files.py

# 后台管理离线自检：admin 全套端点 + 权限闸门（沙箱数据目录）
.venv/bin/python tests/test_admin.py

# 语音链路离线回归：口播稿归一化、音色档案、缓存防目录穿越（全离线 mock）
.venv/bin/python tests/test_tts.py

# 安全回归（pytest）：token 只存哈希、XFF 只信本机反代、限频表上限、天气参数转义
.venv/bin/python -m pytest tests/test_security.py -v

# 3D 熊猫模块（node:test）：姿态/状态机
node tests/test_panda3d.mjs

# 服务启动后的端到端用例（真实打接口 + 真实 LLM）：
.venv/bin/python tests/test_api.py --base http://localhost:8000
```

`test_api.py` 覆盖：健康检查、登录/注册/找回、问候（含 SSE 流式）、闲聊流式、规划链全链路（plan→node→card）、
记忆本与沉淀落盘、图谱（含家长视角过滤 + 时间轴切片）、事务详情/更新（POST/PATCH）、清单、家长收件箱、
传话筒、日历导出、成长雷达、梦想、日志分页、双会话并发隔离与权限矩阵。
`test_offline.py` 覆盖：上述主链路的离线版（SSE 事件顺序、悄悄话隔离、账号越权防线、executor 作用域）+
登录 → 晨报 → plan 全链路 → 记忆/事务/清单落盘 → 图谱视角白名单 → 家长只读边界 → 别名防绕过 →
撞档隔离 → query token 收窄 → 限频 → 历史落盘与重启恢复 → 收件箱裁决联动 → 事务去重 → 安全/缓存响应头。
`test_memory.py` 覆盖：注入字符预算与活跃主题择优、检索相关度/门槛/去重、归档累计计数与行数上限、读缓存写后失效。
`test_web_static.py` / `test_pause_layout.py` 覆盖：前端 id/图标引用与括号配平、"暂停键在输入栏内且与发送键同位置"、
窄屏可见、断网条与「重试/继续」入口、附件入口与文件卡都接上了；`test_router.py` 覆盖续写指令的路由（不误建事务、跳过多余的 LLM 分类调用）。
`test_files.py` 覆盖：扩展名/MIME 识别与文件名消毒（路径穿越只留在展示名里）、文本/GBK/CSV/Word/Excel/PDF 取正文、
扫描件如实告知读不出、图片压缩到 1280 长边并保持 16 倍数、附件配额淘汰最旧、正文注入的字符预算与 `<file_data>` 围栏、
正文落盘封顶（索引不存全文，原长走 `text_chars`）、上传限频、OpenAI/Anthropic 两种协议的图片消息构造、
上传接口的 415/413/400/403/404/429 边界、带附件的一轮对话（含悄悄话不带附件）。
`test_family.py` 覆盖：周报/通知落地/批量下发/导出 + 悄悄话原文不进任何 prompt + 越权 403；
`test_dream.py` 覆盖跨天重复事实晋升、梦日记、幂等与空档案；`test_llm_resilience.py` 覆盖错误分级、退避、熔断、异构兜底与 usage 记账；
`test_admin.py` 覆盖 admin 权限闸门、配置热生效、用户管理护栏、档案/数据文件边界；`test_tts.py` / `test_tts_e2e.py` 覆盖口播稿归一化、
音色档案白名单、voice 事件时序与缓存目录穿越防护；`test_security.py` 覆盖 token 只存哈希与旧明文迁移、XFF 信任边界、限频表硬上限、天气城市参数 URL 转义。

## 九、团队成员

##### 徐浩博 leader 开发

##### 臧泰运 开发

##### 张磊 测试

##### 冯钰骅 设计

## Roadmap

新形态与新业态详见 [`docs/新形态与新业态.md`](docs/新形态与新业态.md)（PWA ✅ · 通知落地 ✅ · 家长周报 ✅ · 童年备忘录 ✅ · IM 渠道/撮合/升学素材 🗺）。

APP/手表/电子宠物形态 · 家长端/老师端 · 企业接口直连（订票等真实操作）· 常驻主动规划 · 私有化部署（数据即文件，孩子数据不出自家服务器）
