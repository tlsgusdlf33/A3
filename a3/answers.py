"""기술사 모범답안 로딩과 분량 계산.

답안은 a3/data/answers/<문항id>.md 에 마크다운으로 둔다.
YAML 덱에 밀어 넣지 않는 이유: 한 편이 A4 3~4장이라 덱 파일이 읽을 수 없게 되고,
주간 루틴이 한 편씩 추가할 때 diff 가 지저분해진다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from a3.util import display_width

ANSWER_DIR = Path(__file__).resolve().parent / "data" / "answers"
FIGURE_DIR = ANSWER_DIR / "figures"

# A4 · 글씨크기 10pt · 여백 보통 기준의 실측값.
# 한 줄에 들어가는 표시 폭(한글 1자 = 2)과 한 장의 줄 수.
LINE_WIDTH = 90
LINES_PER_PAGE = 42

# 유형별 목표 분량(A4 장). 용어형은 1교시 10점짜리라 1장이 정답이고,
# 서술형은 2~4교시 25점이라 3~4장을 채워야 한다. 같은 기준을 쓰면 둘 다 틀린다.
PAGE_TARGET = {
    "용어형": (0.8, 1.6),
    "서술형": (3.0, 4.5),
}
DEFAULT_TARGET = (3.0, 4.5)

_META_RE = re.compile(r"^meta:\s*(\S+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$", re.MULTILINE)
_FIG_RE = re.compile(r"^!\[(그림 \d+[^\]]*)\]\(figures/([\w-]+)\.svg\)\s*$", re.MULTILINE)

# SVG 도해 한 장이 지면에서 차지하는 줄 수. 마크다운에서는 한 줄이지만
# 인쇄하면 그만큼의 높이를 먹으므로, 분량 계산에서 실제 크기로 친다.
FIGURE_LINES = 16


@dataclass
class Answer:
    card_id: str
    title: str
    kind: str
    category: str
    body: str
    path: Path

    @property
    def lines(self) -> int:
        return count_lines(self.body)

    @property
    def pages(self) -> float:
        return round(self.lines / LINES_PER_PAGE, 1)

    @property
    def target(self) -> tuple[float, float]:
        return PAGE_TARGET.get(self.kind.split("(")[0].strip(), DEFAULT_TARGET)

    @property
    def in_range(self) -> bool:
        lo, hi = self.target
        return lo <= self.pages <= hi

    @property
    def tables(self) -> int:
        return self.body.count("|---") + self.body.count("|:-")

    @property
    def svg_figures(self) -> list[tuple[str, str]]:
        """(캡션, 그림 id) 목록."""
        return [(m.group(1), m.group(2)) for m in _FIG_RE.finditer(self.body)]

    @property
    def ascii_figures(self) -> int:
        return self.body.count("```") // 2

    @property
    def figures(self) -> int:
        return len(self.svg_figures) + self.ascii_figures

    def missing_figures(self) -> list[str]:
        return [n for _, n in self.svg_figures
                if not (FIGURE_DIR / f"{n}.svg").exists()]


def count_lines(text: str) -> int:
    """A4 10pt 기준으로 몇 줄을 차지하는지 센다.

    긴 줄은 접혀서 여러 줄이 되고, 빈 줄도 한 줄을 차지한다.
    도표와 도해는 글자 수는 적어도 줄 수는 그대로 먹으므로 이 방식이 실제에 가깝다.
    """
    total = 0
    for raw in text.splitlines():
        line = raw.rstrip()
        if _FIG_RE.match(line):
            total += FIGURE_LINES
            continue
        width = display_width(line)
        total += 1 if width == 0 else -(-width // LINE_WIDTH)  # 올림
    return total


@lru_cache(maxsize=256)
def load(card_id: str) -> Answer | None:
    path = ANSWER_DIR / f"{card_id}.md"
    if not path.exists():
        return None
    body = path.read_text(encoding="utf-8")

    title_match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    meta_match = _META_RE.search(body)
    if not title_match or not meta_match:
        raise ValueError(
            f"{path.name}: 첫 줄에 '# 제목', 그 아래에 "
            f"'meta: <id> | <유형> | <분야>' 가 있어야 합니다."
        )
    if meta_match.group(1) != card_id:
        raise ValueError(f"{path.name}: meta 의 id({meta_match.group(1)})가 파일명과 다릅니다.")

    return Answer(
        card_id=card_id,
        title=title_match.group(1),
        kind=meta_match.group(2),
        category=meta_match.group(3),
        body=body,
        path=path,
    )


def available() -> set[str]:
    if not ANSWER_DIR.exists():
        return set()
    return {p.stem for p in ANSWER_DIR.glob("*.md") if p.stem != "README"}
