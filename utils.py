import requests
import logging
import json
import time

IAM_TOKEN_ENDPOINT = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
IAM_TOKEN_PATH = "token_data.json"









def create_new_iam_token():
    """
    Получает новый IAM-TOKEN и дату истечения его срока годности и
    записывает полученные данные в json
    """
    headers = {"Metadata-Flavor": "Google"}

    try:
        response = requests.get(IAM_TOKEN_ENDPOINT, headers=headers)

    except Exception as e:
        logging.error(f"Ошибка при отправке запроса: {e}")

    else:
        if response.status_code == 200:
            logging.info("Создан новый iam-токен")
            token_data = {
                "access_token": response.json().get("access_token"),
                "expires_at": response.json().get("expires_in") + time.time()
            }

            with open(IAM_TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)

        else:
            logging.error(f"Ошибка при получении ответа: {response.status_code}")


def get_iam_token() -> str:
    """
    Получает действующий IAM-TOKEN и возвращает его
    """
    try:
        with open(IAM_TOKEN_PATH, "r") as token_file:
            token_data = json.load(token_file)

        expires_at = token_data.get("expires_at")

        if expires_at <= time.time():
            logging.debug("Срок действия iam-токена истек")
            create_new_iam_token()

    except FileNotFoundError:
        logging.debug(f"Не найден файл по пути: {IAM_TOKEN_PATH}")
        create_new_iam_token()

    with open(IAM_TOKEN_PATH, "r") as token_file:
        token_data = json.load(token_file)

    return token_data.get("access_token")