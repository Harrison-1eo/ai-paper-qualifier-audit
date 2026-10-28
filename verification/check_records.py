# -*- coding: utf-8 -*-
"""机械核查脚本：把四份人工核查记录变成机器可验证的证据。

检查三件事（全部只依赖本仓库材料）：
  A. 每份核查记录表中引用的 AI 输出原句，确实逐字（按省略号分片）存在于对应的输出存档中；
  B. ground truth 清单中每条的论文引文 + 页码，确实存在于随包 PDF 对应页的 pdftotext 文本中
     （页文本由脚本现场从 PDF 再生，同时演示 §5.1 命令的可再生性）；
  C. 由判定表重新计算的覆盖率统计，与各记录"汇总"节写明的数字一致。

用法：python check_records.py [--root MATERIALS_ROOT]
退出码：0 = 全部通过；1 = 存在不一致（并逐条列出）。
"""
import re, sys, subprocess, io, os
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]
ROOT = os.path.normpath(ROOT)

RECORDS = [
    ("experiments/A1-输出.md", "verification/核查记录-条件A.md"),
    ("experiments/B1-输出.md", "verification/核查记录-条件B.md"),
    ("bohrium/A-对话记录.md", "verification/核查记录-玻尔A.md"),
    ("bohrium/B-对话记录.md", "verification/核查记录-玻尔B.md"),
]

import unicodedata
KEEP_EXTRA = set("%<>[]./=+-~×")
def norm(s):
    """标点与符号不敏感的字级规范化：仅保留字母/数字/百分号等少数字符。
    目的：免疫转写时的引号/逗号差异与 pdftotext 的数学符号乱码（如 κ → U+FFFD）。"""
    s = re.sub(r"\*\*|\||`", "", s)
    out = []
    for ch in s:
        if ch.isalnum() or unicodedata.category(ch)[0] in ("L", "N") or ch in KEEP_EXTRA:
            out.append(ch)
    return "".join(out)

def norm(s):
    """字级规范化：仅保留 ASCII 字母数字、CJK 与少数字符。
    免疫转写时的标点/引号差异与 pdftotext 的数学符号乱码（如 κ → U+FFFD）。"""
    s = re.sub(r"\*\*|\||`", "", s)
    out = []
    for ch in s:
        if (ch.isascii() and ch.isalnum()) or "一" <= ch <= "鿿" or ch in KEEP_EXTRA:
            out.append(ch)
    return "".join(out)

QUOTE_RE = re.compile("[“”\"「」]([^“”\"「」]{6,})[“”\"「」]")
PLACEHOLDER = re.compile(r"^[—－-]+$|无任何对应表述|^结论\s*\d+[:：]\s*$")

def fragments(quote):
    """把引句单元格切分为必须在输出中全部存在的片段：
    优先按引号对拆出每条子引文；否则按省略号/句界切分。"""
    q = re.sub(r"\*\*", "", quote)
    subquotes = QUOTE_RE.findall(q)
    if subquotes:
        parts = []
        for sq in subquotes:
            parts.extend(x for x in re.split(r"…|\.\.\.|—{2,}|[；;。]", sq))
    else:
        parts = re.split(r"…|\.\.\.|—{2,}|[；;。]", q)
    out = []
    for x in parts:
        xn = norm(x)
        if len(xn) >= 6 and not PLACEHOLDER.search(x.strip()):
            out.append(x)
    return out

def parse_record(path):
    rows = {}
    summary_lines = []
    for line in open(os.path.join(ROOT, path), encoding="utf-8"):
        line = line.strip()
        m = re.match(r"\|\s*(GT\d+)", line)
        if m:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and not cells[0].startswith("GT#") and not set(cells[0]) <= {"-", " "}:
                gt = m.group(1)
                judge = cells[1].replace("*", "").strip()
                rows[gt] = (judge, cells[2])
        if line.startswith("- ground truth") or "保留" in line and "覆盖率" in line:
            summary_lines.append(line)
    return rows, summary_lines

