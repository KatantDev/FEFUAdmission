import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise import Tortoise

from tgbot.config import load_config, Config
from tgbot.handlers.enrollee import enrollee_router
from tgbot.handlers.guest import guest_router
from tgbot.services.fefu_api import save_faculties, save_agreements

logger = logging.getLogger(__name__)


async def on_startup() -> None:
    logger.error('Бот был успешно запущен!')

    new_faculties_count = await save_faculties()
    logger.info(f'Добавлено новых факультетов в базу данных: {new_faculties_count}')

    scheduler = AsyncIOScheduler()
    scheduler.add_job(save_agreements, "interval", minutes=5)
    scheduler.start()


async def run_database(config: Config) -> bool:
    try:
        await Tortoise.init(
            db_url=f'postgres://{config.db.user}:{config.db.password}@'
                   f'{config.db.host}:{config.db.port}/{config.db.name}',
            modules={'models': ['tgbot.models.database']}
        )
        await Tortoise.generate_schemas()
        return True
    except Exception as error:
        logger.error(f'Не удалось запустить базу данных. Ошибка: {error}')
        return False


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Запуск бота")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    for router in [
        guest_router,
        enrollee_router
    ]:
        dp.include_router(router)

    if await run_database(config):
        await on_startup()
        await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Бот был выключен!')
