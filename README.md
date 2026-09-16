# FDE 转型实战特训 · 岭湾实验站

岭湾电力客户服务平台（教学合成案例）配套的**在线实验站**：把 `02_实验手册/` 的分册手册装配成可在线阅读的实验页，并提供 7 个自包含的交互向导与 5 份知识文档语料。

> 本材料为培训教学合成的虚构材料，企业与人员均为化名，条文与数值为教学示意值，不对应任何真实机构、制度或业务数据；实务请以现行有效规定为准。

## 一、站点内容

| 板块 | 说明 |
|---|---|
| 📘 实验手册 | 7 个实验，编号连续（实验一 · 需求调研与解决方案框架／实验二 · 诉求智能分类系统／实验三 · 供电业务知识问答／实验四 · 工单分级路由工作流／实验五 · 综合系统 Agent（进阶）／实验六 · 综合证据评审与决策层汇报／实验七 · 复盘真实项目（可选）），支持章内目录、上一实验/下一实验翻页 |
| 🎮 实验向导 | 7 个自包含交互 HTML：角色定位游戏（实验一）／启动提示词向导（实验二·三·四·五）／评审与汇报工作台（实验六）／复盘向导（实验七）。**导航里两组用同一份实验名**，向导一栏后面的标签标明工具类型 |
| 📚 知识文档语料 | 5 份岭湾业务知识文档：3 份 md 在线可读，docx 与 pdf 原样下载，另有 `policy-docs/lab3-policy-rag-docs.zip` 一次打包下载全部 5 份 |
| 🧰 验收工具 | 数据包内 `验收/evaluate.py`：离线桩／学员实现／在线模型三条路径，出指标与 DoD 判定表 |

## 二、目录结构

```
lingwan/                            # 站点仓库（也可作为课程包里的 09_实验网站 直接使用）
├── index.html                      # 主页：品牌栏 + 左侧导航 + iframe 内容区
├── handbook/                       # 实验手册页面（由 scripts/build.py 生成）
│   ├── index.html                  # 手册总览（七个实验卡片）
│   ├── lab1-requirements-brainstorm.html … lab7-migration-review.html   # 各实验分页
│   └── policy/                     # 知识文档在线阅读页 + 目录页
├── wizards/                        # 7 个交互向导（自包含，内联 CSS/JS）
├── policy-docs/                    # 知识文档原始文件（md/docx/pdf）＋ lab3-policy-rag-docs.zip（5 份打包）
├── _source/02_实验手册/             # 学员版手册源文件（构建 handbook/ 用；仓库自带，CI 才能重建）
├── scripts/build.py                # 构建脚本：读手册分册 md → 生成 handbook/
├── scripts/check_links.py          # 站点自检：本地链接与锚点是否全部有效
├── assets/vendor/mermaid.min.js    # 本地 mermaid（图渲染，无外网依赖）
├── .github/workflows/deploy.yml    # GitHub Pages 自动部署
└── README.md
```

**内容源单一**：手册页面不是手写的，而是 `scripts/build.py` 从手册分册 md 生成——改内容请改分册，然后重新构建，避免双处维护。脚本按以下顺序找源目录：课程包内同级 `../02_实验手册/`（优先）→ 仓库内 `_source/02_实验手册/`（独立仓库／CI 用）。

## 三、构建与本地预览

```powershell
# 1) 安装依赖（仅首次）
pip install markdown

# 2) 生成 handbook/ 与合订本
cd <课程包目录>\09_实验网站
python scripts/build.py

# 3) 本地预览
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

构建产物：`handbook/lab1-requirements-brainstorm.html … lab7-migration-review.html`、`handbook/index.html`、`handbook/policy/*.html`、根目录 `FDE转型实战特训-学员版实验手册合订本.md`（可由主页右上角下载）。

站点自检（改完链接或重建后都跑一次）：

```powershell
python scripts/check_links.py     # 本地链接与锚点全量校验，全通过则退出码 0
```

`policy-docs/lab3-policy-rag-docs.zip` 是手工打包的，内容改动后请重新压缩：

```powershell
Compress-Archive -Path "..\01_数据包\岭湾项目包\知识文档\*" -DestinationPath policy-docs\lab3-policy-rag-docs.zip -Force
```

## 四、部署上线（公网静态托管）

本目录是**纯静态站点**：无后端、无构建期依赖、无 CDN 外链，整目录可直接托管对外服务。**本站点就是放在公网给客户访问的**——内容全部是教学合成的虚构材料（企业与人员均为化名、数值为教学示意值），不含任何客户内部数据或真实信息。

**A. GitHub Pages（本仓库 `lingwan` 已按这条路配好）**

- 仓库：`https://github.com/cloudzun/lingwan`
- 线上地址：**`https://cloudzun.github.io/lingwan/`**
- 工作流：`.github/workflows/deploy.yml` —— 推送到 `main` 后自动 `pip install markdown` + `python scripts/build.py` + 发布到 Pages；
- 仓库 **Settings → Pages → Source** 需为 **GitHub Actions**（首次创建仓库后设置一次）。

日常改动只需：改 `_source/02_实验手册/` 里的分册 md（或向导/主页）→ `git add . && git commit -m "…" && git push`，一分钟后线上自动更新。

**B. 客户侧静态托管（对象存储 ／ CDN ／ nginx，公网或内网都行）**

把本目录整体上传即可，入口是 `index.html`。

- 改了手册分册的内容，上传前先在本地跑一次 `python scripts/build.py` 重新生成 `handbook/`（托管侧不需要 Python 环境——构建产物已随目录一起提供）；
- 所有链接均为相对路径，放在任意子路径下都不用改配置；主页用 iframe 嵌入向导页并按内容高度自适应；
- 需要单文件分发时，可把整个目录打成 zip 交给客户，解压即用。

## 五、自包含性与内容纪律

- **自包含**：mermaid 用本地 `assets/vendor/mermaid.min.js`，向导不引 CDN，页面不写外链——因此既能直接公网托管，也能在受限网络里双击打开照样能用。
- **只放虚构材料**：站点内容全部是教学合成的虚构材料，所以**可以且应当部署到公网**；唯一红线是**不要把真实客户数据或内部材料放进本目录**。
- **验收命令**（在数据包根目录执行）：
  ```
  python 验收\evaluate.py --task all --impl stub     # 离线桩基线（无需网络与 Key）
  python 验收\evaluate.py --task all --impl src      # 你的实现（读 ./src/handler.py）
  python 验收\evaluate.py --task all --impl api      # 在线模型（需环境变量 DEEPSEEK_API_KEY）
  ```
