# coding=utf-8
import redis

def insert_start_url():

    redis_client = redis.Redis(host="127.0.0.1", port=6379)
    if redis_client.exists('start_urls'):
        source, url = redis_client.blpop('start_urls')
        redis_client.lpush("cnca:start_urls", url)
        print '[INOF] start_urls 加入: ' + url

if __name__ =="__main__":
    insert_start_url()