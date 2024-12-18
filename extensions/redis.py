import time

from redis import Redis

from share.constants.misc import REDIS_URI

redis_client = Redis.from_url(url=REDIS_URI, decode_responses=True)


def r():
    return redis_client


# 2_getting_started
def ping():
    return r().ping()


def info(section=None):
    return r().info(section)


# 3_redis_data_management
def kset(name, value, ex=None, px=None, nx=False, xx=False, keepttl=False):
    return r().set(name, value, ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl)


def get(name):
    return r().get(name)


def delete(*names):
    return r().delete(*names)


def exists(*names):
    return r().exists(*names)


def ttl(name):
    return r().ttl(name)


def expire(name, time):
    return r().expire(name, time)


def pttl(name):
    return r().pttl(name)


def pexpire(name, time):
    return r().pexpire(name, time)


def persist(name):
    return r().persist(name)


def keys(pattern='*'):
    return r().keys(pattern)


def flushdb(asynchronous=False):
    return r().flushdb(asynchronous)


def rename(src, dst):
    return r().rename(src, dst)


def renamenx(src, dst):
    return r().renamenx(src, dst)


def unlink(*names):
    return r().unlink(*names)


def ktype(name):
    return r().type(name)


# 4_redis_data_structures_strings
# def incr(name):
#     return r().incr(name)


def incrbyfloat(name, amount):
    return r().incrbyfloat(name, amount)


def incrby(name, amount):
    return r().incrby(name, amount)


def decr(name):
    return r().decr(name)


def decrby(name, amount):
    return r().decrby(name, amount)


def strlen(name):
    return r().strlen(name)


def mset(mapping):
    return r().mset(mapping)


def mget(keys, *args):
    return r().mget(keys, *args)


def msetnx(mapping):
    return r().msetnx(mapping)


def getset(name, value):
    return r().getset(name, value)


def getrange(key, start, end):
    return r().getrange(key, start, end)


def setrange(name, offset, value):
    return r().setrange(name, offset, value)


def setex(name, time, value):
    return r().setex(name, time, value)


def psetex(name, time_ms, value):
    return r().psetex(name, time_ms, value)


def setnx(name, value):
    return r().setnx(name, value)


def kobject(infotype, key):
    return r().object(infotype, key)


def scan(cursor=0, match=None, count=None, _type=None):
    return r().scan(cursor, match, count, _type)


# 5_redis_lists
def lpush(name, *values):
    return r().lpush(name, *values)


def lrange(name, start, end):
    return r().lrange(name, start, end)


def rpush(name, *values):
    return r().rpush(name, *values)


def lindex(name, index):
    return r().lindex(name, index)


def linsert(name, where, refvalue, value):
    return r().linsert(name, where, refvalue, value)


def lpop(name):
    return r().lpop(name)


def rpop(name):
    return r().rpop(name)


def ltrim(name, start, end):
    return r().ltrim(name, start, end)


def lset(name, index, value):
    return r().lset(name, index, value)


def llen(name):
    return r().llen(name)


def lrem(name, count, value):
    return r().lrem(name, count, value)


# 6_redis_hashes
def hset(name, key=None, value=None, mapping=None):
    return r().hset(name, key, value, mapping)


def hget(name, key):
    return r().hget(name, key)


def hgetall(name):
    return r().hgetall(name)


def hmget(name, keys, *args):
    return r().hmget(name, keys, *args)


def hlen(name):
    return r().hlen(name)


def hdel(name, *keys):
    return r().hdel(name, *keys)


def hexists(name, key):
    return r().hexists(name, key)


def hkeys(name):
    return r().hkeys(name)


def hvals(name):
    return r().hvals(name)


def hincrby(name, key, amount=1):
    return r().hincrby(name, key, amount=amount)


def hincrbyfloat(name, key, amount=1.0):
    return r().hincrbyfloat(name, key, amount=amount)


def hsetnx(name, key, value):
    return r().hsetnx(name, key, value)

# 7_redis_sets
def sadd(name, *values):
    return r().sadd(name, *values)


def smembers(name):
    return r().smembers(name)


def scard(name):
    return r().scard(name)


def srem(name, *values):
    return r().srem(name, *values)


def spop(name, count=None):
    return r().spop(name, count)


def sismember(name, value):
    return r().sismember(name, value)


def srandmember(name, number=None):
    return r().srandmember(name, number)


def smove(src, dst, value):
    return r().smove(src, dst, value)


def sunion(keys, *args):
    return r().sunion(keys, *args)


def sunionstore(dest, keys, *args):
    return r().sunionstore(dest, keys, *args)


def sinter(keys, *args):
    return r().sinter(keys, *args)


def sinterstore(dest, keys, *args):
    return r().sinterstore(dest, keys, *args)


def sdiff(keys, *args):
    return r().sdiff(keys, *args)


def sdiffstore(dest, keys, *args):
    return r().sdiffstore(dest, keys, *args)


# 8_redis_sorted_sets
def zadd(name, mapping):
    return r().zadd(name, mapping)


def zrange(name, start, end, withscores=False):
    return r().zrange(name, start, end, withscores=withscores)


def zrevrange(name, start, end, withscores=False):
    return r().zrevrange(name, start, end, withscores=withscores)


def zincrby(name, amount, value):
    return r().zincrby(name, amount, value)


def zrank(name, value):
    return r().zrank(name, value)


def zrevrank(name, value):
    return r().zrevrank(name, value)


# 9_redis_hyperloglog
def pfadd(name, *values):
    return r().pfadd(name, *values)


def pfcount(*sources):
    return r().pfcount(*sources)


def pfmerge(dest, *sources):
    return r().pfmerge(dest, *sources)


# 23_redisjson
def json_set(name, path, obj):
    return r().json().set(name, path, obj)


def json_get(name, *args):
    return r().json().get(name, *args)


def json_type(name):
    return r().json().type(name)


def json_strlen(name, path):
    return r().json().strlen(name, path)


def json_strappend(name, value, path):
    return r().json().strappend(name, value, path)


def json_objlen(name, path):
    return r().json().objlen(name, path)


def json_objkeys(name, path):
    return r().json().objkeys(name, path)


def json_numincrby(name, path, number):
    return r().json().numincrby(name, path, number)


def json_delete(name, path):
    return r().json().delete(name, path)


def json_debug(name, path, subcommand='MEMORY'):
    return r().json().debug(subcommand, name, path)


def json_arrlen(name, path):
    return r().json().arrlen(name, path)


def json_arrpop(name, path, index):
    return r().json().arrpop(name, path, index)


def json_arrinsert(name, path, index, *args):
    return r().json().arrinsert(name, path, index, *args)


def mylock(key):
    while not kset(key, 1, ex=10, nx=True):
        print('日志文档已加锁，等待中。。。')
        time.sleep(0.1)


def myonlock(key):
    delete(key)
