#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — FDE 转型实战特训 · 岭湾实验站 构建脚本

作用：
1. 把 `02_实验手册/` 下的**分册学员版手册**装配成站点页面 `handbook/chN.html`
   （含章内目录、上一章/下一章、代码一键复制、mermaid 图渲染、表格样式）；
2. 生成 `handbook/index.html`（实验总览卡片）与 `handbook/policy/*.html`（知识文档在线阅读页）；
3. 生成 `FDE转型实战特训-学员版合订本.md`（把分册按顺序拼成一本，供下载）。

用法：python scripts/build.py
依赖：pip install markdown
"""
import html as html_mod
import os
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("缺少依赖：请先执行 pip install markdown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 手册源目录：课程包内是同级 ../02_实验手册；独立仓库（如 GitHub Pages 自动构建）用仓库内 _source/02_实验手册
_SIBLING = os.path.join(os.path.dirname(ROOT), "02_实验手册")
_BUNDLED = os.path.join(ROOT, "_source", "02_实验手册")
MANUAL_ROOT = _SIBLING if os.path.isdir(_SIBLING) else _BUNDLED
HANDBOOK = os.path.join(ROOT, "handbook")
POLICY_SRC = os.path.join(ROOT, "policy-docs")
ZIP_NAME = "lab3-policy-rag-docs.zip"
ZIP_PATH = os.path.join(POLICY_SRC, ZIP_NAME)
# 素材页上的打包下载（顺序即展示顺序）
ZIPS = [
    ("lab2-classify-kit.zip", "实验二素材包（分类口径 ＋ 25 条样本 ＋ 开发任务 ＋ 脚手架模板）"),
    ("lab3-policy-rag-docs.zip", "实验三语料包（5 份知识文档，一次打包）"),
]

# ---------- 页面样式与脚本（站点主题 / mermaid 渲染 / 代码一键复制） ----------
THEME = r"""
:root{
  --indigo:#1a237e; --indigo2:#283593; --indigo3:#3949ab; --indigo-soft:#5c6bc0;
  --amber:#ffb300; --amber-dark:#b28704; --amber-bg:rgba(255,179,0,.08);
  --ink:#263238; --ink-soft:#546e7a; --muted:#78909c; --line:#e2e8f0;
  --bg:#ffffff; --bg-soft:#fafbfc; --code-bg:#101f4d;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Roboto","PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;color:var(--ink);background:var(--bg);line-height:1.75;font-size:15px}
a{color:var(--amber-dark);text-decoration:none}
a:hover{color:var(--indigo);text-decoration:underline}
.hb-top{background:linear-gradient(135deg,#1a237e 0%,#283593 55%,#3949ab 100%);color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.hb-top .brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.5px;font-size:15px}
.hb-top .brand .dot{width:10px;height:10px;border-radius:50%;background:var(--amber);flex:none}
.hb-top .brand small{font-weight:400;font-size:12px;opacity:.85;margin-left:6px}
.hb-top a{color:#fff;font-size:13px;font-weight:500}
.hb-top a:hover{color:var(--amber);text-decoration:none}
.ch-nav{background:#fff;border-bottom:1px solid var(--line);padding:8px 24px;display:flex;gap:4px;flex-wrap:wrap;align-items:center}
.ch-nav a{font-size:13px;font-weight:500;color:var(--muted);padding:6px 12px;border-radius:4px;white-space:nowrap;border-bottom:2px solid transparent}
.ch-nav a:hover{color:var(--indigo);text-decoration:none;background:var(--bg-soft)}
.ch-nav a.on{color:var(--indigo);font-weight:700;border-bottom-color:var(--amber)}
.ch-nav a.home{margin-left:auto;color:var(--amber-dark)}
.hb-wrap{max-width:none;margin:0;padding:28px 24px 60px;display:flex;gap:40px;align-items:flex-start;justify-content:space-between}
.hb-main{flex:1;min-width:0;max-width:900px}
aside.hb-toc{width:320px;flex:none;position:sticky;top:24px;background:var(--bg-soft);border:1px solid var(--line);border-radius:6px;border-left:3px solid var(--amber);padding:16px 18px;max-height:calc(100vh - 60px);overflow:auto}
aside.hb-toc b{font-size:11.5px;color:var(--muted);display:block;margin-bottom:8px;letter-spacing:1.5px;text-transform:uppercase}
aside.hb-toc ul{list-style:none;padding-left:0}
aside.hb-toc a{display:block;font-size:13px;padding:5px 8px;border-radius:4px;color:var(--ink-soft);font-weight:500}
aside.hb-toc a:hover{background:#fff;color:var(--indigo);text-decoration:none}
aside.hb-toc ul ul a{padding-left:18px;font-weight:400;color:var(--muted);font-size:12.5px}
.hb-main h1{color:var(--indigo);font-size:26px;line-height:1.4;margin:4px 0 6px;padding-bottom:10px;border-bottom:1px solid var(--line);font-weight:700;letter-spacing:.5px}
.hb-main .ch-role{font-size:12px;color:var(--amber-dark);font-weight:700;letter-spacing:1.5px;margin-bottom:18px}
.hb-main h2{color:var(--indigo);font-size:20px;margin:34px 0 12px;padding-left:12px;border-left:4px solid var(--amber);font-weight:600}
.hb-main h3{color:var(--indigo2);font-size:17px;margin:24px 0 10px;font-weight:600}
.hb-main h4{color:var(--indigo);font-size:15px;margin:18px 0 8px;font-weight:600}
.hb-main p{margin:10px 0}
.hb-main ul,.hb-main ol{margin:10px 0;padding-left:26px}
.hb-main li{margin:5px 0}
.hb-main strong{color:var(--indigo);font-weight:700}
.hb-main blockquote{background:var(--bg-soft);border:1px solid var(--line);border-left:4px solid var(--indigo-soft);border-radius:4px;padding:12px 16px;margin:14px 0;color:var(--ink-soft)}
.hb-main blockquote p{margin:6px 0}
.hb-main blockquote blockquote{background:#f1f3f6;border-left-color:var(--amber)}
.hb-main code{background:var(--bg-soft);color:var(--amber-dark);padding:2px 6px;border-radius:4px;font-size:13px;font-family:"Cascadia Mono","Consolas",monospace}
.hb-main pre{background:var(--code-bg);border-radius:6px;padding:16px;overflow:auto;margin:14px 0;line-height:1.65}
.hb-main pre code{background:none;color:#e8eaf6;padding:0;font-size:12.8px;white-space:pre}
.code-wrap{position:relative;margin:14px 0}
.code-wrap pre{margin:0}
.code-copy{position:absolute;top:8px;right:8px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);color:#e8eaf6;font-size:11.5px;font-weight:600;padding:4px 10px;border-radius:4px;cursor:pointer;opacity:.65;transition:opacity .15s,background .15s;font-family:"Roboto","PingFang SC",sans-serif;line-height:1.4}
.code-copy:hover{opacity:1;background:var(--amber);border-color:var(--amber);color:#1a237e}
.code-copy.copied{background:var(--amber);border-color:var(--amber);color:#1a237e;opacity:1}
.hb-main table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;background:#fff}
.hb-main th{background:var(--indigo3);color:#fff;padding:9px 12px;text-align:left;font-weight:600}
.hb-main td{border:1px solid var(--line);padding:8px 12px;vertical-align:top}
.hb-main tr:nth-child(even) td{background:var(--bg-soft)}
.hb-main tr:hover td{background:var(--amber-bg)}
.hb-main hr{border:none;border-top:1px solid var(--line);margin:26px 0}
.hb-main img{max-width:100%;border-radius:4px}
.hb-pager{display:flex;justify-content:space-between;gap:14px;margin-top:40px;padding-top:18px;border-top:1px solid var(--line)}
.hb-pager a{flex:1;background:var(--bg-soft);border:1px solid var(--line);border-radius:6px;padding:14px 18px;color:var(--ink);font-weight:600;font-size:14px}
.hb-pager a:hover{border-color:var(--amber);text-decoration:none}
.hb-pager a small{display:block;font-weight:400;color:var(--muted);font-size:12px;margin-bottom:3px}
.hb-pager a.next{text-align:right}
.hb-pager a .dir{color:var(--amber-dark);font-weight:700}
.ov-hero{max-width:none;margin:0;padding:36px 28px 8px}
.ov-hero h1{color:var(--indigo);font-size:26px;line-height:1.4;font-weight:700;letter-spacing:.5px}
.ov-hero .tag{display:inline-block;color:var(--amber-dark);font-weight:700;font-size:12px;letter-spacing:2px;margin-bottom:10px}
.ov-hero p{color:var(--ink-soft);font-size:14px;margin-top:8px;max-width:900px}
.ov-cards{max-width:none;margin:0;padding:16px 28px 46px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.ov-card{background:#fff;border:1px solid var(--line);border-radius:6px;padding:20px;display:block;color:var(--ink);transition:border-color .18s}
.ov-card:hover{border-color:var(--amber);text-decoration:none}
.ov-card .no{font-size:11.5px;font-weight:700;letter-spacing:1.5px;color:var(--amber-dark);margin-bottom:6px}
.ov-card h3{color:var(--indigo);font-size:16px;margin-bottom:6px;line-height:1.4;font-weight:600}
.ov-card p{font-size:13px;color:var(--ink-soft);line-height:1.6}
.ov-card .meta{margin-top:10px;font-size:11.5px;color:var(--muted);display:flex;gap:8px;flex-wrap:wrap}
.ov-card .meta span{background:var(--bg-soft);border:1px solid var(--line);border-radius:4px;padding:2px 8px;font-weight:500}
.ov-card.zip-card{background:linear-gradient(180deg,#fff8e8,#fff);border-color:var(--amber)}
.ov-card.zip-card .no{color:var(--amber-dark)}
.ov-intro{max-width:none;margin:0;padding:6px 28px 0}
.mermaid{text-align:center;margin:18px 0;overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px}
.mermaid svg{max-width:100%;height:auto}
@media(max-width:760px){
  .hb-wrap{flex-direction:column;gap:18px}
  aside.hb-toc{width:100%;position:static;max-height:280px}
  .hb-main h1{font-size:21px}
}
"""

MERMAID_JS = r"""
<script>
(function(){
  function initMermaid(){
    var blocks = document.querySelectorAll('pre code.language-mermaid');
    if(!blocks.length || typeof mermaid === 'undefined') return;
    blocks.forEach(function(code){
      var div = document.createElement('div');
      div.className = 'mermaid';
      div.textContent = code.textContent;
      code.parentNode.replaceWith(div);
    });
    mermaid.initialize({startOnLoad:false, theme:'default', securityLevel:'loose', flowchart:{htmlLabels:true}});
    mermaid.run({querySelector:'.mermaid'});
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', initMermaid);
  } else {
    initMermaid();
  }
})();
</script>
"""

COPY_JS = r"""<script>
(function(){
  function fallbackCopy(text){
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try{ document.execCommand('copy'); }catch(e){}
    document.body.removeChild(ta);
  }
  function addCopyButtons(){
    document.querySelectorAll('.hb-main pre, .ov-intro pre').forEach(function(pre){
      if (pre.querySelector('.code-copy')) return;
      var code = pre.querySelector('code');
      if (!code) return;
      if (code.className && code.className.indexOf('language-mermaid') !== -1) return;
      var wrap = document.createElement('div');
      wrap.className = 'code-wrap';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      var btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'code-copy'; btn.textContent = '复制';
      btn.setAttribute('aria-label', '复制代码');
      btn.addEventListener('click', function(){
        var text = code.innerText;
        function done(){ btn.textContent = '已复制 ✓'; btn.classList.add('copied');
          setTimeout(function(){ btn.textContent = '复制'; btn.classList.remove('copied'); }, 1600); }
        if (navigator.clipboard && navigator.clipboard.writeText){
          navigator.clipboard.writeText(text).then(done, function(){ fallbackCopy(text); done(); });
        } else { fallbackCopy(text); done(); }
      });
      wrap.appendChild(btn);
    });
  }
  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', addCopyButtons); } else { addCopyButtons(); }
})();
</script>"""
BRAND = "FDE 转型实战特训"
SITE = "岭湾实验站"

# ---------- 实验清单（顺序即站点导航顺序；src 指向 02_实验手册 下的学员版分册） ----------
CHAPTERS = [
    dict(key="lab1-requirements-brainstorm", no="实验一", title="需求调研与解决方案框架", tag="Echo",
         role="🧭 Echo · 判断线 · 不用 AI",
         desc="用三个思维脚手架拆需求：四类失败模式挖风险、四层决策链理干系人、能力金字塔选路线；产出《解决方案框架》。",
         src="lab1-requirements-brainstorm/lab1-requirements-brainstorm.md"),
    dict(key="lab2-classifier", no="实验二", title="诉求智能分类系统", tag="跑通",
         role="🤖 Delta · 施工线 · 简单需求",
         desc="以「客户诉求智能分类」这一件事，把 gstack 八环节完整跑一遍：写启动提示词 → 一环一停 → 验收 → 复盘。",
         src="lab2-classifier/lab2-classifier.md"),
    dict(key="lab3-policy-rag", no="实验三", title="供电业务知识问答", tag="Delta",
         role="🤖 Delta · 施工线 · 答案可追溯",
         desc="RAG 最小实现：先检索后生成、答案带文件名与条款号、检索不到必须拒答，双指标验收。",
         src="lab3-policy-rag/lab3-policy-rag.md"),
    dict(key="lab4-routing-workflow", no="实验四", title="工单分级路由工作流", tag="Delta",
         role="🤖 Delta · 施工线 · 自动化边界",
         desc="按动作判三档：咨询自动答复、跨专业协同查职责库、敏感真暂停转人工；敏感件零漏判是底线。",
         src="lab4-routing-workflow/lab4-routing-workflow.md"),
    dict(key="lab5-cooperative-agent", no="实验五", title="综合系统 Agent（进阶）", tag="进阶",
         role="🚀 进阶 · 课后/选做 · Agentic Loop",
         desc="把完整需求一次做成：四类任务走不同路径、信息不足会追问、敏感主动交还给人；十项标准＋五项硬验收。",
         src="lab5-cooperative-agent/lab5-cooperative-agent.md"),
    dict(key="lab6-review-and-report", no="实验六", title="综合证据评审与决策层汇报", tag="全队",
         role="🧑‍🤝‍🧑 全队 · 判断线收口",
         desc="两层验收、能力回注、交付决策（Go／Conditional Go／Continue Pilot／No-Go）、十段汇报与质询。",
         src="lab6-review-and-report/lab6-review-and-report.md"),
    dict(key="lab7-migration-review", no="实验七", title="复盘真实项目（可选）", tag="可选",
         role="🔁 可选 · 迁移到真实工作",
         desc="把课堂方法迁移到你自己手上的一件真事：准入 Gate、事实底账、双视角复盘、下一阶段决策。",
         src="lab7-migration-review/lab7-migration-review.md"),
]


def mermaid_inject(body_html):
    if "language-mermaid" not in body_html:
        return ""
    return '<script src="../assets/vendor/mermaid.min.js"></script>\n' + MERMAID_JS


def nav_html(active_key, ch_prefix="", root_prefix="../"):
    """顶部实验切换导航：ch_prefix 用于指向同级实验页，root_prefix 用于回到站点首页。"""
    items = []
    for ch in CHAPTERS:
        on = " on" if ch["key"] == active_key else ""
        items.append(f'<a class="ch-nav-item{on}" href="{ch_prefix}{ch["key"]}.html">{ch["no"]} · {ch["title"]}</a>')
    return ('<div class="ch-nav">' + "".join(items) +
            f'<a class="home" href="{root_prefix}index.html">← 返回实验站</a></div>')


def page(title, body, toc, prev, next_, active_key, extra_head="", ch_prefix="", root_prefix="../"):
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_mod.escape(title)} · {BRAND} {SITE}</title>
<style>{THEME}</style>
{extra_head}
</head><body>
<header class="hb-top">
  <div class="brand"><span class="dot"></span>{BRAND} · {SITE}<small>岭湾电力客户服务平台（教学合成案例）</small></div>
  <a href="{root_prefix}index.html">实验站首页</a>
</header>
{nav_html(active_key, ch_prefix, root_prefix)}
<div class="hb-wrap">
  <main class="hb-main">
    {body}
    <div class="hb-pager">{prev}{next_}</div>
  </main>
  <aside class="hb-toc"><b>本章目录</b>{toc}</aside>
</div>
{COPY_JS}
</body></html>"""


def md_to_html(text):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list", "nl2br"],
                           extension_configs={"toc": {"permalink": False}})
    return md.convert(text), md.toc


def strip_first_h1(text):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            return "\n".join(lines[:i] + lines[i + 1:])
    return text


def read_manual(rel):
    path = os.path.join(MANUAL_ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        return None
    return open(path, encoding="utf-8").read()


def build_chapters():
    pages = []
    for i, ch in enumerate(CHAPTERS):
        raw = read_manual(ch["src"])
        if raw is None:
            print(f"[跳过] 找不到手册：{ch['src']}")
            continue
        body_md = strip_first_h1(raw)
        body_html, toc_html = md_to_html(body_md)
        head = (f'<div class="ch-role">{html_mod.escape(ch["role"])}　|　{html_mod.escape(ch["tag"])}</div>'
                f'<h1>{html_mod.escape(ch["no"] + " · " + ch["title"])}</h1>')
        pages.append(dict(ch=ch, key=ch["key"], title=ch["no"] + " · " + ch["title"],
                          body=head + body_html, toc=toc_html))
    return pages


def build_handbook(pages):
    os.makedirs(HANDBOOK, exist_ok=True)
    for i, pg in enumerate(pages):
        prev = next_ = ""
        if i > 0:
            p = pages[i - 1]
            prev = (f'<a class="prev" href="{p["key"]}.html"><small><span class="dir">← 上一实验</span></small>'
                    f'{html_mod.escape(p["title"])}</a>')
        if i < len(pages) - 1:
            n = pages[i + 1]
            next_ = (f'<a class="next" href="{n["key"]}.html"><small><span class="dir">下一实验 →</span></small>'
                     f'{html_mod.escape(n["title"])}</a>')
        extra = mermaid_inject(pg["body"])
        html_out = page(pg["title"], pg["body"], pg["toc"], prev, next_, pg["key"], extra)
        path = os.path.join(HANDBOOK, f'{pg["key"]}.html')
        open(path, "w", encoding="utf-8", newline="\n").write(html_out)
        print(f"[生成] handbook/{pg['key']}.html  ← {pg['ch']['src']}")

    # ---- 总览页 ----
    cards = []
    for pg in pages:
        ch = pg["ch"]
        cards.append(
            f'<a class="ov-card" href="{ch["key"]}.html"><div class="no">{html_mod.escape(ch["no"])} · {html_mod.escape(ch["tag"])}</div>'
            f'<h3>{html_mod.escape(ch["title"])}</h3><p>{html_mod.escape(ch["desc"])}</p>'
            f'<div class="meta"><span>{html_mod.escape(ch["role"])}</span></div></a>')
    cards.append('<a class="ov-card" href="policy/index.html"><div class="no">素材</div><h3>知识文档（政策语料）</h3>'
                 '<p>5 份岭湾电力业务知识文档（供电营业规则／电价与电费／业扩报装／供电服务规范／分布式光伏并网），'
                 '在线可读，docx 与 pdf 可下载，也可一次打包下载。</p><div class="meta"><span>RAG 素材</span><span>5 份</span></div></a>')
    cards.append('<a class="ov-card" href="../wizards/lab2-prompt-wizard.html"><div class="no">工具</div><h3>实验向导（交互工具）</h3>'
                 '<p>角色定位游戏 / 启动提示词向导 / 实验工作台：分步填写、一键复制提示词、参考答复对照。</p>'
                 '<div class="meta"><span>7 个向导</span><span>可离线用</span></div></a>')
    ov = (f'<div class="ov-hero"><div class="tag">学员版 · 实验手册</div><h1>{BRAND} · 实验手册总览</h1>'
          f'<p>本课程实验由七个实验组成：一头一尾是判断线（实验一 · 需求调研与解决方案框架、'
          f'实验六 · 综合证据评审与决策层汇报），中间是施工线（实验二 · 诉求智能分类系统，'
          f'以及实验三 · 供电业务知识问答、实验四 · 工单分级路由工作流两个进阶场景）；'
          f'实验五为进阶（综合系统 Agent（进阶），课后/选做），实验七为可选（复盘真实项目）。'
          f'每个实验都给出逐环节步骤、关键决策点、产出物与可执行的验收命令。</p>'
          f'<p>验收工具：在数据包根目录执行 <code>python 验收\\evaluate.py --task all --impl stub</code>'
          f'（离线桩基线）、<code>--impl src</code>（你的实现）、<code>--impl api</code>（在线模型，需 DEEPSEEK_API_KEY）。</p>'
          f'<p><b>课前环境与网络（国内）：</b>'
          f'1. <b>Python 包下载</b>建议用清华镜像源——<code>pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple</code>；'
          f'2. <b>GitHub 访问</b>如不通畅用加速代理 <code>https://ghfast.top</code>（克隆时 URL 前缀加 <code>https://ghfast.top/</code>）——'
          f'<code>git clone https://ghfast.top/https://github.com/garrytan/gstack.git</code>。'
          f'实验二／三／四的向导里都有「安装 gstack」页，两条路线与这两条网络配置都在上面，可直接复制。</p>'
          f'<p>本课程的所有实验均经过设计与测试；但受限于不同大模型（模型版本、行为差异）与不同 Coding Agent（工具兼容性）的具体差异，'
          f'实验在运行中可能出现偏差（如准确率波动、命令不兼容、输出格式差异等）。请以实际运行结果为准，灵活调整。</p></div>'
          f'<div class="ov-cards">{"".join(cards)}</div>')
    overview = page("实验手册总览", ov, "", "", "", "", "")
    open(os.path.join(HANDBOOK, "index.html"), "w", encoding="utf-8", newline="\n").write(overview)
    print("[生成] handbook/index.html  ← 实验总览")


def build_policy():
    out = os.path.join(HANDBOOK, "policy")
    os.makedirs(out, exist_ok=True)
    items = []
    for fn in sorted(os.listdir(POLICY_SRC)) if os.path.isdir(POLICY_SRC) else []:
        if fn == ZIP_NAME:
            continue
        path = os.path.join(POLICY_SRC, fn)
        stem, ext = os.path.splitext(fn)
        if ext.lower() in (".md", ".markdown"):
            body, _ = md_to_html(open(path, encoding="utf-8").read())
            body = (f'<div class="ch-role">知识文档 · RAG 语料</div><h1>{html_mod.escape(stem)}</h1>'
                    f'<p><a href="../../policy-docs/{html_mod.escape(fn)}" download>下载原文（{ext[1:]}）</a></p>' + body)
            open(os.path.join(out, f"{stem}.html"), "w", encoding="utf-8", newline="\n").write(
                page(stem, body, "", "", "", "", "", ch_prefix="../", root_prefix="../../"))
            items.append((stem, f"{stem}.html", fn, ext[1:]))
            print(f"[生成] handbook/policy/{stem}.html")
        else:
            items.append((stem, None, fn, ext[1:]))
    cards = []
    for zname, zdesc in ZIPS:
        zpath = os.path.join(POLICY_SRC, zname)
        if not os.path.exists(zpath):
            continue
        zkb = round(os.path.getsize(zpath) / 1024, 1)
        cards.append(f'<a class="ov-card zip-card" href="../../policy-docs/{zname}" download>'
                     f'<div class="no">ZIP</div><h3>{html_mod.escape(zdesc)}</h3>'
                     f'<p>一次打包下载到本地，离线实验与讲师备课用。共 {zkb} KB。</p>'
                     f'<div class="meta"><span>打包下载</span><span>{zname}</span></div></a>')
    for stem, pg, fn, ext in items:
        href = pg if pg else f"../../policy-docs/{fn}"
        dl = "" if pg else " download"
        cards.append(f'<a class="ov-card" href="{href}"{dl}><div class="no">{ext.upper()}</div>'
                     f'<h3>{html_mod.escape(stem)}</h3><p>{"在线可读" if pg else "下载原文"}</p></a>')
    ov = (f'<div class="ov-hero"><div class="tag">素材 · RAG 语料</div><h1>岭湾电力业务知识文档（5 份）</h1>'
          f'<p>这些文档是"供电业务知识问答"实验的检索语料：答案必须能指到"文件名 + 第X条"，'
          f'检索不到时必须拒答。md 文档可在线阅读，docx 与 pdf 保留原样下载。'
          f'需要整包离线使用，直接下载</p><ul><li><a href="../../policy-docs/lab2-classify-kit.zip" download>实验二素材包（zip）</a></li><li><a href="../../policy-docs/lab3-policy-rag-docs.zip" download>实验三语料包（zip，5 份知识文档）</a></li></ul></div>'
          f'<div class="ov-cards">{"".join(cards)}</div>')
    open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n").write(
        page("知识文档目录", ov, "", "", "", "", "", ch_prefix="../", root_prefix="../../"))
    print("[生成] handbook/policy/index.html")


def build_combined(pages):
    parts = [f"# {BRAND} · 学员版实验手册合订本\n",
             "> 本合订本由 `scripts/build.py` 从 `02_实验手册/` 的分册自动装配，请勿手工编辑；"
             "修改内容请改分册后重新构建。\n"]
    for pg in pages:
        raw = read_manual(pg["ch"]["src"]) or ""
        parts.append("\n\n---\n\n" + raw.strip() + "\n")
    out = os.path.join(ROOT, f"{BRAND.replace(' ', '')}-学员版实验手册合订本.md")
    open(out, "w", encoding="utf-8", newline="\n").write("".join(parts))
    print(f"[生成] {os.path.basename(out)}")


def main():
    pages = build_chapters()
    if not pages:
        sys.exit("未找到任何分册手册，请检查 02_实验手册 目录")
    build_handbook(pages)
    build_policy()
    build_combined(pages)
    print(f"\n✅ 构建完成：{len(pages)} 个实验页 + 总览 + 知识文档目录")


if __name__ == "__main__":
    main()
