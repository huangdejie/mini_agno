import asyncio
import time


def task(name,seconds):
    print(f"开始任务 {name}")
    time.sleep(seconds)
    print(f"完成任务 {name}")

def run_sync_task():
    start = time.time()
    task("烧水",2)
    task("洗茶壶",1)
    print(f"总耗时:{time.time() - start:.2f}秒")
    
async def async_task(name,seconds):
    print(f"开始任务 {name}")
    await asyncio.sleep(seconds)
    print(f"完成任务 {name}")

async def run_async_task():
    start = time.time()
    await asyncio.gather(
        async_task("烧水", 2),
        async_task("洗杯子", 1),
        async_task("拿茶叶", 1)
    )
    # await async_task("烧水", 2)   
    # await async_task("洗杯子", 1) 
    print(f"总耗时: {time.time() - start:.2f} 秒") 


if __name__ == "__main__":
    run_sync_task()
    print("*******")
    asyncio.run(run_async_task())


