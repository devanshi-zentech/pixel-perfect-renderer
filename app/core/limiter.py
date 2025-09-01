from slowapi import Limiter
from slowapi.util import get_remote_address

# This function determines how to identify a client. By default, it uses the client's IP address.
limiter = Limiter(key_func=get_remote_address)
# print("Limiter", limiter.__dict__)