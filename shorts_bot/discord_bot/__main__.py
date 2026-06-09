import logging

from shorts_bot.discord_bot.bot import run_bot

logging.basicConfig(level=logging.INFO)


def main() -> None:
    run_bot()


if __name__ == "__main__":
    main()
