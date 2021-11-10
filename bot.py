from aiogram.utils import executor
from create_bot import dp
from handlers import exchange_handlers
from database import postgresql


async def start_bot(_):
    print('Bot is ready to work!!!')

postgresql.sql_start()
postgresql.is_table_empty()

exchange_handlers.register_hendlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=start_bot)