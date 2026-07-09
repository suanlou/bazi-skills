"""MCP stdio wrapper for the Miaosuan BaZi engine."""

from __future__ import annotations

from typing import Any

from .engine import computeFromBirth


def _load_fastmcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP support is optional. Install it with: pip install -e '.[mcp]'"
        ) from exc
    return FastMCP


FastMCP = _load_fastmcp()
mcp = FastMCP("miaosuan-bazi")


@mcp.tool()
def compute_bazi(
    datetime: str,
    gender: str,
    city: str,
    name: str = "Anonymous",
    ruleset_path: str | None = None,
) -> dict[str, Any]:
    """Calculate deterministic BaZi facts from birth datetime, gender, and city."""

    return computeFromBirth(
        {
            "name": name,
            "gender": gender,
            "datetime": datetime,
            "city": city,
        },
        ruleset_path=ruleset_path,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
