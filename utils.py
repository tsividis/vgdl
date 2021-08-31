import sys
import socket
from pymongo import MongoClient
from IPython import embed

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def get_mongo_client():
    ''' connect to the appropriate Mongo server '''

    if 'Momchil' in socket.gethostname():
        # mac with exploded battery -- local
        client = MongoClient('localhost', 27017)
        print 'get_mongo_client: mac pro 2017'
    elif 'HUIT' in socket.gethostname():
        # harvard mac with exploded battery -- connect to other mac
        client = MongoClient('10.0.0.98', 27017)
        print 'get_mongo_client: harvard mac'
    else:
        # cannon
        client = MongoClient('holy7c22211.rc.fas.harvard.edu', 27017, username='root', password='parolatabe', authSource='admin')
        print 'get_mongo_client: Cannon or FASSE'

    return client

