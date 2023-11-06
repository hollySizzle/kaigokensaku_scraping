from requests_html import AsyncHTMLSession
asession = AsyncHTMLSession()
import asyncio

async def exec_js():
    resp = await asession.get("https://pycon.jp/2019/")
    print("before:", resp.html.links) # => set()
        # JSで描画
    await resp.html.arender()
    print("after", resp.html.links) # => {'https://pyconjp.connpass.com/event/139133/', ...}

loop = asyncio.get_event_loop()
loop.run_until_complete(exec_js())