import uvicorn

from shorts_bot.config import settings


def main() -> None:
    uvicorn.run(
        "shorts_bot.web.app:app",
        host=settings.web_host,
        port=settings.web_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
