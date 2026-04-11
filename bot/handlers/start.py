from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from apps.db.repositories.user import get_user_by_id, register_user
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.handlers.menu import _main_text

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, session: AsyncSession):
    user_id = message.from_user.id
    user = await get_user_by_id(session, user_id)

    if not user:
        args = command.args
        referred_by = None

        if args and args.isdigit():
            referred_by_id = int(args)
            if referred_by_id != user_id:
                referrer = await get_user_by_id(session, referred_by_id)
                if referrer:
                    referred_by = referred_by_id

        user = await register_user(
            session,
            user_id,
            message.from_user.username,
            message.from_user.full_name,
            referred_by=referred_by
        )

    lang = getattr(user, "language", "ru")
    await message.answer(
        _main_text(lang),
        reply_markup=get_main_menu_keyboard(user, language=lang),
        parse_mode="HTML"
    )
