import re

from django.utils import timezone
from rest_framework.exceptions import ValidationError


def validate_card_data(card_number, expiration_date, cvv):
    normalized_card_number = card_number.replace(" ", "").replace("-", "")
    if (
        not normalized_card_number.isdigit()
        or not 13 <= len(normalized_card_number) <= 19
    ):
        raise ValidationError({"numero_tarjeta": "El número de tarjeta no es válido."})
    if not passes_luhn_check(normalized_card_number):
        raise ValidationError({"numero_tarjeta": "El número de tarjeta no es válido."})

    expiration_match = re.fullmatch(r"(0[1-9]|1[0-2])/([0-9]{2})", expiration_date)
    if expiration_match is None:
        raise ValidationError(
            {"fecha_expiracion": "La fecha debe tener el formato MM/AA."}
        )

    month = int(expiration_match.group(1))
    year = 2000 + int(expiration_match.group(2))
    today = timezone.localdate()
    if (year, month) < (today.year, today.month):
        raise ValidationError({"fecha_expiracion": "La tarjeta está caducada."})

    if re.fullmatch(r"[0-9]{3,4}", cvv) is None:
        raise ValidationError({"cvv": "El CVV debe tener tres o cuatro dígitos."})

    return normalized_card_number


def passes_luhn_check(card_number):
    checksum = 0
    for index, character in enumerate(reversed(card_number)):
        digit = int(character)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0
