"""Point d'entree en ligne de commande.

    python -m jobwatch run                  # veille complete
    python -m jobwatch run --only-new       # ne sortir que les nouveautes
    python -m jobwatch run --source Palexpo # une seule source, pour tester
    python -m jobwatch discover https://... # trouver la page carriere d'un site
    python -m jobwatch state --reset        # repartir a zero
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import Config
from .pipeline import discover, run
from .state import SeenState

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def _setup_logging(verbose: bool, log_file: Path | None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)-18s %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobwatch",
        description="Veille d'offres communication / marketing / evenementiel "
        "en Suisse romande.",
    )
    parser.add_argument("-c", "--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--log-file", type=Path, default=None)

    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="lancer la veille")
    run_cmd.add_argument(
        "--only-new", action="store_true",
        help="ne rapporter que les offres jamais vues",
    )
    run_cmd.add_argument(
        "--source", action="append", default=None,
        help="limiter a un employeur (repetable) ; desactive l'API job-room",
    )

    disc = sub.add_parser("discover", help="lister les liens carriere d'un site")
    disc.add_argument("url")

    st = sub.add_parser("state", help="inspecter ou reinitialiser le fichier d'etat")
    st.add_argument("--reset", action="store_true")

    sub.add_parser("sources", help="lister les sources configurees")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _setup_logging(args.verbose, args.log_file)
    cfg = Config.load(args.config)

    if args.command == "run":
        result = run(cfg, only_new=args.only_new, only=args.source)
        stats = result["stats"]
        print()
        print("Resultat :", ", ".join(f"{k} {v}" for k, v in stats.items()))
        print("CSV      :", result["csv"])
        print("Markdown :", result["markdown"])
        print()
        for offer in result["reported"][:15]:
            flag = "NEW" if offer.is_new else "   "
            print(
                f"{flag} {offer.score:3d}  {offer.title[:58]:58s} "
                f"{offer.employer[:26]:26s} {offer.location[:16]}"
            )
        return 0

    if args.command == "discover":
        for url, label in discover(args.url, cfg):
            print(f"{url}\n    {label}")
        return 0

    if args.command == "state":
        state = SeenState(cfg.state_path())
        if args.reset:
            state.entries = {}
            state.save()
            print("Etat reinitialise :", cfg.state_path())
            return 0
        print(f"{len(state.entries)} offres connues dans {cfg.state_path()}")
        for key, entry in sorted(
            state.entries.items(), key=lambda kv: kv[1].get("first_seen", ""), reverse=True
        )[:20]:
            print(
                f"  {entry.get('first_seen','?')}  {entry.get('score','?'):>3}  "
                f"{entry.get('titre','')[:55]:55s} {entry.get('employeur','')[:24]}"
            )
        return 0

    if args.command == "sources":
        jobroom = cfg.section("jobroom")
        print("API job-room :", "activee" if jobroom.get("enabled") else "desactivee")
        print("  mots-cles :", ", ".join(jobroom.get("keywords", [])))
        print("  cantons   :", ", ".join(jobroom.get("cantons", [])))
        print()
        for employer in cfg.employers:
            mark = "on " if employer.enabled else "off"
            print(f"[{mark}] {employer.name}  ({employer.category})")
            for source in employer.sources:
                target = source.url or f"{source.platform}:{source.company}"
                print(f"        {source.type:7s} {target}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
