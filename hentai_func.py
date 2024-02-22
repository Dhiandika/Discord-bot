from enum import Enum
from random import choice, shuffle
from typing import Optional
import aiohttp
from requests import get


class NsfwApis(Enum):
    Rule34Api = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=1000&tags=rating:explicit+"
    KonachanApi = "https://konachan.com/post.json?s=post&q=index&limit=100&tags=rating:explicit+"
    YandereApi = "https://yande.re/post.json?limit=100&tags=rating:explicit+"
    GelbooruApi = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags=rating:explicit+"
    DanbooruApi = "https://danbooru.donmai.us/posts.json?limit=100&tags=rating:explicit+"


class NekosFunTags(Enum):
    anal = "anal"
    blowjob = "bj"
    cum = "cum"
    hentai = "hentai"
    yuri = "lesbian"


class Hentai:
    def __init__(self):
        self.blacklisted_tags = {"cub"}

    def format_tags(self, tags: str = None):
        if tags:
            tags = [
                tag.strip().replace(" ", "_")
                for tag in tags.split(",")
                if tag.strip().replace(" ", "_")
            ]
            tags_string = "+".join(tags)
            return tags_string
        else:
            return ""

    async def get_nsfw_image(self, provider: NsfwApis, tags: Optional[str] = None):
        tags = tags.lower() if tags else None

        url = provider.value + self.format_tags(tags)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                nsfw_images = await resp.json()

        if not nsfw_images:
            return None

        if provider.value == NsfwApis.GelbooruApi.value:
            nsfw_images_list = list(nsfw_images.get("post", []))
        else:
            nsfw_images_list = list(nsfw_images)

        shuffle(nsfw_images_list)

        if not tags:
            tags = ""

        tags_list = [
            tag.strip().replace(" ", "_")
            for tag in tags.split(",")
            if tag.strip().replace(" ", "_") not in self.blacklisted_tags
        ]

        if len(tags_list) == 0 or len(tags_list) > 3:
            return None

        filtered_ret = [
            img
            for img in nsfw_images_list
            if all(
                tag in img["tag_string"] if provider is NsfwApis.DanbooruApi else tag in img["tags"]
                for tag in tags_list
            )
        ]

        if len(filtered_ret) == 0:
            return None

        filtered_images = []
        for image in filtered_ret:
            tags = (
                image["tag_string"].lower().split(" ")
                if provider is NsfwApis.DanbooruApi
                else image["tags"].lower().split(" ")
            )
            if any(tag in self.blacklisted_tags for tag in tags):
                continue
            filtered_images.append(image)
        return choice(filtered_images)


    @staticmethod
    def nekofun(endpoint: str):
        r = get("http://api.nekos.fun:8080/api/" + endpoint)
        if r.status_code != 200:
            return False
        else:
            return str(r.json()["image"])

    @staticmethod
    def boobchi():
        r = get("https://bocchi-api.vercel.app/JSON")
        if r.status_code != 200:
            return False
        else:
            image=str(r.json()["imgURL"])
            source=str(r.json()["sauceURL"])
            return image, source



