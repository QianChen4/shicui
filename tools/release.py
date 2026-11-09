#!/usr/bin/env python3
"""生成在线更新用的 latest.json。

用法：
    python3 tools/release.py          # 按 拾萃.html 和 更新记录.md 重新生成 latest.json
    python3 tools/release.py --check  # 只检查 latest.json 是否和 拾萃.html 一致（CI 用）

做的事：
1. 读出 拾萃.html 里的 PROGRAM_VERSION（真正的版本号，如 2.11.2）。
2. 把“兼容旧版更新：const PROGRAM_VERSION='…'”注释改成第一位加 1 的旧编号（如 3.11.2），
   让 v2.6.0 以前的更新程序也能认出新版。
3. 从 更新记录.md 里取出这个版本的日期和更新内容。
4. 计算 拾萃.html 的大小和 sha256，写入 latest.json。
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / '拾萃.html'
LOG = ROOT / '更新记录.md'
OUT = ROOT / 'latest.json'


def fail(msg):
    print('错误：' + msg, file=sys.stderr)
    sys.exit(1)


def legacy(ver):
    first, rest = ver.split('.', 1)
    return f'{int(first) + 1}.{rest}'


def notes_for(ver):
    text = LOG.read_text(encoding='utf-8')
    m = re.search(rf'^## v{re.escape(ver)}(?:（([\d-]+)）)?\s*$(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not m:
        fail(f'更新记录.md 里没有 “## v{ver}（日期）” 这一节')
    lines = [re.sub(r'^\s*[-*]\s*', '', l).strip() for l in m.group(2).strip().splitlines()]
    return (m.group(1) or ''), '\n'.join(l for l in lines if l)


def build(fix):
    text = HTML.read_text(encoding='utf-8')
    m = re.search(r"^const PROGRAM_VERSION='([\d.]+)'", text, re.M)
    if not m:
        fail('拾萃.html 里找不到 PROGRAM_VERSION')
    ver = m.group(1)
    compat = f"兼容旧版更新：const PROGRAM_VERSION='{legacy(ver)}'"
    new_text = re.sub(r"兼容旧版更新：const PROGRAM_VERSION='[\d.]+'", compat, text, count=1)
    if compat not in new_text:
        fail('拾萃.html 里找不到“兼容旧版更新”注释')
    if new_text != text:
        if not fix:
            fail('拾萃.html 的兼容旧版注释没有更新，请运行 python3 tools/release.py')
        HTML.write_text(new_text, encoding='utf-8')
    data = HTML.read_bytes()
    date, notes = notes_for(ver)
    return {
        'format': 'shicui-latest',
        'version': legacy(ver),  # 给 v2.6.0 以前的更新程序看的旧编号
        'release': ver,          # 真正的版本号
        'file': '拾萃.html',
        'size': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'date': date,
        'notes': notes,
    }


def main():
    check = '--check' in sys.argv
    info = build(fix=not check)
    out = json.dumps(info, ensure_ascii=False, indent=2) + '\n'
    if check:
        cur = OUT.read_text(encoding='utf-8') if OUT.exists() else ''
        if cur != out:
            fail('latest.json 和 拾萃.html / 更新记录.md 不一致，请运行 python3 tools/release.py')
        print(f'latest.json 正确：v{info["release"]}')
    else:
        OUT.write_text(out, encoding='utf-8')
        print(f'已生成 latest.json：v{info["release"]}，{info["size"]} 字节，sha256 {info["sha256"][:12]}…')


if __name__ == '__main__':
    main()
