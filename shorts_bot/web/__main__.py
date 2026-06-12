import uvicorn

from shorts_bot.__version__ import __version__
from shorts_bot.config import settings


def main() -> None:
    print(f"Shorts Bot v{__version__} → http://localhost:{settings.web_port}")
    uvicorn.run(
        "shorts_bot.web.app:app",
        host=settings.web_host,
        port=settings.web_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
