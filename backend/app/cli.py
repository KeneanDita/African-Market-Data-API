"""Management commands.

    python -m app.cli init-db                  # create tables (dev) - prod uses alembic
    python -m app.cli seed                     # 54 countries + 87 indicators
    python -m app.cli scrape --source world_bank [--from 2000] [--only GDP_CURRENT_USD,POPULATION_TOTAL]
    python -m app.cli scrape --source all
    python -m app.cli create-key --email you@example.com --name "You" [--tier pro]
    python -m app.cli set-tier --email you@example.com --tier pro
    python -m app.cli stats
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from sqlalchemy import func

from app.config import settings
from app.database import Base, SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

SOURCES = ("world_bank", "imf", "who", "un_data", "afdb")


def cmd_init_db(_: argparse.Namespace) -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print(f"tables created on {engine.url.render_as_string(hide_password=True)}")


def cmd_seed(_: argparse.Namespace) -> None:
    from app.utils.countries_seed import seed_countries
    from app.utils.indicators_seed import seed_indicators

    cmd_init_db(_)
    with SessionLocal() as db:
        c = seed_countries(db)
        i = seed_indicators(db)
    print(f"seeded: {c} new countries, {i} new indicators (existing rows refreshed)")


def cmd_scrape(args: argparse.Namespace) -> None:
    from_year = args.from_year or settings.scrape_from_year
    to_year = args.to_year or settings.scrape_to_year
    only = [c.strip().upper() for c in args.only.split(",")] if args.only else None
    sources = SOURCES if args.source == "all" else (args.source,)

    async def run_all():
        results = {}
        for src in sources:
            if src == "world_bank":
                from app.scrapers.world_bank import scrape_all

                results[src] = (await scrape_all(from_year, to_year, only_codes=only)).as_dict()
            else:
                module = __import__(f"app.scrapers.{src}", fromlist=["scrape_all"])
                results[src] = (await module.scrape_all(from_year, to_year)).as_dict()
        return results

    results = asyncio.run(run_all())
    from app.middleware.response_cache import invalidate_response_cache

    invalidate_response_cache()
    for src, stats in results.items():
        print(f"{src:12s} {stats}")


def cmd_create_key(args: argparse.Namespace) -> None:
    from app.models.api_user import TIER_LIMITS, ApiUser
    from app.utils.security import generate_api_key, hash_api_key, key_prefix

    with SessionLocal() as db:
        if db.query(ApiUser).filter(ApiUser.email == args.email.lower()).first():
            sys.exit(f"a key already exists for {args.email}; use set-tier or rotate-key")
        raw = generate_api_key()
        db.add(ApiUser(email=args.email.lower(), name=args.name, api_key_hash=hash_api_key(raw), key_prefix=key_prefix(raw), tier=args.tier, rate_limit=TIER_LIMITS[args.tier]))
        db.commit()
    print(f"API key for {args.email} ({args.tier}): {raw}")
    print("Store it now - only its hash is kept in the database.")


def cmd_rotate_key(args: argparse.Namespace) -> None:
    from app.middleware.api_key_auth import invalidate_auth_cache
    from app.models.api_user import ApiUser
    from app.utils.security import generate_api_key, hash_api_key, key_prefix

    with SessionLocal() as db:
        user = db.query(ApiUser).filter(ApiUser.email == args.email.lower()).first()
        if not user:
            sys.exit(f"no user for {args.email}")
        invalidate_auth_cache(user.api_key_hash)
        raw = generate_api_key()
        user.api_key_hash = hash_api_key(raw)
        user.key_prefix = key_prefix(raw)
        db.commit()
    print(f"new API key for {args.email}: {raw}")


def cmd_set_tier(args: argparse.Namespace) -> None:
    from app.middleware.api_key_auth import invalidate_auth_cache
    from app.models.api_user import TIER_LIMITS, ApiUser

    with SessionLocal() as db:
        user = db.query(ApiUser).filter(ApiUser.email == args.email.lower()).first()
        if not user:
            sys.exit(f"no user for {args.email}")
        user.tier = args.tier
        user.rate_limit = TIER_LIMITS[args.tier]
        db.commit()
        invalidate_auth_cache(user.api_key_hash)
    print(f"{args.email} -> {args.tier} ({TIER_LIMITS[args.tier]} req/h)")


def cmd_stats(_: argparse.Namespace) -> None:
    from app.models import ApiUser, Country, DataPoint, Indicator, RequestLog

    with SessionLocal() as db:
        print(f"countries    : {db.query(func.count(Country.id)).scalar()}")
        print(f"indicators   : {db.query(func.count(Indicator.id)).scalar()}")
        print(f"data points  : {db.query(func.count(DataPoint.id)).scalar()}")
        print(f"api users    : {db.query(func.count(ApiUser.id)).scalar()}")
        print(f"request logs : {db.query(func.count(RequestLog.id)).scalar()}")
        covered = db.query(func.count(func.distinct(DataPoint.indicator_id))).scalar()
        print(f"indicators with data: {covered}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="African Market Data API management")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db").set_defaults(func=cmd_init_db)
    sub.add_parser("seed").set_defaults(func=cmd_seed)
    sub.add_parser("stats").set_defaults(func=cmd_stats)

    p = sub.add_parser("scrape")
    p.add_argument("--source", choices=(*SOURCES, "all"), default="world_bank")
    p.add_argument("--from", dest="from_year", type=int)
    p.add_argument("--to", dest="to_year", type=int)
    p.add_argument("--only", help="comma-separated indicator codes (world_bank only)")
    p.set_defaults(func=cmd_scrape)

    for name, fn in (("create-key", cmd_create_key), ("rotate-key", cmd_rotate_key), ("set-tier", cmd_set_tier)):
        p = sub.add_parser(name)
        p.add_argument("--email", required=True)
        if name == "create-key":
            p.add_argument("--name")
        if name in ("create-key", "set-tier"):
            p.add_argument("--tier", choices=("free", "pro", "enterprise"), default="free" if name == "create-key" else None, required=name == "set-tier")
        p.set_defaults(func=fn)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
