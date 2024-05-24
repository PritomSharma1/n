import json

def write_json(file_name: str, data: dict) -> None:
    with open(file_name, 'w') as file:
        json.dump(data, file)

def read_json(file_name: str) -> dict:
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_user_id(user_id: str):
    with open('user_ids.text', 'a') as file:
        file.write(user_id + '\n')

def read_user_ids() -> set[str]:
    with open('user_ids.text', 'r') as file:
        return set(file.read().split('\n'))
