# AWS 단가 게시판 (서울 리전)

AWS RDS / EC2 의 **공식 단가표**를 엔진·에디션·라이선스 모델(License Included / **BYOL** / **BYOM**)·배포 옵션·인스턴스 조건으로 필터링해 보는 정적 게시판입니다.

- 서버 0대. GitHub Actions가 데이터를 갱신하고 GitHub Pages가 사이트를 서빙합니다.
- **AWS 자격증명 불필요** — AWS Price List Bulk API는 공개 엔드포인트입니다.
- 대상 리전: `ap-northeast-2` (서울)

```
scripts/collect_prices.py    단가 수집 → docs/data/*.json (+ --xlsx 로 엑셀)
scripts/build_standalone.py  데이터를 HTML 안에 삽입 → 단일 파일 버전 생성
scripts/make_sample.py     API 없이 화면 확인용 샘플 데이터 생성
docs/index.html            게시판 UI (단일 파일, 의존성 없음)
docs/data/*.json           갱신되는 데이터 (Actions가 커밋)
_cache/                    가격표 원본 캐시 (git 제외)
.github/workflows/update-prices.yml
```

## 화면 구성

[instances.vantage.sh](https://instances.vantage.sh/) 형식을 따릅니다 — **인스턴스 타입 1개 = 1행**, 엔진/OS별 단가는 **열**로 펼쳐지는 피벗 테이블입니다.

| 탭 | 행 | 열 |
|---|---|---|
| RDS | `db.r6g.2xlarge` 등 인스턴스 타입 | MySQL · PostgreSQL · MariaDB · Aurora MySQL/PostgreSQL · SQL Server Express/Web/Standard/Enterprise · Oracle Standard Two/Enterprise · Db2 |
| EC2 | `m6i.xlarge` 등 인스턴스 타입 | Linux · Windows · RHEL · SUSE · Ubuntu Pro |
| RDS 스토리지 | 스토리지/IOPS 항목 | gp2/gp3/io1, Provisioned IOPS·Throughput, 백업 스냅샷 |

**설정 바** (Vantage와 동일한 축)

- 요금 조건: **온디맨드 / RI 1년 / RI 3년** (Standard 클래스) — 3개만
  - RI **구매 옵션**(No / Partial / All Upfront)은 요금 조건이 아니라 **열**로 펼쳐집니다.
    RI를 선택하면 엔진 열마다 3개 하위 열이 생기고, 상단에 엔진명이 병합 헤더로 표시됩니다.
- 비용 기간: 시간당 / 일 / 월(730h) / 연(8760h)
- 제품: RDS / RDS Custom
- 배포 옵션: **Single-AZ / Multi-AZ** — 2개만
- 라이선스 모델: **전체(열로 구분)** / License Included만 / BYOL만 / BYOM만 / 라이선스 불필요만
  - 라이선스 모델은 **열 이름에 포함**됩니다 (`SQL Server Standard · LI`,
    `Oracle Standard Two · LI` / `· BYOL`, `SQL Server Enterprise · BYOM` …).
    같은 스펙의 LI·BYOL·BYOM 단가를 나란히 비교할 수 있고, 어느 것도 가려지지 않습니다.
- 통화: USD / KRW(환율 직접 입력) · 정밀도: Auto/0/2/4/6자리

> Outposts 전용 엔진 열은 기본 숨김입니다(컬럼 메뉴에서 켤 수 있음).

**표현식 검색** (검색창)

```
vcpu >= 8 and memory < 64 and api ~ r6g
vcpu == 16 or (memory >= 128 and name ~ r6i)
processor ~ graviton
```

비교 연산자(`>= <= > < == !=`), 문자열 포함(`~`), `and` / `or` / 괄호를 지원하고, 일반 텍스트만 입력하면 전체 필드 부분검색으로 동작합니다.

**데이터 갱신 버튼** (검색줄 오른쪽)

세 가지 경로를 한 모달에 담았습니다.

1. **브라우저에서 직접 받기 (기본 동작)** — `데이터 갱신` 을 누르면 창이 열리면서
   **RDS → EC2 순서로 자동 진행**됩니다. 진행 상황은 세 곳에 표시됩니다.
   - 전체 진행줄: `1/2 · RDS 받는 중 12.4 MB / 16.8 MB · 전체 37% · 5초 경과`
   - 서비스별 줄: 개별 진행바 + 완료 시 `16.8 MB · RDS 3,836행 · STORAGE 634행`
   - 툴바 버튼: `갱신 중 37%` (창을 닫아도 진행률이 보입니다)
   진행 중에는 창에 **진행 상황만** 표시되고(파일 불러오기·명령 복사·저장 항목은 숨김),
   RDS·EC2 모두 문제없이 끝나면 결과를 1.2초 보여준 뒤 **창이 자동으로 닫히고**
   화면 하단에 `데이터 갱신 완료 · RDS 3,852행 · EC2 …행 · 42초 소요` 토스트가 뜹니다.
   실패하거나 `중단`한 경우에는 창이 유지되면서 방법 2·3이 다시 나타납니다.
   개별 `RDS만` / `EC2만` 버튼도 그대로 유지했습니다.
   AWS 가 브라우저 직접 요청(CORS)을 막는 환경에서는 실패 메시지와 함께 2·3번을 안내합니다.
2. **파일에서 불러오기** — 내려둔 원본 가격표(`_pricelist_rds_ap-northeast-2.json` 등 AWS `index.json`)나
   이 도구가 만든 `rds.json`·`ec2.json` 을 선택/드래그하면 **브라우저 안에서 다시 파싱**합니다.
   파이썬 수집기와 같은 규칙(BYOM 병합, RDS Custom 분리, RI 매트릭스, licSep 판정)을 JS 로 이식했고,
   17MB 가격표 파싱에 약 1초 걸립니다. 파일은 어디로도 전송되지 않습니다.
3. **파이썬 수집기 명령 복사** — 가장 확실한 방법. 복사 버튼 제공.

갱신 후에는 **단일 파일로 저장**(데이터가 박힌 HTML 재생성) 또는 **JSON으로 저장**
(`rds.json`·`ec2.json`·`rds_storage.json`·`meta.json`)을 할 수 있습니다.
저장한 단일 파일로 기존 파일을 바꿔두면 다음에 열 때도 갱신된 값이 유지됩니다.

그 외: 컬럼 표시/숨김 토글, 열 클릭 정렬, 행 체크 후 **선택 항목만 비교**, 현재 화면 그대로 CSV 내보내기, 필터 초기화, 라이트/다크 자동 대응.

## 배포 (5분)

1. GitHub에서 새 리포지토리 생성 후 이 폴더 내용을 push (`main` 브랜치)
   ```bash
   git init && git add . && git commit -m "init: aws price board"
   git branch -M main
   git remote add origin https://github.com/<계정>/aws-price-board.git
   git push -u origin main
   ```
2. 리포 **Settings → Pages → Build and deployment → Source: GitHub Actions**
3. **Actions** 탭 → `Update AWS prices` → **Run workflow** (수동 1회 실행)
4. 완료되면 `https://<계정>.github.io/aws-price-board/` 로 어디서든 접속

이후 매주 월요일 09:20(KST) 자동 갱신됩니다. 주기는 워크플로우의 `cron` 값을 바꾸면 됩니다.

## 로컬에서 확인

```bash
python3 scripts/collect_prices.py   # 실제 단가 수집 (또는 make_sample.py 로 샘플)
cd docs && python3 -m http.server 8000
# http://localhost:8000
```

> `docs/data/rds.json` · `rds_storage.json` 은 **서울 리전 실제 단가**입니다.
> `ec2.json` 은 아직 샘플이며, `python3 scripts/collect_prices.py --services ec2` 를 한 번
> 실행하거나 Actions 를 돌리면 실제 값으로 교체됩니다.
> (`meta.json` 의 `notCollected` / `source` 로 구분 가능)

## 파일 하나로 쓰기 (서버 없이 더블클릭)

`index.html` 만 따로 열면 데이터를 불러올 수 없습니다. 브라우저는 `file://` 에서
같은 폴더의 JSON 조차 읽지 못하도록 차단하기 때문입니다(보안 정책).
데이터를 HTML 안에 넣어 하나로 합치면 그대로 열립니다.

```bash
python scripts/collect_prices.py       # 1) 단가 수집
python scripts/build_standalone.py     # 2) 단일 파일 생성
# → aws-price-board-standalone.html  (약 1.6 MB)
```

생성된 파일은 서버·인터넷 없이 더블클릭으로 열리고, 메일 첨부나 사내 공유 드라이브로
그대로 전달할 수 있습니다. 웹으로 서비스할 때는 `docs/` 를 GitHub Pages 로 배포하세요
(그때는 `index.html` + `data/` 조합이 그대로 동작합니다).

## 비공개로 운영하려면

단가표는 공개 정보라 그대로 두어도 무방하지만, 사내용으로 감추고 싶다면:

- **Cloudflare Access** (무료 50명): 사이트를 Cloudflare Pages로 옮기고 이메일 도메인(`@mz.co.kr`) 기준 접근 제어
- **GitHub Pages 접근 제어**: Private 리포 + Enterprise Cloud 플랜 필요
- 가장 간단한 방법: 리포는 Private로 두고 Pages만 공개 (URL만 아는 사람이 접근)

## 알아둘 점

- 월 비용 = 시간당 단가 × 730시간
- RI 단가는 Standard 클래스이며, 선결제 금액을 약정 기간(1년=8760h, 3년=26280h)으로 분할해 시간당으로 환산한 **실효 단가**입니다. 구매 옵션별로 `ri1nu`/`ri1pu`/`ri1au`/`ri3nu`/`ri3pu`/`ri3au` 에 각각 담깁니다.
- 서울 리전에서 3년 No Upfront 는 공표 SKU가 매우 적습니다(72건). 화면에서 `–` 가 많이 보이면 정상입니다.
- BYOM(Bring Your Own Media)은 SQL Server 계열에 존재합니다. AWS가 새 라이선스 모델 값을 추가해도 스크립트는 원문 값을 그대로 통과시키므로 필터에 자동 노출됩니다.
- 실제 청구액은 사용량, 약정, EDP/PPA 할인, 데이터 전송료에 따라 달라집니다. 계정 실사용 금액이 필요하면 Cost Explorer 연동을 별도로 붙이면 됩니다(이때는 IAM 키 + GitHub Secrets 필요).

---

## 비용(단가) 수집 기능 — `scripts/collect_prices.py`

사내 기존 스크립트 `collect_rds_sqlserver_pricing.py` 의 도메인 규칙을 그대로 계승한 수집기입니다.
표준 라이브러리만으로 동작하고(`requests` 불필요), `--xlsx` 옵션에만 `openpyxl` 이 필요합니다.

```bash
python scripts/collect_prices.py                     # 서울, RDS+EC2, 캐시 재사용
python scripts/collect_prices.py --refresh           # 가격표 재다운로드
python scripts/collect_prices.py --xlsx              # 기존 형식 엑셀도 저장
python scripts/collect_prices.py --services rds      # RDS만
python scripts/collect_prices.py --region ap-northeast-1
```

### 계승한 규칙

| 규칙 | 내용 |
|---|---|
| BYOM 에디션 병합 | `databaseEdition='Enterprise-BYOM'` → 에디션 `Enterprise` + 라이선스 `BYOM` |
| 언번들 세대 | `m7i·r7i·m8i·r8i·m8a·r8a` 는 라이선스 요금 분리 대상으로 판정 |
| 로컬 캐시 | `_cache/_pricelist_<svc>_<region>.json` 재사용, `--refresh` 로 갱신 |
| 진행률 표시 / 로그 파일 | `collect_log.txt` 에 동시 기록 |
| 월 환산 | 시간당 × 730 |
| 엑셀 산출물 | `SQLServer` / `OpenSource` / `README` 3시트, 기존 컬럼 구성 유지 |

### 보강한 부분

1. **RI 매트릭스**: 1년·3년 × No / Partial / All Upfront 6조합의 실효 시간단가를 모두 수집
   (기존은 `1yr No Upfront` 단일). 선결제액을 약정 기간으로 분할해 시간단가로 환산합니다.
2. **RDS Custom 분리**: `engineCode` 400번대는 RDS Custom(SQL Server 401~407, Oracle 410~411)으로
   분류해 일반 RDS와 섞이지 않게 했습니다. 화면의 **제품** 선택으로 전환합니다.
3. **licenseModel 공백 보정**: RDS Custom SQL Server SKU는 `licenseModel` 이 `NA` 라서,
   요금 설명문(`AWS-provided media` / `customer-provided media (BYOM)`)과 `engineCode` 로
   라이선스 모델을 판정합니다. → 미분류 행 0건.
4. **라이선스 요금 분리 여부를 실측으로 판정** (아래 참고).
5. `is_license_dim` 오탐 수정: 기존 로직은 설명문의 `(License Included)` 문구까지
   라이선스 전용 SKU로 오인할 수 있었습니다.

### ⚠ 검증에서 확인한 사실 (서울 리전, 실제 가격표 기준)

- RDS 가격표에는 **라이선스 요금만 따로 공표하는 SKU가 존재하지 않습니다** (0건).
  따라서 `(LI − License)` 로 컴퓨팅 단가를 빼내는 계산은 성립하지 않습니다.
- 대신 **언번들 세대는 모든 에디션의 공표 단가가 동일**합니다.
  예: `db.m7i.2xlarge` Single-AZ — Enterprise / Standard / Web / BYOM 모두 `$0.988/h`.
  즉 **그 공표 단가 자체가 이미 라이선스 제외 컴퓨팅 단가**이고, SQL Server 라이선스는
  별도 청구되며 가격표에 나타나지 않습니다.
  → 수집기는 이 경우를 `licSep: true` 로 표시하고 `c_od` 에 해당 단가를 넣습니다.
  화면에서는 단가 옆에 <b>*</b> 로 표시됩니다.
- 번들 세대는 라이선스가 단가에 포함됩니다. 예: `db.r6i.large` SQL Server Standard LI
  `$1.05/h`, RI No-Up 1yr `$0.9923/h` — 기존 엑셀 값과 일치 확인.
- `RI No-Up 1yr BYOM` 은 기존 스크립트에서 0건이었으나, RDS Custom 분류·라이선스 보정 후
  **36건** 수집됩니다.

### 데이터 스키마 (`docs/data/rds.json`)

```jsonc
{
  "instanceType": "db.r6i.large", "family": "r6i",
  "product": "RDS",                  // 또는 "RDS Custom"
  "engine": "SQL Server", "edition": "Standard",
  "license": "License Included",     // License Included | BYOL | BYOM | No License Required | Marketplace
  "deployment": "Single-AZ",
  "vcpu": 2, "memory": "16 GiB", "processor": "...", "network": "...",
  "unbundled": false,                // m7i/r7i/m8i/r8i/m8a/r8a 여부
  "licSep": false,                   // 라이선스 별도 청구(가격표 미공표) 여부
  "od": 1.05,                        // 온디맨드 시간당 USD
  "ri1nu": 0.9923, "ri1pu": null, "ri1au": null,
  "ri3nu": null,  "ri3pu": null,  "ri3au": null,
  "c_od": null                       // 라이선스 제외 컴퓨팅 상당액(산출 가능한 경우)
}
```

GitHub Actions 는 매주 이 스크립트를 `--refresh --xlsx` 로 실행하고, 생성된 엑셀과
`collect_log.txt` 를 워크플로우 아티팩트로 첨부합니다.
