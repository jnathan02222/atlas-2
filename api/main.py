from integrations.wikipedia import Wikipedia
import asyncio


def main():
    asyncio.run(Wikipedia().sync())


if __name__ == "__main__":
    main()
