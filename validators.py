def check_name(name):
    min_length = 2
    max_length = 20
    name_length = len(name)
    if min_length <= name_length <= max_length:
        return True
    else:
        return False


def check_age(age):
    if age.isdigit() and 2 <= int(age) <= 102:
        return True
    else:
        return False


def check_gender(gender):
    if gender in ('Жінка', 'Чоловік'):
        return True
    else:
        return False
