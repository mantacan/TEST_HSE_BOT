from telegram import Update
from telegram.ext import CallbackContext
from database_manager import DatabaseManager

class LocationManager:
    def __init__(self, db_manager):
        self.current_location = None
        self.db_manager = db_manager

    async def update_location_command(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Пожалуйста, отправьте свою геолокацию для обновления. Нажмите на иконку скрепки и выберите 'Геолокация'.")

    async def update_location(self, update: Update, context: CallbackContext) -> None:
        if update.message.location:
            user = update.message.from_user
            username = f"@{user.username}" if user.username else user.full_name
            latitude = update.message.location.latitude
            longitude = update.message.location.longitude

            self.db_manager.update_user_location(username, latitude, longitude)

            await update.message.reply_text(
                f"Геолокация обновлена: {latitude}, {longitude}"
            )
        else:
            await update.message.reply_text(
                "Не удалось получить геолокацию. Убедитесь, что вы разрешили доступ к геолокации и попробуйте снова."
            )

    async def show_current_location(self, update: Update, context: CallbackContext) -> None:
        user = update.message.from_user if update.message else update.callback_query.from_user
        username = f"@{user.username}" if user.username else user.full_name

        location = self.db_manager.get_user_location(username)

        if location and location[0] is not None and location[1] is not None:
            latitude, longitude = location
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    f"Текущая геолокация: {latitude}, {longitude}"
                )
            elif update.message:
                await update.message.reply_text(
                    f"Текущая геолокация: {latitude}, {longitude}"
                )
        else:
            error_message = "Геолокация пока не установлена."
            if update.callback_query:
                await update.callback_query.message.reply_text(error_message)
            elif update.message:
                await update.message.reply_text(error_message)