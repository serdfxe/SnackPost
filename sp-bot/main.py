# /sp-bot/main.py
import asyncio
import logging
from celery import Celery
from core.config import REDIS_URL
from bot import main

logging.basicConfig(level=logging.DEBUG)

# # Инициализация Celery
# celery_app = Celery(
#     'sp_bot',
#     broker=REDIS_URL,
#     backend=REDIS_URL,
# )

# def run_celery_worker():
#     """Запуск Celery worker"""
#     celery_app.worker_main(argv=['worker', '--loglevel=info', '--pool=solo'])

# def run_celery_beat():
#     """Запуск Celery beat"""
#     celery_app.Beat(loglevel='info').run()


async def run_bot():
    """Запуск бота"""
    await main()


if __name__ == "__main__":
    # # Для Windows необходимо использовать spawn метод
    # from multiprocessing import Process, set_start_method

    # try:
    #     set_start_method('spawn')
    # except RuntimeError:
    #     pass  # Метод уже установлен

    # # Создаем процессы
    # worker_process = Process(target=run_celery_worker)
    # beat_process = Process(target=run_celery_beat)

    # # Запускаем процессы
    # worker_process.start()
    # beat_process.start()

    try:
        # Запускаем бота в основном потоке
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Остановка приложения...")
    finally:
        # Завершаем процессы
        # worker_process.terminate()
        # beat_process.terminate()
        # worker_process.join()
        # beat_process.join()
        ...
