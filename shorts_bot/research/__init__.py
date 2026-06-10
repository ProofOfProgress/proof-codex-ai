"""Web + vidIQ + YouTube context gathering for deep research."""

from shorts_bot.research.google_trends import GoogleTrendsResult, fetch_google_trends
from shorts_bot.research.web_gather import WebGatherResult, gather_web_context

__all__ = ["GoogleTrendsResult", "WebGatherResult", "fetch_google_trends", "gather_web_context"]
