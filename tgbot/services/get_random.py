from string import ascii_uppercase, digits
from random import choice


async def random_sample() -> str:
    random_letters = ''.join(choice(ascii_uppercase) for i in range(2))
    random_digits = ''.join(choice(digits) for i in range(3))
    random_dig_let = ''.join(choice(ascii_uppercase + digits) for i in range(2))

    return f"{random_letters}-{random_digits}/{random_dig_let}"
