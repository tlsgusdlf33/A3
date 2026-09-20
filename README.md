# A3 — 개인 자동화 비서

매일 아침 휴대폰으로 **오늘 볼 기술사 문제, 오늘 외울 영어, 오늘 알아야 할 소식**을 보내주는 프로그램.
PC를 켜 둘 필요 없이 GitHub이 대신 돌려준다.

```
☀️ 오늘의 브리핑              🏗️ 기술사 훈련 D-139
2026-09-20 (일)               📌 건설기계기술사 D-139 (2027-02-06)
🌤️ 서울 맑음 17~28℃           오늘 3문제 · 누적 학습 21/120문항
                              【1/3】 서술형 · 유압 시스템
🏗️ 건설기계기술사 D-139        Q. 유압 어큐뮬레이터의 기능은?
📚 오늘의 학습량               — 답안 전개 —
  기술사: 복습 2 · 진도 21/120   I. 개요 — 정의, 파스칼 원리…
  영어:  복습 5 · 진도 49/134   II. 회로 구성 및 작동원리…
```

## 무엇을 해 주나

| 태스크 | 하는 일 |
|---|---|
| `brief` | D-day, 오늘 학습량, 날씨, 최근 실행 이력을 한 화면에 |
| `exam` | **건설기계기술사 120문항**을 간격 반복으로 매일 몇 문제씩. 답안 전개 틀 + 채점 키워드 + **모범답안 전문(A4 3~4장)** |
| `english` | **OPIc 말하기 훈련 54문항 + 표현 80장**. 매일 2문항은 입으로 말하고, 5개 표현은 외운다 |
| `radar` | 건설기계 규제/기술 동향, 부업·외주·지원사업 소식 중 **처음 보는 것만** 골라서 |
| `selfupdate` | 원격 저장소에 새 코드가 올라오면 스스로 당겨오고 무엇이 바뀌었는지 알림 |

기술사 문제은행은 Google Drive의 「건설기계기술사」 시트(예상문제 120선)를 구조화한 것이다.
11개 분야(일반 기계 지식 / 유압 / 엔진·파워트레인 / 전기·제어 / 기계 유지관리 /
안전 / 공압 / 특수 건설기계 / 환경 / 문제 해결 / 최근 빈출)를 모두 덮는다.

### 모범답안은 외워서 쓸 수 있어야 한다

기술사는 답을 찾는 시험이 아니라 **외워서 쓰는 시험**이다. 그래서 틀과 키워드만으로는
부족하고, 실제로 옮겨 쓸 전문이 필요하다. `a3/data/answers/` 에 **A4 3~4장(10pt) 분량**의
모범답안을 둔다 — 도표와 도해를 포함한 실전 답안 그대로다.

```bash
python -m a3 answers      # 작성된 답안 목록과 분량
python -m a3 answer 011   # 전문 보기
```

도해를 SVG가 아니라 **ASCII로 그리는 이유**가 있다. 시험장에서는 손으로 그린다.
화면에서만 예쁜 그림은 25분 안에 재현할 수 없으면 쓸모가 없다. ASCII 도해는
알림·터미널·깃허브·웹에서 똑같이 보이고, 펜으로 그대로 옮겨 그릴 수 있다.

분량은 글자 수가 아니라 **줄 수**로 잰다. 표와 도해는 글자가 적어도 지면을 그대로
먹기 때문이다. 폭 90(한글 45자)·장당 42줄 기준으로 계산하며, 서술형이 3~4.5장을
벗어나거나 표가 3개 미만이거나 개요·결론이 없으면 **CI가 막는다**.

현재 10편(A4 39.6장). 서술형 83문항이 목표이고, 주간 루틴이 매주 3편씩 쌓는다.
작성 규약은 [`a3/data/answers/README.md`](a3/data/answers/README.md).

### 영어는 OPIc 기준으로 짰다

오픽은 말하기 시험이라 카드를 눈으로 읽어서는 점수가 오르지 않는다. 그래서 카드가 두 종류다.

