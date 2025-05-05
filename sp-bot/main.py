import asyncio
import logging

from bot import main

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    asyncio.run(main())
