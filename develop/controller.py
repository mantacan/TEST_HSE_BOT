from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    MessageHandler,
)
from location_manager import LocationManager
from search import Search
from group import Group
from database_manager import DatabaseManager
import configparser


def read_api_key_from_config(file_path: str) -> str:
    config = configparser.ConfigParser()
    config.read(file_path)
    return config["api"]["yandex_api_key"]


class Controller:
    def __init__(self, application):
        api_key = read_api_key_from_config("../config.ini")
        self.db_manager = DatabaseManager(
            db_name="bot_database",
            user="postgres",
            password="mysecretpassword",
            host="localhost",
            port="5432",
        )
        self.location_manager = LocationManager(self.db_manager)
        self.application = application
        self.search = Search(api_key=api_key, db_manager=self.db_manager)
        self.group = Group(self.db_manager)
        self._register_handlers()

    def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("menu", self.menu_handler))
        self.application.add_handler(CommandHandler("info", self.info))
        self.application.add_handler(CommandHandler("search", self.search.search))
        self.application.add_handler(
            CommandHandler("status_group", self.group.show_group_info)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.greet)
        )
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(
            CommandHandler("search_for_group", self.search.search_for_group)
        )
        self.application.add_handler(
            CommandHandler(
                "current_location", self.location_manager.show_current_location
            )
        )
        self.application.add_handler(
            CommandHandler(
                "update_location", self.location_manager.update_location_command
            )
        )
        self.application.add_handler(
            MessageHandler(filters.LOCATION, self.location_manager.update_location)
        )
        self.application.add_handler(
            CommandHandler("search_nearby", self.search_nearby)
        )
        self.application.add_handler(
            CommandHandler("add_to_group", self.group.add_to_group)
        )
        self.application.add_handler(
            CommandHandler("show_group_info", self.group.show_group_info)
        )
        self.application.add_handler(
            CommandHandler("remove_from_group", self.group.remove_from_group)
        )

    async def search_nearby(self, update: Update, context: CallbackContext) -> None:
        user = (
            update.message.from_user
            if update.message
            else update.callback_query.from_user
        )
        username = f"@{user.username}" if user.username else user.full_name

        location = self.location_manager.db_manager.get_user_location(username)

        if location and location[0] is not None and location[1] is not None:
            latitude, longitude = location
            results = self.search.find_nearest_bars_and_clubs(latitude, longitude)

            if update.message:
                await update.message.reply_text(results)
            else:
                await update.callback_query.message.reply_text(results)
        else:
            error_message = (
                "Сначала обновите свою геолокацию с помощью команды /update_location."
            )

            if update.message:
                await update.message.reply_text(error_message)
            else:
                await update.callback_query.message.reply_text(error_message)

    async def greet(self, update: Update, context: CallbackContext) -> None:
        user_text = update.message.text
        await update.message.reply_text(f"Привет, {user_text}")

    async def start(self, update: Update, context: CallbackContext) -> None:
        user = update.message.from_user
        username = f"@{user.username}" if user.username else user.full_name

        self.db_manager.add_user(username)

        keyboard = [
            [
                KeyboardButton("/menu"),
                KeyboardButton("Обновить геолокацию", request_location=True),
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        inline_keyboard = [
            [InlineKeyboardButton("Узнать о боте", callback_data="info")],
            [InlineKeyboardButton("Найти ближайший бар/клуб", callback_data="search")],
            [InlineKeyboardButton("Список группы", callback_data="status_group")],
            [
                InlineKeyboardButton(
                    "Найти бар для группы", callback_data="search_for_group"
                )
            ],
        ]
        inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)

        welcome_message = (
            "Спасибо за использование данного бота, с его помощью вы сможете найти ближайший бар для вас и ваших друзей, бот работает "
            "в двух режимах:\n"
            "Одиночный режим: бот ищет бар/клуб исходя из вашей геолокации\n"
            "Групповой режим: бот ищет бар/клуб исходя из геолокации всех участников\n\n"
            "Узнать о боте:\n/info\n\n"
            "Найти ближайший бар:\n /search\n\n"
            "Обновить геолокацию:\n /update_location\n\n"
            "Текущая геолокация:\n /current_location\n\n"
            "Список группы:\n /show_group_info\n\n"
            "Найти бар для группы:\n /search_for_group"
        )

        await update.message.reply_text(
            welcome_message, reply_markup=inline_reply_markup
        )
        await update.message.reply_text(
            "Меню доступно в любое время.", reply_markup=reply_markup
        )

    async def menu_handler(self, update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Узнать о боте", callback_data="info")],
            [InlineKeyboardButton("Найти ближайший бар", callback_data="search")],
            [
                InlineKeyboardButton(
                    "Обновить геолокацию", callback_data="update_location"
                )
            ],
            [
                InlineKeyboardButton(
                    "Текущая геолокация", callback_data="current_location"
                )
            ],
            [
                InlineKeyboardButton(
                    "Показать список группы", callback_data="show_group_info"
                )
            ],
            [
                InlineKeyboardButton(
                    "Найти бар для группы", callback_data="search_for_group"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите одну из опций:", reply_markup=reply_markup
        )

    async def button_handler(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()

        if query.data == "info":
            await self.info(update, context, is_callback=True)
        elif query.data == "search":
            await self.search.search(update, context)
        elif query.data == "update_location":
            await self.request_location(update, context)
        elif query.data == "current_location":
            await self.location_manager.show_current_location(update, context)
        elif query.data == "show_group_info":
            await self.group.show_group_info(update, context)
        elif query.data == "search_for_group":
            await self.search.search_for_group(update, context)

    async def request_location(self, update: Update, context: CallbackContext) -> None:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "Пожалуйста, отправьте свою геолокацию, используя кнопку 'Обновить геолокацию' на клавиатуре или команду /update_location."
            )
        elif update.message:
            await update.message.reply_text(
                "Пожалуйста, отправьте свою геолокацию, используя кнопку 'Обновить геолокацию' на клавиатуре или команду /update_location."
            )

    async def info(
        self, update: Update, context: CallbackContext, is_callback=False
    ) -> None:
        info_message = (
            "Спасибо за использование данного бота, с его помощью вы сможете найти ближайший бар для вас и ваших друзей, бот работает "
            "в двух режимах:\n"
            "Одиночный режим: бот ищет бар/клуб исходя из вашей геолокации\n"
            "Групповой режим: бот ищет бар/клуб исходя из геолокации всех участников\n\n"
            "Узнать о боте:\n/info\n\n"
            "Найти ближайший бар:\n /search\n\n"
            "Обновить геолокацию:\n /update_location\n\n"
            "Текущая геолокация:\n /current_location\n\n"
            "Список группы:\n /show_group_info\n\n"
            "Найти бар для группы:\n /search_for_group"
        )

        if is_callback:
            await update.callback_query.message.reply_text(info_message)
        else:
            await update.message.reply_text(info_message)
