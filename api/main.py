from integrations.wikipedia import Wikipedia
import asyncio
from wikipedia_api.client import Client
from db import DB


async def test():
    # page_wikitext = await Client().wikitext("Radiohead")
    # print(page_wikitext)
    # async for artist in Client().transcludedin("Template:Infobox musical artist"):
    #     print(artist)

    # async for rd in Client().redirects("Joe Keery"):
    #     print(rd)
    # wikitext = await Client().wikitext("The Strokes")
    # index = wikitext.find("Radiohead")
    # start = wikitext[:index][::-1].find(".")
    # end = wikitext[index:].find(". ")
    # print(wikitext[index - start : index + end + 1])
    # print(DB().shortest_path("The Strokes", "Radiohead"))

    await Wikipedia().sync()


def main():
    # asyncio.run(Wikipedia().sync())
    asyncio.run(test())


if __name__ == "__main__":
    main()
