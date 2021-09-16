import asyncio


queue = asyncio.Queue()


async def producer(item):
    await queue.put(item)


async def consumer():
    while True:
        task = await queue.get()
        print(task)


async def main():
    asyncio.ensure_future(consumer())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(consumer())
    asyncio.run(producer(1))
    # loop.run_until_complete(main())
    # asyncio.run(producer(123))
