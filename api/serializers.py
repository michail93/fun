import asyncio
import aiohttp

from urllib.parse import urlparse

from rest_framework import serializers


class VisitedLinksSerializer(serializers.Serializer):
    links = serializers.ListField(child=serializers.CharField(max_length=300, allow_null=False, allow_blank=False),
                                  allow_empty=False)

    def validate_links(self, value):
        asyncio.run(self.check_urls(value))

        unique_domains = set()

        for result in self.result_of_checking:
            if not result[0]:
                raise serializers.ValidationError(f'link {result[1]} is not valid link')
            else:
                hostname = urlparse(result[1]).hostname
                if hostname:
                    unique_domains.add(hostname)

        return unique_domains

    async def check_func(self, client, url):
        result = True

        if not url.startswith('http'):
            url = f'http://{url}'

        try:
            await client.head(url)
        except aiohttp.ClientConnectorError:
            result = False
        except asyncio.TimeoutError:
            result = False
        except aiohttp.ClientError:
            pass

        return result, url

    async def check_urls(self, urls):
        coroutines = []
        self.result_of_checking = []

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as client:
            for url in urls:
                coroutines.append(self.check_func(client, url))

            self.result_of_checking = await asyncio.gather(*coroutines)
