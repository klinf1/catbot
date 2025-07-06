def prepare_for_db(str_list: list[str]) -> list[str]:
    str_list = list(map(str.lower, str_list))
    str_list = list(map(str.strip, str_list))
    return str_list


def capitalize_for_db(str_list: list[str]) -> list[str]:
    return list(map(str.capitalize, str_list))
