#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단일 파일(standalone) HTML 빌드.

docs/index.html + docs/data/*.json 을 하나로 합쳐
더블클릭만으로(file:// 에서도) 열리는 HTML 을 만듭니다.

  python scripts/build_standalone.py
  → aws-price-board-standalone.html

옵션
  --out <경로>     출력 파일명 지정
  --minify         숫자 정밀도를 6자리로 줄여 용량 축소
"""
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "index.html")
DATA = os.path.join(ROOT, "docs", "data")
MARKER = "/*__EMBED__*/"


def load(name):
    path = os.path.join(DATA, name)
    if not os.path.isfile(path):
        print(f"  [건너뜀] {name} 없음")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def inline_icons(html):
    """<link rel=icon ...> 들을 SVG data URI 한 쌍으로 교체."""
    import re
    import urllib.parse

    def uri(name):
        path = os.path.join(ROOT, "docs", name)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            svg = re.sub(r"\s+", " ", f.read()).strip()
        return "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:;=,()#'")

    fav, touch = uri("favicon.svg"), uri("icon-192.svg")
    if not fav:
        return html
    block = f'<link rel="icon" type="image/svg+xml" href="{fav}">\n'
    if touch:
        block += f'<link rel="apple-touch-icon" href="{touch}">\n'
    html = re.sub(r'(<!-- 파비콘[^\n]*\n)?(<link rel="(?:icon|apple-touch-icon)"[^\n]*\n)+',
                  block, html, count=1)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "aws-price-board-standalone.html"))
    args = ap.parse_args()

    with open(SRC, encoding="utf-8") as f:
        html = f.read()
    if MARKER not in html:
        raise SystemExit(f"[오류] {SRC} 에 {MARKER} 표시가 없습니다.")

    print("[수집] docs/data/*.json")
    payload = {}
    for key, name in (("rds", "rds.json"), ("ec2", "ec2.json"),
                      ("storage", "rds_storage.json"), ("ebs", "ebs.json"),
                      ("meta", "meta.json")):
        d = load(name)
        if d is not None:
            payload[key] = d
            n = len(d) if isinstance(d, list) else "-"
            print(f"  {name}: {n}행")

    if not any(k in payload for k in ("rds", "ec2", "storage", "ebs")):
        raise SystemExit("[오류] 삽입할 데이터가 없습니다. 먼저 collect_prices.py 를 실행하세요.")

    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # </script> 문자열이 데이터에 있으면 HTML 파싱이 깨지므로 이스케이프
    blob = blob.replace("</", "<\\/")
    html = html.replace(MARKER, "window.__DATA__ = " + blob + ";")

    # 파비콘 인라인화: 단일 파일은 옆에 아이콘 파일이 없으므로 data URI 로 심는다
    html = inline_icons(html)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[완료] {args.out}  ({os.path.getsize(args.out)/1048576:.2f} MB)")
    print("       더블클릭으로 바로 열립니다 (서버·인터넷 불필요).")


if __name__ == "__main__":
    main()
