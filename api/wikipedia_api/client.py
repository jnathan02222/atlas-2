import httpx
from httpx import Response
import asyncio


class Client:
    async def api_request(
        self, url="https://en.wikipedia.org/w/api.php", params={}, backoff=1
    ) -> Response:
        headers = {
            "User-Agent": "Atlas-2 https://github.com/jnathan02222/atlas-2",
        }

        async with httpx.AsyncClient() as client:
            request = await client.get(
                url=url, params=params, headers=headers, timeout=30.0
            )

        if request.status_code == 429 and backoff < 32:
            await asyncio.sleep(backoff)
            return await self.api_request(url, params, backoff * 2)
        elif not request.status_code == 200:
            raise Exception(request.text)

        return request

    async def paginated_api_request(self, params, continue_accessor):
        data = (await self.api_request(params=params)).json()
        yield data
        while "continue" in data:
            params[continue_accessor] = data["continue"][continue_accessor]
            data = (await self.api_request(params=params)).json()
            yield data

    async def transcludedin(self, title):
        def process_data(data):
            page = next(iter(data["query"]["pages"].values()))
            for artist in page["transcludedin"]:
                yield artist

        params = {
            "action": "query",
            "titles": title,
            "prop": "transcludedin",
            "format": "json",
            "tilimit": 500,
            "tinamespace": 0,
        }

        async for data in self.paginated_api_request(params, "ticontinue"):
            for item in process_data(data):
                yield item

    async def wikitext(self, title) -> str:
        params = {
            "action": "raw",
            "title": title,
        }
        return (
            await self.api_request(
                url="https://en.wikipedia.org/w/index.php", params=params
            )
        ).text

    async def links(self, title):
        def process_data(data):
            page = next(iter(data["query"]["pages"].values()))
            if "links" not in page:
                return

            for link in page["links"]:
                yield link

        params = {
            "action": "query",
            "titles": title,
            "prop": "links",
            "format": "json",
            "pllimit": 500,
            "plnamespace": 0,
        }

        async for data in self.paginated_api_request(params, "plcontinue"):
            for item in process_data(data):
                yield item

    # async def redirects(self, title):
    #     def process_data(data):
    #         page = next(iter(data["query"]["pages"].values()))
    #         if "redirects" not in page:
    #             return

    #         for link in page["redirects"]:
    #             yield link

    #     params = {
    #         "action": "query",
    #         "titles": title,
    #         "prop": "redirects",
    #         "format": "json",
    #         "rdlimit": 500,
    #         "rdnamespace": 0,
    #     }

    #     async for data in self.paginated_api_request(params, "rdcontinue"):
    #         for item in process_data(data):
    #             yield item
