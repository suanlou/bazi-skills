"""Deterministic BaZi calculation entrypoints.

This module is intentionally limited to the open-source engine surface:
birth data -> chart/rule facts. It does not include AI prompts, commercial
report templates, user profiling, or payment/product logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

from .calculation.calendar_converter import CalendarConverter
from .calculation.mingge_calculator import MinggeCalculator
from .calculation.paipan_detail_calculator import PaipanDetailCalculator
from .calculation.shishen_calculator import ShishenCalculator
from .calculation.wuxing_calculator import WuxingCalculator

PACKAGE_VERSION = "0.1.0"
CHINA_TZ = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class BirthInput:
    name: str
    gender: str
    birth_datetime: datetime
    city: str


def _resource_path(filename: str) -> str:
    return str(resources.files("miaosuan_bazi_engine.data").joinpath(filename))


def _baseline_ruleset_path() -> str:
    return _resource_path("config.baseline.json")


def _city_coordinates_path() -> str:
    return _resource_path("city_coordinates.json")


def _normalize_gender(value: Any) -> str:
    if value in ("男", "male", "m", "M", "man"):
        return "男"
    if value in ("女", "female", "f", "F", "woman"):
        return "女"
    raise ValueError("gender must be one of: 男, 女, male, female")


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("datetime must be an ISO-8601 string or datetime object")

    if parsed.tzinfo is None:
        return parsed

    # The current calculation engine models China civil time before true-solar
    # adjustment. Normalize offset-aware inputs to UTC+8, then drop tzinfo.
    return parsed.astimezone(CHINA_TZ).replace(tzinfo=None)


def _normalize_input(data: Mapping[str, Any]) -> BirthInput:
    if "datetime" not in data:
        raise ValueError("computeFromBirth requires a datetime field")

    return BirthInput(
        name=str(data.get("name") or "Anonymous"),
        gender=_normalize_gender(data.get("gender", "male")),
        birth_datetime=_parse_datetime(data["datetime"]),
        city=str(data.get("city") or data.get("city_name") or "北京"),
    )


def _split_pillar(text: str) -> dict[str, str]:
    return {"text": text, "stem": text[0], "branch": text[1]}


def _normalize_pillars(raw_pillars: Mapping[str, str]) -> dict[str, dict[str, str]]:
    return {
        "year": _split_pillar(raw_pillars["年柱"]),
        "month": _split_pillar(raw_pillars["月柱"]),
        "day": _split_pillar(raw_pillars["日柱"]),
        "hour": _split_pillar(raw_pillars["时柱"]),
    }


def _stem_ten_gods(
    sizhu: Mapping[str, str],
    shishen_calculator: ShishenCalculator,
) -> dict[str, str]:
    day_stem = sizhu["日柱"][0]
    return {
        "year_stem": shishen_calculator.determine_shishen(day_stem, sizhu["年柱"][0]),
        "month_stem": shishen_calculator.determine_shishen(day_stem, sizhu["月柱"][0]),
        "day_stem": "日主",
        "hour_stem": shishen_calculator.determine_shishen(day_stem, sizhu["时柱"][0]),
    }


def _rule_tags(
    sizhu: Mapping[str, str],
    wuxing_scores: Mapping[str, Any],
    body_strength: Mapping[str, Any],
    mingge: Mapping[str, Any],
) -> list[str]:
    tags: list[str] = []
    day_stem = sizhu["日柱"][0]
    day_branch = sizhu["日柱"][1]
    month_branch = sizhu["月柱"][1]

    tags.append(f"day_stem:{day_stem}")
    tags.append(f"day_branch:{day_branch}")
    tags.append(f"month_branch:{month_branch}")

    strength = body_strength.get("strength")
    if strength:
        tags.append(f"body_strength:{strength}")

    main_format = mingge.get("main_format")
    if main_format:
        tags.append(f"main_format:{main_format}")

    yong_shen = mingge.get("yong_shen") or []
    for item in yong_shen:
        tags.append(f"yong_shen:{item}")

    sorted_elements = sorted(
        wuxing_scores.items(),
        key=lambda item: item[1].get("力量值", 0) if isinstance(item[1], Mapping) else 0,
        reverse=True,
    )
    if sorted_elements:
        tags.append(f"dominant_element:{sorted_elements[0][0]}")
        tags.append(f"weakest_element:{sorted_elements[-1][0]}")

    return tags


def compute_from_birth(
    data: Mapping[str, Any],
    *,
    ruleset_path: str | Path | None = None,
    city_coordinates_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compute deterministic BaZi chart facts from birth data.

    Args:
        data: Mapping with `datetime`, `gender`, `city`, and optional `name`.
        ruleset_path: Optional JSON ruleset overriding baseline weights.
        city_coordinates_path: Optional city longitude table.
    """

    birth = _normalize_input(data)
    ruleset = str(ruleset_path or data.get("ruleset_path") or _baseline_ruleset_path())
    cities = str(city_coordinates_path or _city_coordinates_path())

    converter = CalendarConverter(config_path=ruleset, city_coords_path=cities)
    calendar_result = converter.process_birth_info(
        birth.birth_datetime.year,
        birth.birth_datetime.month,
        birth.birth_datetime.day,
        birth.birth_datetime.hour,
        birth.birth_datetime.minute,
        birth.city,
        birth.name,
    )
    if calendar_result is None:
        raise RuntimeError("calendar conversion failed")

    sizhu = calendar_result["四柱"]
    lunar_info = dict(calendar_result["阴历信息"])
    lunar_info.pop("lunar_obj", None)

    wuxing_calculator = WuxingCalculator(ruleset)
    shishen_calculator = ShishenCalculator(ruleset)
    mingge_calculator = MinggeCalculator(ruleset)
    paipan_calculator = PaipanDetailCalculator(ruleset)

    wuxing_scores, season, wangshui_analysis, comprehensive_analysis = (
        wuxing_calculator.calculate_wuxing_scores(sizhu, calendar_result["阴历信息"])
    )
    shishen_weights = shishen_calculator.calculate_shishen_weights(sizhu)
    body_strength = shishen_calculator.analyze_body_strength(sizhu)
    mingge = mingge_calculator.calculate_mingge(
        sizhu,
        wuxing_scores,
        shishen_weights,
        calendar_result["阴历信息"],
    )
    paipan = paipan_calculator.calculate_paipan_detail(sizhu, {"十神权重": shishen_weights})

    rule_tags = _rule_tags(sizhu, wuxing_scores, body_strength, mingge)

    return {
        "version": PACKAGE_VERSION,
        "engine": "miaosuan-bazi-engine",
        "ruleset": {
            "name": Path(ruleset).stem,
            "path": ruleset,
        },
        "input": {
            "name": birth.name,
            "gender": birth.gender,
            "datetime": birth.birth_datetime.isoformat(timespec="minutes"),
            "city": birth.city,
        },
        "time": {
            "input": calendar_result["输入时间"],
            "beijing": calendar_result["北京时间"],
            "true_solar": calendar_result["真太阳时"],
            "longitude": calendar_result["经度"],
            "longitude_delta": calendar_result["经度时差"],
            "equation_of_time": calendar_result["均时差"],
            "dst": calendar_result["夏令时信息"],
        },
        "lunar": lunar_info,
        "pillars": _normalize_pillars(sizhu),
        "day_master": {
            "stem": sizhu["日柱"][0],
            "branch": sizhu["日柱"][1],
            "pillar": sizhu["日柱"],
        },
        "wuxing": {
            "season": season,
            "scores": wuxing_scores,
            "wangshuai": wangshui_analysis,
            "summary": comprehensive_analysis,
        },
        "ten_gods": {
            "stems": _stem_ten_gods(sizhu, shishen_calculator),
            "weights": shishen_weights,
        },
        "body_strength": body_strength,
        "mingge": mingge,
        "paipan": paipan,
        "rule": {
            "tags": rule_tags,
            "basis": [
                "birth datetime normalized to China civil time",
                "true solar time adjusted by city longitude",
                "four pillars from lunar-python",
                "weights loaded from configurable ruleset JSON",
            ],
        },
    }


def computeFromBirth(
    data: Mapping[str, Any],
    *,
    ruleset_path: str | Path | None = None,
    city_coordinates_path: str | Path | None = None,
) -> dict[str, Any]:
    """JavaScript-style alias for AI agents and docs."""

    return compute_from_birth(
        data,
        ruleset_path=ruleset_path,
        city_coordinates_path=city_coordinates_path,
    )
