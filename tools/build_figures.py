"""답안 도해를 SVG 로 생성한다.  실행: python tools/build_figures.py"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from a3.figures import ACCENT, FILL, Fig, Plot  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "a3" / "data" / "answers" / "figures"
FIGURES: dict[str, Fig] = {}


def fig(name: str):
    def deco(fn):
        FIGURES[name] = fn()
        return fn
    return deco


# ─────────────────────────── 077 로드롤러 ───────────────────────────

@fig("077-1")
def compaction_curve():
    p = Plot(560, 330, "함수비에 따른 건조밀도 변화와 최적함수비",
             xlim=(6, 20), ylim=(1.76, 1.98),
             xlabel="함수비 w (%)", ylabel="건조밀도 γd (t/m³)")
    p.axes([6, 8, 10, 12, 14, 16, 18, 20], [1.80, 1.85, 1.90, 1.95],
           yfmt=lambda v: f"{v:.2f}")
    p.band(12, 16)
    p.curve([(6, 1.785), (8, 1.825), (10, 1.872), (12, 1.926),
             (14, 1.952), (16, 1.918), (18, 1.858), (20, 1.798)])
    p.vline(14, "OMC 14%")
    p.dot(14, 1.952, "γd,max = 1.95 t/m³", dx=10, dy=-12, anchor="start")
    p.text(p.X(14), p.Y(1.782), "관리 범위 OMC ± 2%", size=11, accent=True, weight=600)
    p.text(p.X(7.2), p.Y(1.855), "함수비 부족", size=10.5, opacity=0.7, anchor="start")
    p.text(p.X(7.2), p.Y(1.838), "입자 마찰 과다", size=10, opacity=0.6, anchor="start")
    p.text(p.X(19.4), p.Y(1.875), "함수비 과다", size=10.5, opacity=0.7, anchor="end")
    p.text(p.X(19.4), p.Y(1.858), "간극수압 발생", size=10, opacity=0.6, anchor="end")
    return p


@fig("077-2")
def pass_count():
    p = Plot(560, 300, "다짐 횟수에 따른 다짐도 변화와 과다짐 구간",
             xlim=(0, 12), ylim=(80, 102),
             xlabel="다짐 횟수 (회)", ylabel="다짐도 (%)")
    p.axes([0, 2, 4, 6, 8, 10, 12], [80, 85, 90, 95, 100])
    p.line(p.pl, p.Y(95), p.w - p.pr, p.Y(95), accent=True, dash="5 4", width=1.3)
    p.text(p.w - p.pr, p.Y(95) - 7, "관리 기준 95%", size=11, accent=True,
           anchor="end", weight=600)
    p.curve([(0, 82), (2, 88.5), (4, 93), (6, 96), (8, 97.4), (10, 97.6), (12, 96.4)])
    p.dot(6, 96, "적정 6회", dx=2, dy=16, anchor="start")
    p.text(p.X(2.6), p.Y(86), "급증 구간", size=10.5, opacity=0.7)
    p.text(p.X(11), p.Y(99.6), "과다짐 →", size=10.5, opacity=0.7, anchor="end")
    p.text(p.X(11), p.Y(98.2), "입자 파쇄로 밀도 저하", size=10.5, opacity=0.7, anchor="end")
    return p


# ─────────────────────────── 023 토크컨버터 ───────────────────────────

@fig("023-1")
def tc_performance():
    p = Plot(580, 340, "토크컨버터의 속도비에 따른 토크비와 전달효율",
             xlim=(0, 1), ylim=(0, 3.2),
             xlabel="속도비 e = N터빈 / N펌프", ylabel="토크비 t / 효율 η")
    p.axes([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 1.0, 2.0, 3.0],
           xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.1f}")
    # 토크비 : 스톨에서 최대, 클러치점에서 1.0
    p.curve([(0, 2.6), (0.2, 2.15), (0.4, 1.72), (0.6, 1.36), (0.8, 1.06), (0.9, 1.0), (1.0, 1.0)],
            dash="6 4")
    p.text(p.X(0.13), p.Y(2.45), "토크비 t", size=11, anchor="start", opacity=0.8)
    # 효율 : η = t · e → 포물선형
    p.curve([(0, 0), (0.2, 0.43), (0.4, 0.69), (0.6, 0.82), (0.75, 0.87),
             (0.85, 0.85), (0.9, 0.7), (1.0, 0)], accent=True)
    p.text(p.X(0.42), p.Y(0.55), "효율 η", size=11.5, accent=True, weight=600)
    p.dot(0, 2.6, "스톨점 t = 2.6", dx=8, dy=-10, anchor="start")
    p.dot(0.75, 0.87, "최고효율 87%", dx=-8, dy=18, anchor="middle")
    p.vline(0.9, "클러치점")
    p.text(p.X(0.08), p.Y(0.25), "효율 0 = 전 입력이 열로", size=10.5,
           anchor="start", opacity=0.7)
    return p


# ─────────────────────────── 051 크레인 ───────────────────────────

@fig("051-1")
def crane_capacity():
    p = Plot(560, 330, "작업반경에 따른 정격하중 감소 곡선",
             xlim=(3, 30), ylim=(0, 52),
             xlabel="작업반경 R (m)", ylabel="정격하중 (ton)")
    p.axes([3, 6, 10, 14, 18, 22, 26, 30], [0, 10, 20, 30, 40, 50])
    p.curve([(3, 50), (6, 32), (10, 18.5), (14, 12), (18, 8.2), (22, 5.8),
             (26, 4.2), (30, 3.1)], accent=True)
    p.line(p.X(6), p.Y(0), p.X(6), p.Y(32), dash="4 3", width=1, opacity=0.5)
    p.line(p.X(12), p.Y(0), p.X(12), p.Y(14.5), dash="4 3", width=1, opacity=0.5)
    p.dot(6, 32, "6m → 32t", dx=8, dy=-8, anchor="start")
    p.dot(12, 14.5, "12m → 14.5t", dx=8, dy=-6, anchor="start")
    p.text(p.X(19), p.Y(30), "반경 2배 → 하중 1/2 이하", size=11.5, weight=600)
    p.text(p.X(19), p.Y(25), "붐을 눕힐수록 위험이 급증", size=10.5, opacity=0.7)
    p.text(p.X(19), p.Y(20), "반드시 운전실 정격하중표 확인", size=10.5,
           accent=True, weight=600)
    return p


@fig("051-2")
def sling_angle():
    p = Plot(560, 300, "줄걸이 각도에 따른 로프 장력 배수",
             xlim=(0, 150), ylim=(0, 4.2),
             xlabel="줄걸이 각도 θ (°)", ylabel="장력 배수 (× 하중 W)")
    p.axes([0, 30, 60, 90, 120, 150], [1.0, 2.0, 3.0, 4.0],
           yfmt=lambda v: f"{v:.1f}")
    p.band(0, 60, opacity=0.07, accent=False)
    p.curve([(0, 1.00), (30, 1.04), (60, 1.16), (90, 1.41), (120, 2.00), (150, 3.86)],
            accent=True)
    p.dot(60, 1.16, "60° 1.16W", dy=-12)
    p.dot(90, 1.41, "90° 1.41W", dy=-12)
    p.dot(120, 2.00, "120° 2.00W", dx=-8, dy=-10, anchor="end")
    p.dot(150, 3.86, "150° 3.86W", dx=-8, dy=6, anchor="end")
    p.text(p.X(30), p.Y(3.4), "권장 60° 이하", size=11.5, weight=600)
    p.text(p.X(126), p.Y(3.0), "금지", size=12, accent=True, weight=700)
    p.vline(90, "허용 한계")
    return p


# ─────────────────────────── 029 터보차저 ───────────────────────────

@fig("029-1")
def turbo_torque():
    p = Plot(570, 320, "과급 엔진과 자연흡기 엔진의 토크 곡선 비교",
             xlim=(700, 2400), ylim=(55, 145),
             xlabel="엔진 회전수 (rpm)", ylabel="토크 (%)")
    p.axes([800, 1200, 1600, 2000, 2400], [60, 80, 100, 120, 140])
    p.curve([(700, 88), (1000, 96), (1400, 100), (1800, 99), (2200, 94), (2400, 89)],
            dash="6 4")
    p.text(p.X(2330), p.Y(83), "자연흡기", size=11, opacity=0.8, anchor="end")
    p.curve([(700, 74), (900, 78), (1100, 92), (1300, 118), (1600, 133),
             (1900, 136), (2200, 129), (2400, 120)], accent=True)
    p.text(p.X(1750), p.Y(140), "과급 (터보)", size=11.5, accent=True, weight=600)
    p.band(700, 1150, opacity=0.08, accent=False)
    p.text(p.X(920), p.Y(64), "터보래그", size=11, weight=600)
    p.text(p.X(920), p.Y(59.5), "배기량 부족", size=10, opacity=0.7)
    p.vline(1200, "과급 개시")
    p.dot(1900, 136, "+36%", dy=-12)
    return p


# ─────────────────────────── 105 DPF ───────────────────────────

@fig("105-2")
def dpf_regen():
    p = Plot(570, 310, "PM 퇴적에 따른 DPF 차압 상승과 재생 사이클",
             xlim=(0, 100), ylim=(0, 26),
             xlabel="운전 시간 (h)", ylabel="차압 (kPa)")
    p.axes([0, 20, 40, 60, 80, 100], [0, 5, 10, 15, 20, 25])
    p.line(p.pl, p.Y(20), p.w - p.pr, p.Y(20), accent=True, dash="5 4", width=1.3)
    p.text(p.w - p.pr, p.Y(20) - 7, "재생 개시 임계값 20 kPa", size=11,
           accent=True, anchor="end", weight=600)
    saw = []
    x = 0
    for _ in range(3):
        saw += [(x, 5), (x + 26, 20)]
        x += 26
        saw += [(x + 2, 5)]
        x += 6
    p.curve([(a, b) for a, b in saw if a <= 100], smooth=False, width=1.8)
    for xr in (26, 58, 90):
        if xr <= 100:
            p.line(p.X(xr), p.Y(20), p.X(xr), p.Y(5), accent=True, width=2)
    p.text(p.X(29), p.Y(16.5), "강제 재생", size=10.5, accent=True,
           weight=600, anchor="start")
    p.text(p.X(29), p.Y(14.5), "후분사 → 배기 600℃", size=10, opacity=0.7, anchor="start")
    p.text(p.X(29), p.Y(12.5), "15~30분 · 연료 2~3%", size=10, opacity=0.7, anchor="start")
    # Ash 누적선
    p.curve([(0, 1.2), (50, 2.6), (100, 4.2)], dash="3 3", width=1.4, accent=False)
    p.text(p.X(50), p.Y(23.4), "Ash 누적 — 재생으로 제거 불가 (점선)", size=10.5,
           opacity=0.75, anchor="middle")
    return p


# ─────────────────────────── 006 무한궤도 ───────────────────────────

@fig("006-2")
def track_tension():
    p = Plot(560, 300, "트랙 장력과 하부주행체 부품 수명의 관계",
             xlim=(0, 100), ylim=(0, 110),
             xlabel="트랙 장력 (상대값)", ylabel="부품 수명 (%)")
    p.axes([0, 20, 40, 60, 80, 100], [0, 25, 50, 75, 100],
           xfmt=lambda v: {0: "이완", 50: "적정", 100: "과장력"}.get(v, ""))
    p.band(38, 62)
    p.curve([(0, 30), (15, 55), (30, 83), (42, 97), (50, 100), (58, 97),
             (72, 76), (86, 52), (100, 34)], accent=True)
    p.dot(50, 100, "최적 구간", dy=-13)
    p.text(p.X(10), p.Y(20), "탈선 · 슈 이탈", size=10.5, opacity=0.8)
    p.text(p.X(10), p.Y(12), "스프로킷 충격 마모", size=10, opacity=0.65)
    p.text(p.X(90), p.Y(24), "부싱 면압 급증", size=10.5, opacity=0.8)
    p.text(p.X(90), p.Y(16), "수명 30~50% 단축", size=10, opacity=0.65)
    p.text(p.X(50), p.Y(14), "처짐량 20~30 mm", size=11, accent=True, weight=600)
    return p


# ─────────────────────────── 016 작동유 오염 ───────────────────────────

@fig("016-1")
def wear_acceleration():
    p = Plot(570, 320, "작동유 청정도에 따른 정밀 간극 마모 진행",
             xlim=(0, 5000), ylim=(0, 24),
             xlabel="가동 시간 (h)", ylabel="간극 확대량 (㎛)")
    p.axes([0, 1000, 2000, 3000, 4000, 5000], [0, 5, 10, 15, 20],
           xfmt=lambda v: f"{v // 1000}k" if v else "0")
    p.line(p.pl, p.Y(15), p.w - p.pr, p.Y(15), dash="5 4", width=1.2, opacity=0.6)
    p.text(p.w - p.pr, p.Y(15) - 7, "성능 한계", size=10.5, anchor="end", opacity=0.7)
    p.curve([(0, 1), (1000, 2.4), (2000, 3.9), (3000, 5.5), (4000, 7.2), (5000, 9.0)])
    p.text(p.X(4850), p.Y(10.6), "NAS 9급 유지", size=11, anchor="end", weight=600)
    p.curve([(0, 1), (1000, 3.2), (2000, 6.4), (2800, 10.5), (3400, 16), (3800, 23)],
            accent=True)
    p.text(p.X(3350), p.Y(21), "오염 방치", size=11, accent=True,
           weight=600, anchor="end")
    p.dot(2800, 10.5, "임계점", dx=-10, dy=4, anchor="end")
    p.text(p.X(1200), p.Y(19), "1~10㎛ 입자가 간극에 끼어", size=10.5, anchor="start", opacity=0.8)
    p.text(p.X(1200), p.Y(17.4), "연삭 마모 → 간극 확대 → 가속", size=10.5,
           anchor="start", opacity=0.8)
    return p


# ═══════════════════════ 구조도 ═══════════════════════

@fig("011-1")
def pascal():
    f = Fig(600, 290, "파스칼의 원리에 의한 힘의 증폭과 일의 보존")
    # 소경 실린더
    f.rect(70, 120, 60, 95, r=2)
    f.rect(74, 150, 52, 61, r=1, fill=FILL)
    f.line(100, 90, 100, 148, width=2)
    f.rect(78, 82, 44, 10, r=1, fill=FILL)
    f.arrow(100, 48, 100, 78, accent=True, width=2)
    f.text(100, 40, "F₁ = 100 N", size=12.5, accent=True, weight=600)
    f.text(100, 232, "A₁ = 10 cm²", size=11.5)
    f.text(100, 248, "소경 실린더", size=10.5, opacity=0.65)
    # 대경 실린더
    f.rect(370, 120, 120, 95, r=2)
    f.rect(374, 168, 112, 43, r=1, fill=FILL)
    f.line(430, 108, 430, 166, width=2)
    f.rect(398, 100, 64, 10, r=1, fill=FILL)
    f.arrow(430, 96, 430, 66, accent=True, width=2)
    f.text(430, 56, "F₂ = 1,000 N", size=12.5, accent=True, weight=600)
    f.text(430, 232, "A₂ = 100 cm²", size=11.5)
    f.text(430, 248, "대경 실린더", size=10.5, opacity=0.65)
    # 연결 유로
    f.rect(130, 185, 240, 26, r=2, fill=FILL)
    f.text(250, 202, "밀폐 작동유   P = 10 N/cm² (전 구간 동일)", size=11)
    # 행정 표시
    f.line(146, 90, 146, 148, dash="3 3", width=1, opacity=0.6)
    f.arrow(146, 148, 146, 92, width=1.1)
    f.text(152, 122, "S₁ = 100 mm", size=10.5, anchor="start", opacity=0.8)
    f.line(506, 108, 506, 166, dash="3 3", width=1, opacity=0.6)
    f.arrow(506, 166, 506, 110, width=1.1)
    f.text(512, 142, "S₂ = 10 mm", size=10.5, anchor="start", opacity=0.8)
    # 식
    f.text(300, 275, "P = F₁/A₁ = F₂/A₂  →  힘은 면적비만큼 증폭, 행정은 그 역수만큼 감소",
           size=11.5, weight=600)
    return f


@fig("011-2")
def hydraulic_circuit():
    f = Fig(600, 340, "건설기계 기본 유압회로 구성 (ISO 1219 기호)")
    # 탱크
    f.line(58, 258, 58, 300, width=1.6); f.line(58, 300, 122, 300, width=1.6)
    f.line(122, 300, 122, 258, width=1.6)
    f.text(90, 318, "탱크", size=11)
    # 펌프
    f.circle(90, 205, 24)
    f.poly([(90, 187), (99, 200), (81, 200)], closed=True, fill="currentColor")
    f.text(90, 168, "펌프", size=11)
    f.line(90, 258, 90, 229, width=1.4)
    f.text(120, 246, "스트레이너", size=9.5, anchor="start", opacity=0.6)
    f.rect(78, 244, 24, 9, r=1, dash="2 2", width=1)
    # 펌프 → 분기
    f.line(90, 181, 90, 120, width=1.4); f.line(90, 120, 220, 120, width=1.4)
    # 릴리프 밸브
    f.rect(190, 175, 40, 46, r=2)
    f.arrow(210, 214, 210, 182, width=1.2)
    f.line(190, 152, 190, 198, dash="3 3", width=1, opacity=0.55)
    f.line(190, 152, 210, 152, dash="3 3", width=1, opacity=0.55)
    f.line(210, 152, 210, 175, dash="3 3", width=1, opacity=0.55)
    f.text(210, 240, "릴리프", size=10.5, accent=True, weight=600)
    f.text(210, 253, "32~35 MPa", size=9.5, accent=True)
    f.line(210, 221, 210, 285, width=1.4); f.line(210, 285, 122, 285, width=1.4)
    f.line(210, 120, 210, 175, width=1.4)
    # 방향제어밸브 (3위치 4포트)
    for i, x in enumerate((290, 330, 370)):
        f.rect(x, 100, 40, 44, r=0)
    f.text(310, 127, "↗↘", size=13); f.text(350, 127, "⊥⊤", size=12); f.text(390, 127, "↖↙", size=13)
    f.line(220, 120, 290, 120, width=1.4)
    f.text(330, 90, "방향제어밸브 4/3", size=11)
    f.text(330, 78, "(올포트 블록 중립)", size=9.5, opacity=0.6)
    # 실린더
    f.rect(470, 96, 100, 52, r=2)
    f.line(520, 96, 520, 148, width=1.6)
    f.rect(516, 110, 8, 24, fill="currentColor")
    f.line(524, 122, 596, 122, width=2.4)
    f.text(520, 168, "유압 실린더", size=11)
    f.text(520, 182, "F = P × A", size=10, opacity=0.7)
    f.line(410, 110, 470, 110, width=1.4)
    f.arrow(440, 110, 468, 110, accent=True, width=1.6)
    f.line(410, 138, 450, 138, width=1.4); f.line(450, 138, 450, 200, width=1.4)
    # 리턴 라인
    f.line(450, 200, 260, 200, width=1.4, dash="6 3")
    f.line(260, 200, 260, 285, width=1.4, dash="6 3")
    f.rect(248, 254, 24, 14, r=1)
    f.text(284, 262, "리턴 필터 10㎛", size=9.5, anchor="start", opacity=0.6)
    f.line(260, 285, 210, 285, width=1.4, dash="6 3")
    f.text(470, 214, "복귀 라인", size=10, opacity=0.6, anchor="end")
    return f


@fig("015-1")
def swash_pump():
    f = Fig(600, 300, "사판식 액시얼 피스톤 펌프의 토출량 가변 원리")
    for k, (ox, ang, title, note) in enumerate((
            (30, 26, "사판각 α 최대", "행정 大 → 토출량 최대"),
            (330, 9, "사판각 α 최소", "행정 小 → 토출량 최소"))):
        f.rect(ox + 20, 70, 150, 110, r=3)
        # 실린더 블록
        f.rect(ox + 60, 82, 60, 86, r=2, fill=FILL)
        f.text(ox + 90, 196, "실린더 블록", size=10, opacity=0.65)
        # 구동축
        f.line(ox + 20, 125, ox + 60, 125, width=2.4)
        f.text(ox + 26, 115, "축", size=10, opacity=0.65, anchor="start")
        # 피스톤 3개
        import math
        for j, py in enumerate((96, 125, 154)):
            stroke = 16 + ang * 0.9 - abs(j - 1) * 4
            f.line(ox + 120, py, ox + 120 + stroke, py, width=3)
            f.circle(ox + 120 + stroke + 4, py, 3.5, fill="currentColor")
        # 사판
        cx, cy = ox + 152, 125
        dx = math.tan(math.radians(ang)) * 52
        f.line(cx - dx, cy - 52, cx + dx, cy + 52, accent=True, width=3)
        f.text(ox + 95, 60, title, size=11.5, weight=600, accent=(k == 0))
        f.text(ox + 95, 224, note, size=10.5, opacity=0.75)
        # 각도 표기
        f.line(cx, cy - 52, cx, cy + 52, dash="3 3", width=1, opacity=0.5)
        f.text(cx + 8, cy - 34, "α", size=13, accent=True, weight=700, anchor="start")
    f.text(300, 262, "q = A · D · tan α · Z    →  회전수 변경 없이 토출량을 무단 조절",
           size=11.5, weight=600)
    f.text(300, 280, "A 피스톤 단면적 · D 피치원 지름 · Z 피스톤 수", size=10, opacity=0.65)
    return f


@fig("023-2")
def tc_structure():
    f = Fig(560, 290, "토크컨버터 3요소의 배치와 유체 순환 경로")
    f.text(88, 36, "엔진측", size=11, opacity=0.7)
    f.text(472, 36, "변속기측", size=11, opacity=0.7)
    # 하우징
    f.path("M120,70 Q280,44 440,70 L440,210 Q280,236 120,210 Z", width=1.2, opacity=0.35)
    # 펌프 임펠러
    f.path("M150,78 Q186,140 150,202 L128,202 Q128,140 128,78 Z", fill=FILL, width=1.5)
    f.text(140, 254, "펌프", size=11, weight=600)
    f.text(140, 268, "임펠러 (P)", size=10, opacity=0.7)
    f.line(60, 140, 128, 140, width=2.6)
    f.text(60, 128, "엔진 직결", size=10, anchor="start", opacity=0.7)
    # 터빈 러너
    f.path("M410,78 Q374,140 410,202 L432,202 Q432,140 432,78 Z", fill=FILL, width=1.5)
    f.text(420, 254, "터빈", size=11, weight=600)
    f.text(420, 268, "러너 (T)", size=10, opacity=0.7)
    f.line(432, 140, 500, 140, width=2.6)
    f.text(500, 128, "출력축", size=10, anchor="end", opacity=0.7)
    # 스테이터
    f.rect(258, 116, 44, 48, r=3, accent=True, width=2)
    f.text(280, 145, "S", size=14, accent=True, weight=700)
    f.text(280, 98, "스테이터 (고정자)", size=11, accent=True, weight=600)
    f.text(280, 186, "원웨이 클러치", size=10, opacity=0.7)
    f.text(280, 199, "일방향 고정", size=10, opacity=0.7)
    # 순환 경로
    f.path("M152,92 Q280,60 408,92", accent=True, width=2)
    f.parts.append(f'<polygon points="408,92 396,86 398,97" fill="{ACCENT}"/>')
    f.text(280, 74, "① 원심력으로 유체 가속", size=10.5, accent=True)
    f.path("M406,190 Q350,206 304,166", accent=True, width=2)
    f.parts.append(f'<polygon points="304,166 316,168 307,177" fill="{ACCENT}"/>')
    f.text(360, 218, "② 터빈 유출", size=10.5, accent=True)
    f.path("M256,152 Q210,190 154,192", accent=True, width=2)
    f.parts.append(f'<polygon points="154,192 166,186 165,197" fill="{ACCENT}"/>')
    f.text(196, 168, "③ 방향 전환 → 반력", size=10.5, accent=True)
    return f


@fig("105-1")
def dpf_wallflow():
    f = Fig(640, 292, "DPF 월플로우 구조에 의한 PM 포집 원리")
    f.rect(150, 60, 340, 160, r=4)
    f.text(320, 44, "월플로우 필터 (코디어라이트 / SiC)", size=11)
    for y in (70, 100, 130, 160, 190):
        f.line(150, y + 25, 490, y + 25, width=1, opacity=0.45)
    # 채널 마개 : 입구/출구 교대
    for i in range(5):
        y = 62 + i * 31.6
        if i % 2 == 0:
            f.rect(152, y, 16, 27, r=1, fill="currentColor", width=0)
            f.text(325, y + 18, "채널 A — 출구 막힘 → 배기가 벽을 통과", size=10, opacity=0.8)
        else:
            f.rect(472, y, 16, 27, r=1, fill="currentColor", width=0)
            f.parts.append(f'<rect x="172" y="{y+3}" width="296" height="7" fill="{ACCENT}" opacity="0.55" rx="2"/>')
            f.text(325, y + 22, "채널 B — 입구 막힘", size=10, opacity=0.8)
    f.arrow(72, 140, 146, 140, width=2.2)
    f.text(72, 128, "배기 유입", size=10.5, anchor="start")
    f.text(72, 168, "PM 0.1㎛", size=10, anchor="start", opacity=0.65)
    f.arrow(494, 140, 568, 140, width=2.2)
    f.text(568, 128, "정화 배기", size=10.5, anchor="end")
    f.text(568, 168, "포집률 90~99%", size=10, anchor="end", opacity=0.65)
    f.parts.append(f'<rect x="150" y="246" width="24" height="7" fill="{ACCENT}" opacity="0.55" rx="2"/>')
    f.text(182, 253, "PM 퇴적층", size=10.5, accent=True, anchor="start", weight=600)
    f.text(320, 280, "기공 10~20㎛ > PM 입경 0.1㎛ 이지만, 확산·차단·관성충돌로 포집된다",
           size=10.5, opacity=0.75)
    return f


@fig("006-1")
def undercarriage():
    f = Fig(620, 280, "하부주행체의 구성과 동력 전달 경로")
    # 트랙 프레임
    f.rect(90, 96, 440, 34, r=4, fill=FILL)
    f.text(310, 88, "트랙 프레임", size=10.5, opacity=0.65)
    # 스프로킷 (우), 아이들러 (좌)
    f.circle(508, 165, 34, accent=True, width=2)
    for a in range(0, 360, 30):
        import math
        r1, r2 = 34, 41
        x1 = 508 + r1 * math.cos(math.radians(a)); y1 = 165 + r1 * math.sin(math.radians(a))
        x2 = 508 + r2 * math.cos(math.radians(a)); y2 = 165 + r2 * math.sin(math.radians(a))
        f.line(round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1), accent=True, width=1.6)
    f.text(508, 232, "스프로킷", size=11, accent=True, weight=600)
    f.text(508, 245, "(기동륜) 동력 입력", size=9.5, accent=True)
    f.circle(112, 165, 30, width=2)
    f.text(112, 232, "아이들러", size=11, weight=600)
    f.text(112, 245, "(유동륜) 장력 조절", size=9.5, opacity=0.7)
    # 하부 롤러
    for x in (175, 231, 287, 343, 399, 448):
        f.circle(x, 172, 13)
    f.text(300, 262, "하부롤러 — 차체 하중 지지", size=10, opacity=0.7)
    # 상부 롤러
    f.circle(230, 92, 10); f.circle(390, 92, 10)
    f.text(310, 74, "상부롤러 — 트랙 처짐 방지", size=10, opacity=0.7)
    # 트랙
    f.path("M112,135 L508,131 M112,195 L508,199", width=2.4)
    f.path("M112,135 A30,30 0 0 0 112,195", width=2.4)
    f.path("M508,131 A34,34 0 0 1 508,199", width=2.4)
    for x in range(126, 500, 26):
        f.line(x, 199, x, 209, width=2)
    f.text(310, 224, "트랙 슈 + 링크 + 핀·부싱", size=10, opacity=0.7)
    # 동력 경로
    f.arrow(572, 165, 546, 165, accent=True, width=2)
    f.text(578, 160, "유압", size=9.5, anchor="start", accent=True)
    f.text(578, 172, "모터", size=9.5, anchor="start", accent=True)
    # 접지압
    f.line(100, 214, 520, 214, dash="4 3", width=1, opacity=0.45)
    f.text(310, 20, "접지압 p = W / (2·B·L) = 0.3~0.6 kgf/cm²  (사람이 서 있을 때와 유사)",
           size=11.5, weight=600)
    f.text(310, 36, "넓은 접지면적 → 연약지반 주행 가능 + 높은 견인계수", size=10, opacity=0.65)
    return f


# ═══════════════════ 014 유압 밸브 ═══════════════════

@fig("014-1")
def valve_classes():
    f = Fig(700, 300, "유압 밸브의 3대 분류와 회로상 위치, 제어 대상의 대응")
    f.text(350, 22, "펌프 → 밸브 → 액추에이터", size=11, opacity=0.6)
    # 펌프
    f.circle(62, 150, 22)
    f.poly([(62, 134), (70, 146), (54, 146)], closed=True, fill="currentColor")
    f.text(62, 194, "펌프", size=10.5)
    f.line(84, 150, 118, 150, width=1.6)
    cols = [
        (118, "압력 제어", ["릴리프", "리듀싱", "시퀀스", "카운터밸런스"], "힘 (P)", "회로 최고압 제한"),
        (300, "유량 제어", ["미터인", "미터아웃", "블리드오프"], "속도 (Q)", "교축으로 유량 조절"),
        (470, "방향 제어", ["4포트 3위치", "스풀식", "파일럿·솔레노이드"], "방향", "유로 전환"),
    ]
    for x, title, items, target, note in cols:
        f.rect(x, 62, 150, 176, r=5, fill=FILL)
        f.text(x + 75, 84, title, size=12.5, weight=600)
        f.line(x + 16, 94, x + 134, 94, width=1, opacity=0.35)
        for i, it in enumerate(items):
            f.text(x + 75, 114 + i * 18, "· " + it, size=10.5, opacity=0.8)
        f.text(x + 75, 202, target, size=12, accent=True, weight=700)
        f.text(x + 75, 222, note, size=9.5, opacity=0.6)
    f.arrow(268, 150, 296, 150, width=1.6)
    f.arrow(450, 150, 466, 150, width=1.6)
    f.arrow(620, 150, 618, 150, width=1.6)
    f.line(620, 150, 604, 150, width=1.6)
    f.rect(622, 130, 44, 40, r=2)
    f.line(644, 130, 644, 170, width=1.6)
    f.line(644, 150, 684, 150, width=2.4)
    f.text(650, 200, "액추에이터", size=10.5)
    f.text(350, 270, "압력은 부하가 만들고, 속도는 유량이 만든다 — 밸브의 역할은 여기서 도출된다",
           size=11.5, weight=600)
    f.text(350, 288, "제어 3요소 : 힘 · 속도 · 방향", size=10, opacity=0.6)
    return f


@fig("014-2")
def flow_control():
    f = Fig(660, 330, "미터인·미터아웃·블리드오프 회로 구성과 부하 방향에 따른 적용")
    panels = [
        (14, "미터인", "액추에이터 입구를 조인다", "저항부하 (밀기)", "붐 상승", True),
        (234, "미터아웃", "출구를 조여 배압을 만든다", "자중부하 (끌기)", "붐 하강", False),
        (454, "블리드오프", "잉여유를 탱크로 흘린다", "저항부하", "대유량 회로", True),
    ]
    for ox, title, how, load, use, meter_in in panels:
        f.rect(ox + 6, 44, 192, 208, r=5)
        f.text(ox + 102, 34, title, size=13, weight=700,
               accent=(title == "미터아웃"))
        # 펌프
        f.circle(ox + 34, 206, 15)
        f.poly([(ox + 34, 195), (ox + 40, 203), (ox + 28, 203)], closed=True, fill="currentColor")
        f.text(ox + 34, 240, "P", size=10, opacity=0.6)
        # 실린더
        f.rect(ox + 120, 72, 66, 40, r=2)
        f.line(ox + 153, 72, ox + 153, 112, width=1.6)
        f.line(ox + 153, 92, ox + 192, 92, width=2.2)
        f.text(ox + 153, 64, "실린더", size=9.5, opacity=0.6)
        # 라인
        f.line(ox + 34, 191, ox + 34, 86, width=1.4)
        f.line(ox + 34, 86, ox + 118, 86, width=1.4)
        f.line(ox + 118, 104, ox + 62, 104, width=1.4)
        f.line(ox + 62, 104, ox + 62, 222, width=1.4)
        f.line(ox + 62, 222, ox + 96, 222, width=1.4)
        f.line(ox + 96, 222, ox + 96, 236, width=1.4)
        f.text(ox + 96, 248, "T", size=10, opacity=0.6)
        # 교축 위치
        if title == "미터인":
            tx, ty = ox + 78, 86
        elif title == "미터아웃":
            tx, ty = ox + 90, 104
        else:
            tx, ty = ox + 34, 132
            f.line(ox + 34, 132, ox + 14, 132, accent=True, width=1.4)
            f.line(ox + 14, 132, ox + 14, 236, accent=True, width=1.4)
            f.text(ox + 14, 248, "T", size=10, accent=True)
        f.parts.append(
            f'<path d="M{tx - 8},{ty - 8} L{tx + 8},{ty + 8} M{tx - 8},{ty + 8} L{tx + 8},{ty - 8}" '
            f'stroke="{ACCENT}" stroke-width="2.2" fill="none"/>')
        lx, ly = (tx, ty - 14) if ty < 100 else ((tx + 30, ty + 4) if ty > 120 else (tx, ty + 22))
        f.text(lx, ly, "교축", size=10, accent=True, weight=600,
               anchor="start" if ty > 120 else "middle")
        f.text(ox + 102, 272, how, size=10, opacity=0.75)
        f.text(ox + 102, 292, load, size=11, weight=600,
               accent=(title == "미터아웃"))
        f.text(ox + 102, 310, use, size=10, opacity=0.6)
    f.text(330, 326, "자중부하에서 미터인을 쓰면 로드측 진공 → 캐비테이션 → 자주낙하",
           size=10.5, accent=True, weight=600)
    return f


@fig("014-3")
def ls_circuit():
    p = Plot(600, 320, "오픈센터·클로즈드센터·부하감응 회로의 동력 손실 비교",
             xlim=(0, 100), ylim=(0, 105),
             xlabel="부하율 (%)", ylabel="펌프 소비동력 (%)")
    p.axes([0, 20, 40, 60, 80, 100], [0, 25, 50, 75, 100])
    # 유효 동력 = 부하율에 비례
    p.curve([(0, 0), (50, 50), (100, 100)], dash="4 3", width=1.4)
    p.text(p.X(86), p.Y(78), "유효 동력", size=10.5, opacity=0.7, anchor="end")
    # 오픈센터 : 항상 최대 토출
    p.curve([(0, 92), (30, 94), (60, 96), (100, 100)], smooth=False)
    p.text(p.X(22), p.Y(99), "오픈센터 (OC)", size=11, weight=600, anchor="start")
    # 클로즈드센터
    p.curve([(0, 42), (30, 58), (60, 76), (100, 100)], smooth=False)
    p.text(p.X(40), p.Y(64), "클로즈드센터 (CC)", size=10.5, anchor="start", opacity=0.85)
    # 부하감응
    p.curve([(0, 10), (30, 40), (60, 68), (100, 100)], accent=True, smooth=False)
    p.text(p.X(34), p.Y(30), "부하감응 (LS)", size=11.5, accent=True,
           weight=700, anchor="start")
    p.parts.append(
        f'<rect x="{p.X(10)}" y="{p.Y(92)}" width="{p.X(20) - p.X(10)}" '
        f'height="{p.Y(25) - p.Y(92)}" fill="{ACCENT}" opacity="0.12"/>')
    p.dot(15, 92, "", accent=False)
    p.dot(15, 25, "")
    p.text(p.X(24), p.Y(80), "이 차이가 열로 버려진다", size=11, accent=True,
           weight=600, anchor="start")
    p.text(p.X(96), p.Y(10), "LS : 연비 10~20% 개선", size=11.5, anchor="end", weight=700)
    return p


# ═══════════════════ 019 유압 실린더 ═══════════════════

@fig("019-1")
def cylinder():
    f = Fig(660, 320, "복동 실린더의 구조와 헤드측·로드측 면적차에 의한 추력·속도 차이")
    # 본체
    f.rect(90, 96, 400, 104, r=4)
    f.rect(94, 100, 392, 96, r=2, fill=FILL, width=0)
    # 피스톤
    f.rect(292, 100, 26, 96, r=1, fill="currentColor", width=0)
    # 로드
    f.line(318, 148, 588, 148, width=7)
    f.rect(484, 132, 18, 32, r=2)
    f.text(493, 122, "로드 패킹", size=9, opacity=0.6)
    f.rect(470, 128, 12, 40, r=2, dash="2 2", width=1)
    f.text(458, 120, "와이퍼", size=9, opacity=0.6, anchor="end")
    # 포트
    f.arrow(60, 124, 88, 124, accent=True, width=2)
    f.text(56, 118, "압유", size=10, anchor="end", accent=True)
    f.arrow(516, 176, 544, 176, width=1.6)
    f.text(548, 180, "→ 탱크", size=10, anchor="start", opacity=0.7)
    f.line(490, 176, 516, 176, width=1.6)
    # 면적 표시
    f.line(140, 100, 140, 196, dash="3 3", width=1, opacity=0.55)
    f.text(190, 128, "헤드측 A₁ = πD²/4", size=11.5, weight=600)
    f.text(190, 146, "면적 大 → 추력 大, 속도 小", size=10, opacity=0.7)
    f.line(400, 100, 400, 140, dash="3 3", width=1, opacity=0.55)
    f.line(400, 156, 400, 196, dash="3 3", width=1, opacity=0.55)
    f.text(400, 178, "로드측 A₂ = π(D²−d²)/4", size=11, weight=600, accent=True)
    # 치수
    f.line(70, 96, 70, 200, width=1, opacity=0.5)
    f.arrow(70, 148, 70, 98, width=1)
    f.arrow(70, 148, 70, 198, width=1)
    f.text(62, 152, "D", size=12, anchor="end", weight=600)
    f.line(560, 132, 560, 164, width=1, opacity=0.5)
    f.text(568, 152, "d", size=12, anchor="start", weight=600)
    f.text(330, 62, "F = P · A          v = Q / A", size=14, weight=700)
    f.text(330, 80, "추력은 면적에 비례, 속도는 면적에 반비례", size=10.5, opacity=0.65)
    f.text(330, 244, "D=120 · d=70 · P=32 MPa · Q=150 ℓ/min 일 때", size=11, opacity=0.7)
    f.text(180, 268, "전진  362 kN · 0.221 m/s", size=12, weight=600)
    f.text(480, 268, "후진  239 kN · 0.335 m/s", size=12, weight=600, accent=True)
    f.text(330, 292, "면적비 1.52 : 1  →  힘이 큰 쪽은 느리고, 빠른 쪽은 약하다",
           size=11.5, weight=600)
    return f


@fig("019-2")
def rod_ratio():
    p = Plot(600, 320, "로드 지름비 d/D 에 따른 후진 추력과 속도의 변화",
             xlim=(0.3, 0.8), ylim=(0, 200),
             xlabel="로드 지름비 d / D", ylabel="전진 대비 비율 (%)")
    p.axes([0.3, 0.4, 0.5, 0.6, 0.7, 0.8], [0, 50, 100, 150, 200],
           xfmt=lambda v: f"{v:.1f}")
    p.band(0.55, 0.65)
    # 후진 추력비 = 1 - (d/D)^2
    thrust = [(r, (1 - r * r) * 100) for r in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]
    p.curve(thrust, accent=True)
    p.text(p.X(0.36), p.Y(84), "후진 추력비", size=11.5, accent=True,
           weight=600, anchor="start")
    # 후진 속도비 = 1 / (1 - (d/D)^2)
    speed = [(r, 100 / (1 - r * r)) for r in [0.3, 0.4, 0.5, 0.6, 0.7, 0.75]]
    p.curve(speed)
    p.text(p.X(0.63), p.Y(178), "후진 속도비", size=11.5, weight=600, anchor="end")
    p.line(p.pl, p.Y(100), p.w - p.pr, p.Y(100), dash="4 3", width=1, opacity=0.45)
    p.text(p.X(0.6), p.Y(18), "건설기계 통상 범위", size=11, accent=True, weight=600)
    p.text(p.X(0.6), p.Y(8), "0.55 ~ 0.65", size=11, accent=True, weight=600)
    p.dot(0.6, 64, "64%", dx=12, dy=4, anchor="start")
    p.text(p.X(0.78), p.Y(42), "로드를 굵게 하면", size=10, anchor="end", opacity=0.7)
    p.text(p.X(0.78), p.Y(32), "좌굴에 강해지나", size=10, anchor="end", opacity=0.7)
    p.text(p.X(0.78), p.Y(22), "후진 추력은 준다", size=10, anchor="end", opacity=0.7)
    return p


# ═══════════════════ 022 디젤 vs 가솔린 ═══════════════════

@fig("022-1")
def pv_diagram():
    f = Fig(660, 330, "정적(오토)·정압(디젤) 사이클의 P-V 선도 비교")
    for ox, title, comp, kind in ((20, "오토 사이클 (가솔린)", "압축비 ε = 10", "정적"),
                                  (350, "디젤 사이클 (건설기계)", "압축비 ε = 20", "정압")):
        # 축
        f.line(ox + 56, 44, ox + 56, 240, width=1.4)
        f.line(ox + 56, 240, ox + 290, 240, width=1.4)
        f.text(ox + 290, 262, "체적 V", size=10.5, anchor="end", opacity=0.75)
        f.text(ox + 40, 40, "압력 P", size=10.5, anchor="start", opacity=0.75)
        f.text(ox + 173, 26, title, size=12.5, weight=600, accent=(kind == "정압"))
        acc = kind == "정압"
        if kind == "정적":
            # 1-2 단열압축, 2-3 정적가열, 3-4 단열팽창, 4-1 정적방열
            f.path(f"M{ox+250},{240-14} C{ox+180},{240-30} {ox+120},{240-70} {ox+96},{240-118}",
                   width=2)
            f.line(ox + 96, 240 - 118, ox + 96, 240 - 186, accent=True, width=2.6)
            f.text(ox + 108, 240 - 168, "2→3 정적가열", size=9.5, anchor="start",
                   accent=True, weight=600)
            f.path(f"M{ox+96},{240-186} C{ox+140},{240-120} {ox+200},{240-56} {ox+250},{240-40}",
                   width=2)
            f.line(ox + 250, 240 - 40, ox + 250, 240 - 14, width=1.6, dash="3 3")
        else:
            f.path(f"M{ox+250},{240-14} C{ox+170},{240-34} {ox+108},{240-86} {ox+86},{240-160}",
                   width=2)
            f.line(ox + 86, 240 - 160, ox + 148, 240 - 160, accent=True, width=2.6)
            f.text(ox + 117, 240 - 170, "2→3 정압가열", size=9.5, accent=True, weight=600)
            f.path(f"M{ox+148},{240-160} C{ox+186},{240-108} {ox+216},{240-58} {ox+250},{240-40}",
                   width=2)
            f.line(ox + 250, 240 - 40, ox + 250, 240 - 14, width=1.6, dash="3 3")
        f.text(ox + 173, 284, comp, size=11, weight=600)
        eff = "이론 열효율 약 60%" if kind == "정적" else "이론 열효율 약 65%"
        f.text(ox + 173, 302, eff, size=10.5, opacity=0.75)
        f.text(ox + 173, 320, "실제 25~35%" if kind == "정적" else "실제 40~45%",
               size=11, accent=acc, weight=600)
    f.line(336, 44, 336, 268, width=1, opacity=0.22, dash="4 4")
    f.text(193, 44, "노킹 때문에 압축비 12 이상 불가", size=9.5, opacity=0.62)
    f.text(523, 44, "공기만 압축 → 노킹 제약 없음", size=9.5, opacity=0.62)
    return f


@fig("022-2")
def torque_compare():
    p = Plot(620, 330, "회전수에 따른 토크 특성 비교와 건설기계 상용 운전 영역",
             xlim=(500, 6000), ylim=(0, 120),
             xlabel="엔진 회전수 (rpm)", ylabel="최대토크 대비 (%)")
    p.axes([1000, 2000, 3000, 4000, 5000, 6000], [0, 25, 50, 75, 100],
           xfmt=lambda v: f"{v // 1000}k")
    p.band(1000, 2200)
    p.curve([(700, 82), (1000, 94), (1400, 100), (1800, 97), (2200, 88), (2500, 74)],
            accent=True)
    p.text(p.X(1250), p.Y(113), "디젤", size=12.5, accent=True, weight=700)
    p.text(p.X(1250), p.Y(105), "저속 대토크", size=10, accent=True)
    p.curve([(900, 48), (1500, 62), (2500, 78), (3500, 94), (4200, 100),
             (5000, 93), (6000, 76)], dash="6 4")
    p.text(p.X(4200), p.Y(115), "가솔린", size=12, weight=600)
    p.text(p.X(4200), p.Y(107), "고속에서 최대", size=10, opacity=0.7)
    p.text(p.X(1600), p.Y(16), "건설기계 상용 영역", size=11, accent=True, weight=600)
    p.text(p.X(1600), p.Y(7), "1,000 ~ 2,200 rpm · 최대토크 1,400 rpm", size=10, accent=True)
    p.dot(1400, 100, "")
    p.text(p.X(5700), p.Y(40), "굴착·견인은", size=10, anchor="end", opacity=0.75)
    p.text(p.X(5700), p.Y(30), "저속에서 최대 힘이", size=10, anchor="end", opacity=0.75)
    p.text(p.X(5700), p.Y(20), "필요하다", size=10, anchor="end", opacity=0.75)
    return p


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, f in sorted(FIGURES.items()):
        (OUT / f"{name}.svg").write_text(f.render(), encoding="utf-8")
    print(f"{len(FIGURES)}개 생성 → {OUT.relative_to(OUT.parents[4])}")
    for name in sorted(FIGURES):
        size = (OUT / f"{name}.svg").stat().st_size
        print(f"  {name}.svg  {size / 1024:.1f} KB  {FIGURES[name].label}")


if __name__ == "__main__":
    main()
