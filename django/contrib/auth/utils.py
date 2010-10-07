from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor
import random


UNUSABLE_PASSWORD = '!' # This will never be a valid hash


def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)
    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    parts = enc_password.split('$')
    if len(parts) != 3:
        return False
    algo, salt, hsh = parts
    return hsh == get_hexdigest(algo, salt, raw_password)


def is_password_usable(enc_password):
    return enc_password is not None and enc_password != UNUSABLE_PASSWORD


def make_password(algo, raw_password):
    """
    Produce a new password string in this format: algorithm$salt$hash
    """
    if raw_password is None:
        return UNUSABLE_PASSWORD
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hsh)
