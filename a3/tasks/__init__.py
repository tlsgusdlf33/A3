"""태스크 레지스트리.

태스크는 실행되어 Message 하나를 만들고, 상태를 갱신하고, 결과를 돌려준다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from a3.config import Config
from a3.notify import Message
from a3.store import Store


@dataclass
class TaskResult:
    name: str
    message: Message | None
    summary: str
    changed: bool = False
    extras: dict = field(default_factory=dict)


TaskFn = Callable[[Config, Store], TaskResult]

_REGISTRY: dict[str, TaskFn] = {}
_HELP: dict[str, str] = {}


def register(name: str, help_text: str) -> Callable[[TaskFn], TaskFn]:
    def deco(fn: TaskFn) -> TaskFn:
        _REGISTRY[name] = fn
        _HELP[name] = help_text
        return fn

    return deco


def get(name: str) -> TaskFn:
    if name not in _REGISTRY:
        raise KeyError(name)
    return _REGISTRY[name]


def names() -> list[str]:
    return list(_REGISTRY)


def help_text(name: str) -> str:
    return _HELP.get(name, "")


def load_all() -> None:
    """모든 태스크 모듈을 임포트해 레지스트리를 채운다."""
    from a3.tasks import brief, english, exam, radar, selfupdate  # noqa: F401
