import redis


class RedisClient:

    client = None

    def __init__(self):
        self.client = redis.StrictRedis(
            host='127.0.0.1',
            port=6379,
            db=0
        )

    def get(self, key):

        return self.client.get(key)

    def set(self, key, value):

        self.client.set(key, value)

    def delete(self, key):
        self.client.delete(key)
