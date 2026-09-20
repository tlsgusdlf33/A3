"""자체 업데이트.

원격 브랜치에 새 커밋이 있으면 당겨오고, 무엇이 바뀌었는지 알린다.
GitHub Actions 처럼 이미 최신 코드로 체크아웃된 환경에서는 '최신' 만 보고한다.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from a3 import __version__, util
from a3.config import REPO_ROOT, Config
from a3.notify import Message
from a3.store import Store
from a3.tasks import TaskResult, register

GIT_TIMEOUT = 60


def _git(*args: str, cwd: Path = REPO_ROOT) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


@register("selfupdate", "자체 업데이트 — 원격 브랜치 최신 코드 반영")
def run(config: Config, store: Store) -> TaskResult:
    if not (REPO_ROOT / ".git").exists():
        return TaskResult(
            "selfupdate",
            Message("🔄 자체 업데이트", "git 저장소가 아닙니다. 업데이트를 건너뜁니다."),
            "git 저장소 아님",
        )

    code, branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if code != 0:
        return TaskResult("selfupdate", Message("🔄 자체 업데이트", f"브랜치 확인 실패: {branch}"), "실패")

    code, out = _git("fetch", "origin", branch)
    if code != 0:
        return TaskResult(
            "selfupdate",
            Message("🔄 자체 업데이트", f"fetch 실패:\n{util.truncate(out, 400)}"),
            "fetch 실패",
        )

    _, local = _git("rev-parse", "HEAD")
    _, remote = _git("rev-parse", f"origin/{branch}")
    if local == remote:
        body = f"이미 최신입니다.\n버전 {__version__} · {branch} @ {local[:8]}"
        return TaskResult("selfupdate", Message("🔄 자체 업데이트", body, tags=["arrows_counterclockwise"]), "최신")

    _, log = _git("log", "--oneline", "--no-decorate", f"HEAD..origin/{branch}")
    incoming = [ln for ln in log.splitlines() if ln.strip()]

    code, pull_out = _git("merge", "--ff-only", f"origin/{branch}")
    if code != 0:
        body = (
            f"새 커밋 {len(incoming)}개가 있지만 자동 반영에 실패했습니다 "
            f"(로컬 변경 충돌 가능).\n\n{util.truncate(pull_out, 400)}"
        )
        return TaskResult(
            "selfupdate",
            Message("🔄 자체 업데이트 — 수동 확인 필요", body, priority="high", tags=["warning"]),
            "ff-merge 실패",
            changed=False,
        )

    lines = [f"새 커밋 {len(incoming)}개를 반영했습니다. ({branch})", ""]
    lines += [f"  • {c}" for c in incoming[:10]]
    if len(incoming) > 10:
        lines.append(f"  … 외 {len(incoming) - 10}개")
    lines.append("")
    lines.append(f"버전 {__version__} · {remote[:8]}")
    lines.append("※ 의존성이 바뀌었다면 `pip install -r requirements.txt` 를 다시 실행하세요.")

    return TaskResult(
        "selfupdate",
        Message("🔄 자체 업데이트 완료", "\n".join(lines), tags=["arrows_counterclockwise"]),
        f"{len(incoming)}개 커밋 반영",
        changed=True,
    )
