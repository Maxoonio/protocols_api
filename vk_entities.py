from api_client import make_request, VKAPIError


def get_user_data(user_ids: str, fields: str = None):
    params = {'user_ids': user_ids}
    if fields:
        params['fields'] = fields

    try:
        response = make_request('users.get', params)
        return response if response else []
    except VKAPIError as e:
        print(f"Ошибка при получении данных пользователя '{user_ids}': {e.error_msg} (код: {e.error_code})")
        return None


def get_user_id_from_data(user_data_list: list):
    if user_data_list and isinstance(user_data_list, list) and len(user_data_list) > 0:
        return user_data_list[0].get('id')
    return None


def format_user_name(user_data_list: list):
    if user_data_list and isinstance(user_data_list, list) and len(user_data_list) > 0:
        user = user_data_list[0]
        first_name = user.get('first_name', 'N/A')
        last_name = user.get('last_name', 'N/A')
        return f"{first_name} {last_name}"
    return "Неизвестный пользователь"


def is_user_deactivated_status(user_data_item: dict):
    if user_data_item and isinstance(user_data_item, dict):
        return user_data_item.get('deactivated')  # Возвращает None или строку (e.g., 'deleted', 'banned')
    return None


def get_friends_data(user_id: int, count: int = None, offset: int = 0, fields: str = None):
    params = {'user_id': str(user_id), 'offset': offset}
    if count is not None:
        params['count'] = count
    if fields:
        params['fields'] = fields

    try:
        response = make_request('friends.get', params)
        return response
    except VKAPIError as e:
        if e.error_code in [15, 30, 204]:
            print(
                f"Не удалось получить доступ к друзьям пользователя ID {user_id}: Профиль приватный или доступ ограничен.")
        elif e.error_code == 18:
            print(f"Не удалось получить доступ к друзьям пользователя ID {user_id}: Пользователь удален или забанен.")
        else:
            print(f"Ошибка при получении друзей для ID {user_id}: {e.error_msg} (код: {e.error_code})")
        return None


def get_user_albums_data(owner_id: int, count: int = None, offset: int = 0):
    params = {'owner_id': str(owner_id)}
    if count is not None:
        params['count'] = count
    if offset is not None:
        params['offset'] = offset

    try:
        response = make_request('photos.getAlbums', params)
        return response
    except VKAPIError as e:
        if e.error_code in [15, 30, 200, 204]:
            print(
                f"Не удалось получить доступ к альбомам пользователя ID {owner_id}: Профиль/альбомы приватны или доступ ограничен.")
        elif e.error_code == 18:
            print(f"Не удалось получить доступ к альбомам пользователя ID {owner_id}: Пользователь удален или забанен.")
        else:
            print(f"Ошибка при получении альбомов для ID {owner_id}: {e.error_msg} (код: {e.error_code})")
        return None
