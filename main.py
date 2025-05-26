import time
from vk_entities import (
    get_user_data,
    get_user_id_from_data,
    format_user_name,
    is_user_deactivated_status,
    get_friends_data,
    get_user_albums_data
)
from api_client import VKAPIError, ACCESS_TOKEN

if not ACCESS_TOKEN:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!! ВНИМАНИЕ: Пожалуйста, установите ваш реальный ACCESS_TOKEN в файле config.py !!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


def display_friends_details(target_user_id: int, target_user_name: str, requested_friends_display_count: int = None):
    print(f"\n Получение списка друзей для {target_user_name} (ID: {target_user_id})...")

    friends_response = get_friends_data(
        user_id=target_user_id,
        count=requested_friends_display_count,
        fields='first_name,last_name,deactivated,id'
    )

    if not friends_response:
        return

    friend_items = friends_response.get('items', [])
    total_friends_of_target = friends_response.get('count', 0)

    if not friend_items:
        if total_friends_of_target > 0:
            print(
                f" У пользователя {target_user_name} {total_friends_of_target} друзей, но детали не могут быть загружены (например, все приватные или нет прав на поля).")
        else:
            print(f" У пользователя {target_user_name} нет друзей или их список недоступен.")
        return

    print(
        f"\n--- Друзья пользователя {target_user_name} (ID: {target_user_id}) (отображается до {len(friend_items)} из {total_friends_of_target}) ---")

    for friend_obj in friend_items:
        friend_id = friend_obj.get('id')
        friend_first_name = friend_obj.get('first_name', 'Имя не указано')
        friend_last_name = friend_obj.get('last_name', '')
        friend_full_name = f"{friend_first_name} {friend_last_name}".strip()

        deactivated_status = friend_obj.get('deactivated')

        if deactivated_status:
            print(f"\nДруг: {friend_full_name} (ID: {friend_id}) - ДЕАКТИВИРОВАН ({deactivated_status}).")
            continue

        print(f"\n👤 Друг: {friend_full_name} (ID: {friend_id})")

        try:
            time.sleep(0.35)

            friends_of_friend_response = get_friends_data(user_id=friend_id)
            if friends_of_friend_response:
                friends_of_friend_count = friends_of_friend_response.get('count', 'N/A')
                print(f"Количество друзей: {friends_of_friend_count}")
            else:
                print(f"Количество друзей: не удалось получить.")
        except VKAPIError as e_inner:
            print(f"Количество друзей: Ошибка VK API - {e_inner.error_msg}")
        except Exception as e_gen:
            print(f"Количество друзей: Произошла неожиданная ошибка: {e_gen}")


def display_albums_details(user_id: int, user_display_name: str):
    print(f"\nПолучение альбомов для {user_display_name} (ID: {user_id})...")
    albums_response = get_user_albums_data(owner_id=user_id)

    if not albums_response:
        return

    albums_count = albums_response.get('count', 0)
    album_items = albums_response.get('items', [])

    print(f"\n---Альбомы пользователя {user_display_name} (ID: {user_id}) ---")
    print(f"Всего альбомов: {albums_count}")

    if not album_items and albums_count > 0:
        print(
            "Не удалось получить детали альбомов, хотя альбомы существуют (возможно, проблема с правами доступа к деталям).")
    elif not album_items:
        print("Фотоальбомы не найдены или недоступны.")
    else:
        for i, album in enumerate(album_items):
            album_title = album.get('title', 'Альбом без названия')
            album_size = album.get('size', 0)
            print(f"\n{i + 1}. Альбом: \"{album_title}\"")
            print(f"   Количество фото: {album_size}")


def run_app():
    print("========================================")
    print(" VK API Data Retriever by Gemini & User ")
    print("========================================")

    user_id_or_name_input = input("Введите ID или короткое имя пользователя (например, '1' или 'durov'): ").strip()
    if not user_id_or_name_input:
        print("ID пользователя не может быть пустым.")
        return

    try:
        print(f"\nЗапрос данных для пользователя: '{user_id_or_name_input}'...")
        user_data_list = get_user_data(user_id_or_name_input, fields='deactivated')

        if not user_data_list:
            return

        target_user_main_data = user_data_list[0]

        current_user_id = get_user_id_from_data([target_user_main_data])
        current_user_name = format_user_name([target_user_main_data])

        if not current_user_id:
            print("Не удалось получить ID пользователя.")
            return

        print(f"\n👤 Информация для пользователя: {current_user_name} (ID: {current_user_id})")

        deactivated_status = is_user_deactivated_status(target_user_main_data)
        if deactivated_status:
            print(f"Статус пользователя: {deactivated_status.upper()}")

        while True:
            print("\nДоступные действия:")
            print("1. 🧑‍🤝‍🧑 Друзья (вывести список друзей пользователя и их кол-во друзей)")
            print("2. 🏞️ Альбомы (вывести список фотоальбомов пользователя)")
            req = input("⌨️ Введите номер опции (1 или 2) или 'выход' для завершения: ").strip().lower()

            if req == '1' or req == 'друзья':
                friends_count_input_str = input(
                    "❔ Скольких друзей отобразить информацию? (Enter - по умолчанию API, обычно до 5000): ").strip()
                requested_display_count = None
                if friends_count_input_str.isdigit():
                    requested_display_count = int(friends_count_input_str)

                display_friends_details(current_user_id, current_user_name, requested_display_count)
                break
            elif req == '2' or req == 'альбомы':
                display_albums_details(current_user_id, current_user_name)
                break
            elif req == 'выход' or req == 'exit':
                print("👋 Завершение работы.")
                break
            else:
                print("Некорректный ввод. Пожалуйста, выберите '1', '2', или 'выход'.")

    except VKAPIError as e:
        print(f"Произошла ошибка VK API: {e.error_code} - {e.error_msg}")
        if e.request_params:
            pass
    except ConnectionError as e:
        print(f"Ошибка сети: {e}")
    except ValueError as e:
        print(f"🛠Ошибка обработки данных: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_app()