ok = fail = 0
def check(cond, label, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {label}")
    else: fail += 1; print(f"  [FAIL] {label} {detail}")

print("== A. 核查记录引句 vs AI 输出存档（省略号分片子串匹配） ==")
all_judgments = {}
for out_rel, rec_rel in RECORDS:
    out_text = norm(open(os.path.join(ROOT, out_rel), encoding="utf-8").read())
    rows, _ = parse_record(os.path.join(ROOT, rec_rel))
    n_verified = n_skip = 0
    bad = []
    for gt, (judge, quote) in rows.items():
        all_judgments.setdefault(rec_rel, {})[gt] = judge
        if judge.startswith("未保留") or "无任何对应表述" in quote:
            n_skip += 1; continue
        frs = fragments(quote)
        if not frs:
            n_skip += 1; continue
        missing = [f for f in frs if norm(f) not in out_text]
        if missing:
            bad.append((gt, missing[0][:40]))
        else:
            n_verified += 1
    print(f"- {os.path.basename(rec_rel)}: 逐字验证 {n_verified} 条 / 跳过（无引句或未保留） {n_skip} 条")
    check(not bad, f"{os.path.basename(rec_rel)} 引句全部命中存档", f"首个失配: {bad[:2]}")

print("== B. ground truth 引文 vs 随包 PDF 对应页（页文本现场再生） ==")
pdf = os.path.join(ROOT, "paper", "2610.28675.pdf")
r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", pdf, "-"], capture_output=True)
pages = [norm(p) for p in r.stdout.decode("utf-8", errors="replace").split("\f")]
gt_rows = 0; gt_bad = []
for line in open(os.path.join(ROOT, "verification/原文限定条件清单-ground-truth.md"), encoding="utf-8"):
    m = re.match(r"\|\s*(GT\d+)\s*\|", line)
    if not m or "限定条件内容" in line: continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 4: continue
    gt_rows += 1
    gt, pos, quote = m.group(1), cells[2], cells[3]
    page_ids = sorted(set(int(x) for x in re.findall(r"p\s*(\d+)", pos) + re.findall(r"[–~-]\s*(\d+)", pos)))
    if not page_ids: continue
    subqs = QUOTE_RE.findall(re.sub(r"\*\*", "", quote)) or [quote]
    subs = []
    for sq in subqs:
        for piece in re.split(r"…|\.\.\.|[；;。]", sq):
            pn = norm(piece)
            if len(pn) >= 8: subs.append(pn)
    if not subs: continue
    hit = all(any(x in pages[p-1] for p in page_ids if 0 < p <= len(pages)) for x in subs)
    if not hit: gt_bad.append((gt, subs[0][:36]))
print(f"- 解析 GT 条目 {gt_rows} 条，页码引文核查 {gt_rows - len(gt_bad)} 条命中")
check(not gt_bad, "GT 论文引文均可定位到所述页", f"失配: {gt_bad[:3]}")

print("== C. 覆盖率统计复算 vs 记录汇总 ==")
for _, rec_rel in RECORDS:
    rows, _ = parse_record(os.path.join(ROOT, rec_rel))
    c = Counter(j.split("（")[0].strip() for j in (x[0] for x in rows.values()))
    n = sum(c.values())
    expect = {"保留": c.get("保留", 0), "部分": c.get("部分", 0), "未保留": c.get("未保留", 0)}
    # 汇总行形如 "保留 15（68.2%）；部分 4（18.2%）；未保留 3（13.6%）" 或 "保留 22 条（100%）"
    text = open(os.path.join(ROOT, rec_rel), encoding="utf-8").read()
    summary_line = next((l for l in text.splitlines() if l.strip().startswith("- **保留") or l.strip().startswith("- 保留")), "")
    ms = re.findall(r"(保留|部分|未保留)[^\d%]*(\d+)", summary_line)
    stated = {k: int(v) for k, v in ms[:3]} if ms else {}
    got = {k: expect[k] for k in stated} if stated else expect
    check(all(stated.get(k) == expect[k] for k in ("保留", "部分", "未保留") if k in stated),
          f"{os.path.basename(rec_rel)} 汇总数字与复算一致", f"记录声明 {stated} vs 复算 {expect}")

print(f"\n== 结果: PASS {ok} / FAIL {fail} ==")
sys.exit(0 if fail == 0 else 1)
