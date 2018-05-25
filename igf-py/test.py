import redis

r = redis.Redis(
    host='127.0.0.1')
#    port=port, 
#    password='password')
#r.set('foo', 'bar')
#print r.get('foo0')
value = r.smembers('shortcodes')
print(value)
