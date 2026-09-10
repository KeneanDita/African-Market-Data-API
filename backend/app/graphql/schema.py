from __future__ import annotations

import strawberry
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

from app.database import get_db
from app.graphql import resolvers
from app.graphql.types import CompareResult, Country, DataPoint, Indicator, IndicatorSnapshot, Region, TrendSeries
from app.middleware.api_key_auth import api_key_header, authenticate


@strawberry.type
class Query:
    countries: list[Country] = strawberry.field(resolver=resolvers.countries, description="All African countries, optionally filtered by region")
    country: Country | None = strawberry.field(resolver=resolvers.country)
    indicators: list[Indicator] = strawberry.field(resolver=resolvers.indicators)
    indicator: Indicator | None = strawberry.field(resolver=resolvers.indicator)
    data: list[DataPoint] = strawberry.field(resolver=resolvers.data, description="Time series for one country and indicator")
    compare: CompareResult = strawberry.field(resolver=resolvers.compare, description="Rank countries on one indicator")
    compare_trend: list[TrendSeries] = strawberry.field(resolver=resolvers.compare_trend)
    regions: list[Region] = strawberry.field(resolver=resolvers.regions)
    region_summary: list[IndicatorSnapshot] = strawberry.field(resolver=resolvers.region_summary)


schema = strawberry.Schema(query=Query)


async def get_context(request: Request, db: Session = Depends(get_db), api_key: str | None = Depends(api_key_header)) -> dict:
    auth = getattr(request.state, "auth", None) or authenticate(api_key, db)
    return {"request": request, "db": db, "auth": auth}


graphql_router = GraphQLRouter(schema, context_getter=get_context, graphql_ide="graphiql")
