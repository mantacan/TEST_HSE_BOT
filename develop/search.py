import requests
from telegram import Update
from telegram.ext import CallbackContext


class Search:
    def __init__(self, api_key, db_manager):
        self.api_key = api_key
        self.db_manager = db_manager

    # TEST
    async def search(self, update: Update, context: CallbackContext) -> None:
        user = (
            update.message.from_user
            if update.message
            else update.callback_query.from_user
        )
        username = f"@{user.username}" if user.username else user.full_name

        location = self.db_manager.get_user_location(username)
        if location and location[0] is not None and location[1] is not None:
            latitude, longitude = location
            results = self.find_nearest_bars_and_clubs(latitude, longitude)
            if update.message:
                await update.message.reply_text(results)
            else:
                await update.callback_query.message.reply_text(results)
        else:
            error_message = (
                "Геолокация не установлена. Пожалуйста, обновите свою геолокацию."
            )
            if update.message:
                await update.message.reply_text(error_message)
            else:
                await update.callback_query.message.reply_text(error_message)

    async def search_for_group(self, update: Update, context: CallbackContext) -> None:
        users = self.db_manager.get_all_users()
        if not users:
            await update.message.reply_text(
                "В группе нет пользователей с установленной геолокацией."
            )
            return

        latitudes = []
        longitudes = []
        for user in users:
            username = user[1]
            location = self.db_manager.get_user_location(username)
            if location and location[0] is not None and location[1] is not None:
                latitudes.append(location[0])
                longitudes.append(location[1])

        if not latitudes or not longitudes:
            await update.message.reply_text(
                "Нет доступных геолокаций участников группы."
            )
            return

        central_latitude = sum(latitudes) / len(latitudes)
        central_longitude = sum(longitudes) / len(longitudes)

        results = self.find_nearest_bars_and_clubs(central_latitude, central_longitude)
        if update.message:
            await update.message.reply_text(results)
        else:
            await update.callback_query.message.reply_text(results)

    def find_nearest_bars_and_clubs(self, latitude, longitude):
        url = "https://catalog.api.2gis.com/3.0/items"
        params = {
            "q": "бар, клуб",
            "point": f"{longitude},{latitude}",
            "radius": 5000,
            "key": self.api_key,
            "page_size": 5,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return self._parse_search_results(data)
        except requests.RequestException as e:
            return f"Ошибка при поиске: {str(e)}. Попробуйте позже."

    def _parse_search_results(self, data):
        results = []
        for item in data.get("result", {}).get("items", []):
            name = item.get("name", "Без названия")
            address = item.get("address_name", "Адрес не указан")

            geometry = item.get("geometry", {}).get("location", {})
            place_lat = geometry.get("lat", None)
            place_lon = geometry.get("lon", None)

            if place_lat is None or place_lon is None:
                coordinates = self._get_coordinates_by_address(address)
                if coordinates:
                    place_lat, place_lon = coordinates
                else:
                    place_lat, place_lon = "Не удалось определить", "координаты"

            if place_lat != "Не удалось определить" and place_lon != "координаты":
                yandex_link = self._generate_yandex_maps_link_with_name(
                    name, place_lat, place_lon
                )
            else:
                yandex_link = "Ссылка не доступна"

            results.append(f"{name}\nАдрес: {address}\nСсылка: {yandex_link}")

        if not results:
            return "Бары и клубы не найдены рядом с вами."

        return "\n\n".join(results)

    def _get_coordinates_by_address(self, address):
        """Использует OpenStreetMap Nominatim для получения координат по адресу."""
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            geo_data = response.json()

            if geo_data:
                return float(geo_data[0]["lat"]), float(geo_data[0]["lon"])
            else:
                return None
        except requests.RequestException as e:
            print(f"Ошибка при геокодировании с помощью Nominatim: {str(e)}")
            return None

    def _generate_yandex_maps_link_with_name(self, place_name, latitude, longitude):
        place_name_encoded = requests.utils.quote(place_name)
        return f"https://yandex.ru/maps/?text={place_name_encoded}&pt={longitude},{latitude}&z=16&l=map"
