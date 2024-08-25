# app/utils.py
import hmac

def safe_str_cmp(a, b):
    return hmac.compare_digest(a, b)

""" def safe_str_cmp(a, b):
    if len(a) != len(b):
        return False
    return all(x == y for x, y in zip(a, b)) """
