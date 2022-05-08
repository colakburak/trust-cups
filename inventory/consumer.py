import sys,time
from main import redis, Product

#sys.path.insert(1, '/home/barak/craftHack/user')
from main1 import User


key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exist!')

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)  # '>' -> get all the events

        if results != []:
            for result in results:
                obj = result[1][0][1]
                try:
                    product = Product.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                    print('Product quantity -')

                    user = User.get(obj['user_id'])
                    user.trustIndex = user.trustIndex + (0.001 * int(obj['total']))
                    print('Trust index ++')
                    user.save()

                except:
                    redis.xadd('refund_order', obj, '*')


    except Exception as e:
        print(str(e))

    time.sleep(1)  # Every second consume message
