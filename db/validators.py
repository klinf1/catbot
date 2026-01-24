def validate_name(val: str) -> str:
    return val.strip().capitalize()


def validate_stat(val: int) -> int:
    if val < 0 or val > 10:
        raise ValueError("Это значение должно быть между 0 и 10!")
    return val


def validate_positive(val: int) -> int:
    if val < 1:
        raise ValueError("Это значение должно быть больше 0!")
    return val


def validate_negative(val: int) -> int:
    if val > -1:
        raise ValueError("Это значение должно быть меньше 0!")
    return val


def validate_percent(val: int) -> int:
    if val < 0 or val > 100:
        raise ValueError("Это значение должно быть между 0 и 100!")
    return val
