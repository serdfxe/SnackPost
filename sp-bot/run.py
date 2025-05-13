import logging

from aiogram import Bot
from aiogram.types import Update, Message

from fastapi import FastAPI
from fastapi.requests import Request

import uvicorn

from contextlib import asynccontextmanager

from bot import create_dp

from core.config import API_TOKEN, WEBHOOK_URL


bot = Bot(token=API_TOKEN)
dp = create_dp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


processed_updates = set()

@dp.update.outer_middleware()
async def duplicate_filter(handler, update, data):
    if update.update_id in processed_updates:
        return
    processed_updates.add(update.update_id)
    return await handler(update, data)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )

    uvicorn.run(app, host="0.0.0.0", port=443)