- **말하기 카드(54)** — 영어 질문 + 한국어 해석 + ⏱제한시간을 먼저 준다.
  *소리 내어 말한 뒤에* 답변 뼈대 3단계와 쓸 표현을 확인한다.
  8개 유형(자기소개 / 직업 / 묘사 / 습관 / 경험 / 비교 / 롤플레이 / 돌발)을 모두 덮는다.
- **표현 카드(80)** — 담화 표지·시간 벌기 20개 + 펌프·도장·검사·발주처 메일 실무 영어 60개.

실무 영어를 버리지 않은 이유가 있다. 배경설문에서 '직장인'을 고르면 **직업 문항이 반드시 나오고**,
그때 쓸 재료가 바로 그 어휘들이다. 「장비가 고장 나서 공급업체에 전화하는 롤플레이」처럼
본인 실무가 그대로 문제로 나오는 카드도 넣어 뒀다.

말하기 quota는 표현과 분리돼 있다. 한 통에 섞어 뽑으면 표현 카드가 말하기를 밀어내는데,
오픽에서 그건 치명적이라 테스트로 막아 뒀다.

## 5분 설치

### 1. 휴대폰에 알림 앱 설치
[ntfy](https://ntfy.sh) 앱 설치 (iOS / Android, 무료, 가입 불필요) → **Subscribe to topic** →
남이 못 맞힐 긴 이름 입력. 예: `a3-hr-9f3k2m`

> 토픽 이름은 사실상 비밀번호다. 짧고 흔한 이름을 쓰면 남이 내 알림을 구독할 수 있다.

### 2. GitHub에 비밀값 등록
저장소 → Settings → Secrets and variables → Actions → **New repository secret**

| 이름 | 값 |
|---|---|
| `A3_NTFY_TOPIC` | 위에서 정한 토픽 이름 |

이것만 넣으면 끝. 매일 아침 07:12, 평일 저녁 19:07(KST)에 자동으로 돈다.
바로 시험해 보려면 Actions 탭 → `daily` → **Run workflow**.

### 3. (선택) 내 PC에서도 쓰기

```bash
git clone https://github.com/tlsgusdlf33/A3.git && cd A3
pip install -r requirements.txt
python -m a3 init                  # config.yaml 생성
cp .env.example .env               # A3_NTFY_TOPIC 채우기
set -a; source .env; set +a
python -m a3 test-notify           # 폰에 알림 오는지 확인
python -m a3 run all
```

## 쓰는 법

```bash
python -m a3 run all               # 전부 실행
python -m a3 run exam english      # 골라서 실행
python -m a3 run radar --dry-run   # 알림 안 보내고 결과만 확인

python -m a3 status                # 진도 확인
python -m a3 show exam 013         # 특정 문제 다시 보기 (틀 + 키워드)
python -m a3 answer 011            # 모범답안 전문 (A4 3~4장)
python -m a3 answers               # 답안이 작성된 문항 목록
python -m a3 grade exam 013 4      # 채점 (0~5) → 다음 복습일 자동 계산
python -m a3 show english o063     # 오픽 롤플레이 카드 보기
python -m a3 grade english o063 3

python -m a3 tasks                 # 태스크 목록
```

### 채점(`grade`)이 중요한 이유

간격 반복은 **잘 아는 건 멀리, 헷갈리는 건 가까이** 배치한다. SM-2 알고리즘을 쓴다.

| 점수 | 의미 | 다음 복습 |
|---|---|---|
| 5 | 막힘없이 답안 구조가 나옴 | 점점 길게 (1일 → 6일 → 16일 → …) |
| 3~4 | 떠오르긴 하는데 버벅임 | 조금 길게 |
| 0~2 | 백지 | 내일 다시 |

채점을 건너뛰어도 진도는 나간다 — 출제된 카드는 일주일 뒤로 미뤄지고,
**새 문항이 항상 우선**이라 30일이면 90문항을 만난다.

## 설정

`config.yaml`(없으면 내장 기본값)에서 바꾼다. 비밀값은 환경변수로.

```yaml
exam:
  date: "2027-02-06"    # Q-Net 공고 뜨면 실제 날짜로
  provisional: true     # 추정일이면 알림에 '※추정' 표시
  daily_cards: 3
  categories: ["유압 시스템"]   # 약한 분야만 집중 공략할 때

english:
  name: OPIc
  target_level: IH
  speaking_cards: 2     # 하루에 입으로 말해 볼 오픽 문항
  word_cards: 5         # 하루에 외울 표현
  tags: ["오픽-롤플레이", "오픽-돌발"]   # 시험 직전 약점만 집중 공략

brief:
  latitude: 37.5665     # 사는 곳 좌표
  longitude: 126.9780
```

전체 항목은 [`config.example.yaml`](config.example.yaml) 참고.

### 시험일에 대하여

2026년 기술사 회차(138회 2/7, 139회 5/16, 140회 8/22)는 모두 종료됐다.
설정된 `2027-02-06`은 **141회 추정일**이며, 알림에 `※추정`으로 표시된다.
[Q-Net 기술사 시험일정](https://www.q-net.or.kr/crf021.do)에 공고가 뜨면
`exam.date`를 고치고 `provisional: false`로 바꿀 것.

## 알림 채널

기본은 ntfy. 여러 개를 동시에 켤 수 있다 (`A3_CHANNELS=ntfy,telegram`).

| 채널 | 필요한 것 |
|---|---|
| `ntfy` | 토픽 이름만 (`A3_NTFY_TOPIC`) — **권장** |
| `telegram` | 봇 토큰 + chat_id (`A3_TELEGRAM_TOKEN`, `A3_TELEGRAM_CHAT_ID`) |
| `discord` | 웹훅 URL (`A3_DISCORD_WEBHOOK`) |
| `console` | 없음. 터미널 출력 |

## 진도는 어디에 저장되나

`state/a3.json` — 사람이 읽을 수 있는 JSON. GitHub Actions가 매일 실행 후 커밋하므로
**진도가 git 히스토리에 남는다**. 언제 무엇을 봤는지 나중에 되짚을 수 있다.

## 내용 늘리기

- 기술사 문제 추가: [`a3/data/exam_deck.yaml`](a3/data/exam_deck.yaml)의 `cards`에 한 줄
- 모범답안 추가: `a3/data/answers/<문항번호>.md` — [작성 규약](a3/data/answers/README.md) 참고
- 오픽/영어 카드 추가: [`a3/data/english_deck.yaml`](a3/data/english_deck.yaml)
  (`kind: speaking` 이면 말하기 카드. `structure` 3단계와 `phrases` 3개가 필수)
- 레이더 키워드/피드: `config.yaml`의 `radar`

덱은 테스트가 구조를 검사한다 (`python -m pytest tests -q`). 기술사 카드에 키워드가
3개 미만이거나, 말하기 카드에 뼈대가 3단계 미만이거나, 오픽 8개 유형 중 하나가
비면 CI가 잡는다.

## 개발

```bash
pip install -r requirements.txt pytest
python -m pytest tests -q          # 369개
```

## 구조

```
a3/
├── cli.py          명령행
├── config.py       설정 (환경변수 > config.yaml > 기본값)
├── store.py        JSON 상태 저장소 (원자적 쓰기)
├── srs.py          SM-2 간격 반복
├── notify.py       ntfy / telegram / discord / console
├── tasks/          brief · exam · english · radar · selfupdate
├── answers.py      모범답안 로딩 + A4 분량 계산
└── data/
    ├── exam_deck.yaml      120문항 · 11개 분야
    ├── english_deck.yaml   말하기 54 + 표현 80
    └── answers/            모범답안 전문 (A4 3~4장, 도표·도해 포함)
```
