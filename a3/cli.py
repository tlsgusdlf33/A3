"""a3 명령행 인터페이스."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
import traceback

from a3 import __version__, answers, srs, tasks, util
from a3.config import REPO_ROOT, load
from a3.notify import Message, Notifier
from a3.store import Store
from a3.tasks.decks import load_deck

DEFAULT_ORDER = ["selfupdate", "brief", "exam", "english", "radar"]
DECK_FILES = {"exam": "exam_deck.yaml", "english": "english_deck.yaml"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="a3", description="A3 — 개인 자동화 비서")
    p.add_argument("--version", action="version", version=f"a3 {__version__}")
    p.add_argument("--config", help="설정 파일 경로 (기본: repo/config.yaml)")
    p.add_argument("--dry-run", action="store_true", help="알림을 실제로 보내지 않음")
    p.add_argument("-v", "--verbose", action="store_true", help="디버그 로그")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="태스크 실행")
    run.add_argument("names", nargs="*", default=["all"],
                     help=f"실행할 태스크 (기본 all). 가능: {', '.join(DEFAULT_ORDER)}")
    run.add_argument("--no-save", action="store_true", help="상태를 저장하지 않음")

    sub.add_parser("tasks", help="사용 가능한 태스크 목록")
    sub.add_parser("status", help="학습 진행 상황 요약")

    grade = sub.add_parser("grade", help="카드 채점 (간격 반복 갱신)")
    grade.add_argument("deck", choices=sorted(DECK_FILES))
    grade.add_argument("card_id")
    grade.add_argument("quality", type=int, choices=range(6),
                       help="0~5 (3 미만이면 처음부터 다시)")

    show = sub.add_parser("show", help="카드 내용 보기")
    show.add_argument("deck", choices=sorted(DECK_FILES))
    show.add_argument("card_id")

    ans = sub.add_parser("answer", help="모범답안 전문 보기 (A4 3~4장)")
    ans.add_argument("card_id")

    sub.add_parser("answers", help="모범답안이 작성된 문항 목록")

    sub.add_parser("test-notify", help="알림 채널 점검용 메시지 발송")
    sub.add_parser("init", help="config.example.yaml 을 config.yaml 로 복사")
    return p


def cmd_run(args, config, store) -> int:
    tasks.load_all()
    names = args.names or ["all"]
    if "all" in names:
        names = DEFAULT_ORDER
    unknown = [n for n in names if n not in tasks.names()]
    if unknown:
        print(f"알 수 없는 태스크: {', '.join(unknown)}", file=sys.stderr)
        print(f"가능한 태스크: {', '.join(sorted(tasks.names()))}", file=sys.stderr)
        return 2

    notifier = Notifier(config)
    stamp = util.now().isoformat(timespec="seconds")
    failures = 0

    for name in names:
        try:
            result = tasks.get(name)(config, store)
        except Exception as exc:  # 한 태스크가 죽어도 나머지는 돌린다.
            failures += 1
            logging.getLogger(__name__).debug("%s 실패\n%s", name, traceback.format_exc())
            print(f"✗ {name}: {exc}", file=sys.stderr)
            store.log_run(name, stamp, f"실패: {exc}", ok=False)
            notifier.send(
                Message(f"⚠️ {name} 실행 실패", f"{exc}", priority="high", tags=["warning"])
            )
            continue

        if result.message is not None:
            for r in notifier.send(result.message):
                if not r.ok:
                    print(f"  · 알림 {r.channel}: {r.detail}", file=sys.stderr)
        store.log_run(name, stamp, result.summary, ok=True)
        print(f"✓ {name}: {result.summary}")

    if not args.no_save:
        store.save()
    return 1 if failures else 0


def cmd_status(config, store) -> int:
    today = util.today()
    print(f"a3 {__version__} · {today.isoformat()}")
    print(f"상태 파일: {store.path}")
    for key, filename in sorted(DECK_FILES.items()):
        try:
            cards = load_deck(filename)["cards"]
        except (FileNotFoundError, ValueError) as exc:
            print(f"  {key}: 덱 오류 — {exc}")
            continue
        state = store.deck(key)
        due = sum(1 for c in cards if (r := state.get(str(c["id"]))) and srs.is_due(r, today))
        started = len(state)
        print(f"  {key:8s} 진도 {started}/{len(cards)} · 오늘 복습 {due}장")
    runs = store.recent_runs(5)
    if runs:
        print("\n최근 실행")
        for r in runs:
            print(f"  {'✓' if r.get('ok', True) else '✗'} {r['at'][:19]} {r['task']} — {r['summary']}")
    return 0


def _find_card(deck_key: str, card_id: str):
    cards = load_deck(DECK_FILES[deck_key])["cards"]
    for c in cards:
        if str(c["id"]) == card_id:
            return c
    return None


def cmd_grade(args, store) -> int:
    if _find_card(args.deck, args.card_id) is None:
        print(f"{args.deck} 덱에 '{args.card_id}' 카드가 없습니다.", file=sys.stderr)
        return 2
    today = util.today()
    card = store.card(args.deck, args.card_id) or srs.new_card(args.card_id, today)
    updated = srs.review(card, args.quality, today)
    store.put_card(args.deck, args.card_id, updated)
    store.save()
    print(
        f"✓ {args.deck}/{args.card_id} 채점 {args.quality} → "
        f"{updated['interval']}일 뒤({updated['due']}) 다시, 난이도계수 {updated['ease']}"
    )
    return 0


def cmd_show(args) -> int:
    card = _find_card(args.deck, args.card_id)
    if card is None:
        print(f"{args.deck} 덱에 '{args.card_id}' 카드가 없습니다.", file=sys.stderr)
        return 2
    if args.deck == "exam":
        frames = load_deck(DECK_FILES["exam"]).get("frames", {})
        print(f"[{card['type']} · {card['category']}]  {card['id']}")
        print(f"Q. {card['q']}\n")
        for step in frames.get(card.get("frame_as") or card["category"], []):
            print(f"  {step}")
        print("\n키워드: " + " · ".join(card.get("keywords", [])))
    elif card.get("kind") == "speaking":
        print(f"[{card['tag']}]  {card['id']}  · {card.get('seconds', 90)}초")
        print(f"🎤 {card['q']}")
        print(f"   ({card['ko']})\n")
        print("뼈대")
        for i, step in enumerate(card.get("structure", []), 1):
            print(f"  {i}) {step}")
        print("\n쓸 표현")
        for phrase in card.get("phrases", []):
            print(f"  · {phrase}")
        if card.get("tip"):
            print(f"\n💡 {card['tip']}")
    else:
        print(f"[{card['tag']}]  {card['id']}")
        print(f"{card['front']}\n  → {card['back']}")
        if card.get("ex"):
            print(f"  ▸ {card['ex']}")
    return 0


def cmd_answer(args) -> int:
    card = _find_card("exam", args.card_id)
    if card is None:
        print(f"exam 덱에 '{args.card_id}' 문항이 없습니다.", file=sys.stderr)
        return 2
    answer = answers.load(args.card_id)
    if answer is None:
        print(f"{args.card_id}번 모범답안은 아직 작성되지 않았습니다.", file=sys.stderr)
        print(f"  문제: {card['q']}", file=sys.stderr)
        print("  `a3 show exam %s` 로 답안 틀과 키워드는 볼 수 있습니다." % args.card_id,
              file=sys.stderr)
        return 1
    lo, hi = answer.target
    print(answer.body)
    print(
        f"\n{'─' * 60}\n"
        f"{answer.card_id} · {answer.kind} · A4 {answer.pages}장 (목표 {lo}~{hi}) · "
        f"표 {answer.tables} · 도해 {answer.figures}"
    )
    return 0


def cmd_answers() -> int:
    cards = load_deck(DECK_FILES["exam"])["cards"]
    have = answers.available()
    written = [c for c in cards if str(c["id"]) in have]
    essay = [c for c in cards if c["type"] == "서술형"]
    print(f"모범답안 {len(written)}편 / 서술형 {len(essay)}문항\n")
    total = 0.0
    for card in written:
        a = answers.load(str(card["id"]))
        total += a.pages
        mark = " " if a.in_range else "!"
        print(f" {mark}{a.card_id}  A4 {a.pages}장  표{a.tables:2d} 도해{a.figures}  {a.title}")
    print(f"\n  합계 A4 {round(total, 1)}장")
    print("  전문 보기: a3 answer <문항번호>")
    return 0


def cmd_test_notify(config) -> int:
    notifier = Notifier(config)
    results = notifier.send(
        Message(
            "🔔 A3 알림 테스트",
            "이 메시지가 휴대폰에 보이면 설정이 끝난 것입니다.\n"
            f"채널: {', '.join(notifier.channels)}",
            tags=["bell"],
        )
    )
    ok = True
    for r in results:
        print(f"{'✓' if r.ok else '✗'} {r.channel}" + (f" — {r.detail}" if r.detail else ""))
        ok = ok and r.ok
    return 0 if ok else 1


def cmd_init() -> int:
    src, dst = REPO_ROOT / "config.example.yaml", REPO_ROOT / "config.yaml"
    if dst.exists():
        print(f"{dst} 가 이미 있습니다. 덮어쓰지 않습니다.")
        return 0
    shutil.copy(src, dst)
    print(f"✓ {dst} 생성. exam.date 와 notify 설정을 채우세요.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.command == "init":
        return cmd_init()

    config = load(args.config)
    if args.dry_run:
        config.data["notify"]["dry_run"] = True

    if args.command == "tasks":
        tasks.load_all()
        for name in sorted(tasks.names()):
            print(f"  {name:12s} {tasks.help_text(name)}")
        return 0
    if args.command == "show":
        return cmd_show(args)
    if args.command == "answer":
        return cmd_answer(args)
    if args.command == "answers":
        return cmd_answers()
    if args.command == "test-notify":
        return cmd_test_notify(config)

    store = Store(config.state_path)
    if args.command == "run":
        return cmd_run(args, config, store)
    if args.command == "status":
        return cmd_status(config, store)
    if args.command == "grade":
        return cmd_grade(args, store)
    return 2
