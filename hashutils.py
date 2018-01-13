
import hashlib
import random
import string

# random string of letters length 5
def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

# makes users pw hash, make  pw salt, and store both the pw and the salt
def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password)).hexdigest()
    return '{0},{1}'.format(hash, salt)

# checks password against hashed/salted password in db
def check_pw_hash(password, hash):
    salt = hash.split(',')[1]

    if make_pw_hash(password, salt) == hash:
        return True
    else:
        return False
