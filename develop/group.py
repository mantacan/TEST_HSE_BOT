from telegram import Update
from telegram.ext import CallbackContext


class Group:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def show_group_info(self, update: Update, context: CallbackContext) -> None:
        users = self.db_manager.get_all_users()

        if not users:
            response = "Группа пуста. Зарегистрируйтесь в боте, чтобы присоединиться."
        else:
            info = "Информация о группе:\n"
            for user in users:
                username = user[1]
                info += f"{username}\n"
            response = info

        if update.callback_query:
            await update.callback_query.message.reply_text(response)
        elif update.message:
            await update.message.reply_text(response)

    async def add_to_group(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Все пользователи, зарегистрированные в боте, автоматически добавлены в группу."
        )

    async def remove_from_group(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Пользователей нельзя удалять из группы, так как все зарегистрированные пользователи автоматически являются частью группы."
        )

    async def manage_group(self, update: Update, context: CallbackContext) -> None:
        group_management_text = (
            "Показать информацию о группе: /show_group_info\n"
            "Все зарегистрированные пользователи автоматически добавлены в группу."
        )

        if update.callback_query:
            await update.callback_query.message.reply_text(group_management_text)
        elif update.message:
            await update.message.reply_text(group_management_text)
