import sys


if sys.platform == 'win32' and sys.version_info.major == 3 and \
        sys.version_info.minor >= 8:
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
