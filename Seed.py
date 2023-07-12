import hashlib
import string
import random


def generateSeed(seed=None):
    if(seed is not None):
        rngSeed = seed
    else:
        rngSeed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    rngSeedBytes = rngSeed.encode('utf-8')
    rSeed = int(hashlib.md5(rngSeedBytes).hexdigest(),16)
    print('numeric seed is: '+str(rSeed))
    random.seed(rSeed)
    return rSeed