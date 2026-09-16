#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_links.py — 实验站静态链接自检

检查内容：
1. 所有本地 href / src 目标文件是否存在（含 iframe 指向的手册页）；
2. 带 #锚点 的链接，目标文件里是否真有该 id / name；
3. 输出汇总，缺失项以 [缺失] 标出，退出码 1。

用法：python scripts/check_links.py
"""
import io
import os
import re
import sys
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SKIP_EXT = (".html", ".htm")
ATTR = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)
ID = re.compile(r'\bid\s*=\s*"([^"]+)"|\bname\s*=\s*"([^"]+)"', re.I)


def html_files():
    for dirpath, dirnames, filenames in os.walk(SITE):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".github")]
        for fn in sorted(filenames):
            if fn.lower().endswith(SKIP_EXT):
                yield os.path.join(dirpath, fn)


def ids_of(path):
    try:
        return {a or b for a, b in ID.findall(io.open(path, encoding="utf-8", errors="replace").read())}
    except OSError:
        return set()


def main():
    files = list(html_files())
    total = missing = anchors_bad = external = 0
    by_file = {}
    ids_cache = {}
    for page in files:
        rel = os.path.relpath(page, SITE)
        text = io.open(page, encoding="utf-8", errors="replace").read()
        for raw in ATTR.findall(text):
            if raw.startswith(("http://", "https://", "mailto:", "javascript:", "data:", "#")):
                if raw.startswith("http"):
                    external += 1
                continue
            total += 1
            path_part, _, frag = raw.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(page), unquote(path_part)))
            if not os.path.exists(target):
                missing += 1
                by_file.setdefault(rel, []).append(f"[缺失] {raw}")
                continue
            if frag and target.lower().endswith(SKIP_EXT):
                if target not in ids_cache:
                    ids_cache[target] = ids_of(target)
                if frag not in ids_cache[target]:
                    anchors_bad += 1
                    by_file.setdefault(rel, []).append(f"[锚点丢失] {raw}")
    print(f"扫描 HTML {len(files)} 个；本地链接 {total} 条；外链 {external} 条")
    for rel in sorted(by_file):
        print(f"\n{rel}")
        for line in by_file[rel]:
            print("  " + line)
    print(f"\n结果：缺失 {missing} 条，锚点问题 {anchors_bad} 条")
    if not by_file:
        print("✅ 全部本地链接与锚点有效")
    return 1 if by_file else 0


if __name__ == "__main__":
    sys.exit(main())
