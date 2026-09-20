"""답안용 SVG 도해 생성기.

그림을 코드로 그리는 이유:
  · 저작권 문제가 없다 (교재·제조사 도해를 가져다 쓸 수 없다)
  · 자료함 페이지는 보안 정책상 외부 이미지를 차단한다
  · 다크모드에서도 보인다 (currentColor 상속)
  · 벡터라 확대해도 선명하고, 선 그림이라 손으로 옮겨 그릴 수 있다

색은 두 가지만 쓴다.
  · 구조선·글자 : currentColor — 페이지 전경색을 상속해 두 테마에서 모두 읽힌다
  · 강조 1색     : var(--fig-accent) — 그림이 말하려는 '그 한 가지'에만 쓴다
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field

ACCENT = "var(--fig-accent, #c4400c)"
FILL = "var(--fig-fill, rgba(0,0,0,.05))"


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


@dataclass
class Fig:
    """SVG 한 장. viewBox 좌표로 그리고 CSS 가 크기를 맞춘다."""

    w: int
    h: int
    label: str
    parts: list[str] = field(default_factory=list)

    # --- 기본 도형 ---

    def line(self, x1, y1, x2, y2, *, accent=False, dash=None, width=1.4, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{ACCENT if accent else "currentColor"}" stroke-width="{width}"'
            f' opacity="{opacity}"{d}/>'
        )

    def rect(self, x, y, w, h, *, r=3, accent=False, fill=None, width=1.4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill or "none"}" stroke="{ACCENT if accent else "currentColor"}" '
            f'stroke-width="{width}"{d}/>'
        )

    def circle(self, cx, cy, r, *, accent=False, fill=None, width=1.4):
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill or "none"}" '
            f'stroke="{ACCENT if accent else "currentColor"}" stroke-width="{width}"/>'
        )

    def path(self, d, *, accent=False, fill=None, width=1.4, dash=None, opacity=1.0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<path d="{d}" fill="{fill or "none"}" '
            f'stroke="{ACCENT if accent else "currentColor"}" stroke-width="{width}"'
            f' opacity="{opacity}"{da} stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def poly(self, points, *, accent=False, fill=None, width=1.4, closed=False, dash=None):
        pts = " ".join(f"{x},{y}" for x, y in points)
        tag = "polygon" if closed else "polyline"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<{tag} points="{pts}" fill="{fill or "none"}" '
            f'stroke="{ACCENT if accent else "currentColor"}" stroke-width="{width}"'
            f'{da} stroke-linejoin="round"/>'
        )

    def text(self, x, y, s, *, size=12, anchor="middle", accent=False,
             weight=None, opacity=1.0, mono=False):
        fw = f' font-weight="{weight}"' if weight else ""
        fam = ' font-family="IBM Plex Mono, monospace"' if mono else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"'
            f' fill="{ACCENT if accent else "currentColor"}" opacity="{opacity}"'
            f'{fw}{fam}>{esc(s)}</text>'
        )

    def arrow(self, x1, y1, x2, y2, *, accent=False, dash=None, width=1.4):
        mk = "arrА" if accent else "arr"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{ACCENT if accent else "currentColor"}" stroke-width="{width}"'
            f'{d} marker-end="url(#{mk})"/>'
        )

    def box(self, x, y, w, h, lines, *, accent=False, fill=None, size=12, r=4):
        """상자 + 가운데 정렬 텍스트 (여러 줄 가능)."""
        self.rect(x, y, w, h, r=r, accent=accent, fill=fill)
        n = len(lines)
        cy = y + h / 2 - (n - 1) * size * 0.7 + size * 0.35
        for i, ln in enumerate(lines):
            self.text(x + w / 2, cy + i * size * 1.4, ln, size=size, accent=accent)

    def render(self) -> str:
        defs = (
            '<defs>'
            '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"'
            ' markerHeight="6" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>'
            f'<marker id="arrА" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"'
            ' markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
            '</defs>'
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}"'
            f' role="img" aria-label="{esc(self.label)}"'
            f' style="max-width:100%;height:auto" fill="none">'
            f'{defs}{"".join(self.parts)}</svg>\n'
        )


def _catmull_rom(px, tension=0.5):
    """점을 실제로 지나가는 부드러운 경로.

    제어점을 수평으로 두면 각 데이터점에서 기울기가 0이 되어 봉우리가 평평해진다.
    Catmull-Rom 은 앞뒤 점의 기울기를 써서 실제 모양을 유지한다.
    """
    n = len(px)
    d = f"M{px[0][0]},{px[0][1]}"
    for i in range(n - 1):
        p0 = px[i - 1] if i > 0 else px[0]
        p1, p2 = px[i], px[i + 1]
        p3 = px[i + 2] if i + 2 < n else px[-1]
        c1 = (round(p1[0] + (p2[0] - p0[0]) * tension / 3, 2),
              round(p1[1] + (p2[1] - p0[1]) * tension / 3, 2))
        c2 = (round(p2[0] - (p3[0] - p1[0]) * tension / 3, 2),
              round(p2[1] - (p3[1] - p1[1]) * tension / 3, 2))
        d += f" C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {p2[0]},{p2[1]}"
    return d


class Plot(Fig):
    """축과 눈금이 있는 선도. 모든 눈금에 실제 수치를 붙인다."""

    def __init__(self, w, h, label, *, xlim, ylim, xlabel="", ylabel="",
                 pad=(58, 22, 46, 20)):
        super().__init__(w, h, label)
        self.x0, self.x1 = xlim
        self.y0, self.y1 = ylim
        self.pl, self.pr, self.pb, self.pt = pad  # left, right, bottom, top
        self.xlabel, self.ylabel = xlabel, ylabel

    def X(self, v):
        span = self.x1 - self.x0
        return round(self.pl + (v - self.x0) / span * (self.w - self.pl - self.pr), 2)

    def Y(self, v):
        span = self.y1 - self.y0
        return round(self.h - self.pb - (v - self.y0) / span * (self.h - self.pb - self.pt), 2)

    def axes(self, xticks, yticks, *, grid=True, xfmt=str, yfmt=str):
        if grid:
            for v in yticks:
                self.line(self.pl, self.Y(v), self.w - self.pr, self.Y(v),
                          width=0.7, opacity=0.18)
        self.line(self.pl, self.pt, self.pl, self.h - self.pb, width=1.4)
        self.line(self.pl, self.h - self.pb, self.w - self.pr, self.h - self.pb, width=1.4)
        for v in xticks:
            x = self.X(v)
            self.line(x, self.h - self.pb, x, self.h - self.pb + 4, width=1)
            self.text(x, self.h - self.pb + 17, xfmt(v), size=11, opacity=0.75, mono=True)
        for v in yticks:
            y = self.Y(v)
            self.line(self.pl - 4, y, self.pl, y, width=1)
            self.text(self.pl - 8, y + 4, yfmt(v), size=11, anchor="end",
                      opacity=0.75, mono=True)
        if self.xlabel:
            self.text(self.w - self.pr, self.h - 6, self.xlabel, size=11,
                      anchor="end", opacity=0.75)
        if self.ylabel:
            # anchor="end" 로 두면 좌측 패딩을 넘어 잘린다. 축 위에 왼쪽 정렬한다.
            self.text(4, 13, self.ylabel, size=11, anchor="start", opacity=0.75)

    def curve(self, pts, *, accent=False, dash=None, width=1.8, smooth=True):
        px = [(self.X(x), self.Y(y)) for x, y in pts]
        if not smooth or len(px) < 3:
            self.poly(px, accent=accent, dash=dash, width=width)
            return
        d = _catmull_rom(px)
        self.path(d, accent=accent, dash=dash, width=width)

    def band(self, xa, xb, *, opacity=0.09, accent=True):
        self.parts.append(
            f'<rect x="{self.X(xa)}" y="{self.pt}" width="{self.X(xb) - self.X(xa)}" '
            f'height="{self.h - self.pb - self.pt}" fill="{ACCENT if accent else "currentColor"}" '
            f'opacity="{opacity}"/>'
        )

    def vline(self, x, label=None, *, accent=True, size=11):
        self.line(self.X(x), self.pt, self.X(x), self.h - self.pb,
                  accent=accent, dash="4 3", width=1.2)
        if label:
            self.text(self.X(x), self.pt - 6, label, size=size, accent=accent, weight=600)

    def dot(self, x, y, label=None, *, accent=True, dx=0, dy=-10, anchor="middle"):
        self.circle(self.X(x), self.Y(y), 4, accent=accent, fill=ACCENT if accent else "currentColor")
        if label:
            self.text(self.X(x) + dx, self.Y(y) + dy, label, size=11,
                      accent=accent, weight=600, anchor=anchor)
