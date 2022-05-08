from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

# Middleware for frontend React
# SO fronted request api methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-12871.c250.eu-central-1-1.ec2.cloud.redislabs.com",
    port=12871,
    password="63T5YKjGvnCVuJ5ck5Rp1mejFyIGQ2lu",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    user_id:str
    name: str
    price: float
    fee: float
    total: float
    quantity: int
    trustPrice: int
    status: str  # pending/completed/refunded


    class Meta:
        database = redis
        

@app.get('/orders')
def all():
    return [pk for pk in Order.all_pks()]

@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):  # id and quantity
    body = await request.json()
    body2 = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])  # Communicate get request from other place
    req2 = requests.get('http://localhost:8004/users/%s' % body['user_id'])
    
    product = req.json()
    product2 = req2.json()

    order = Order(
        name=product['name'],
        product_id=body['id'],
        price=product['price'],
        fee=product['price'] * 0.2,
        quantity=body['quantity'],
        total=1.2 * product['price'],
        trustPrice=product['trustPrice'],
        status='pending',
        user_id=body2['user_id'],
        trustIndex=product2['trustIndex']
    )
    
    order.save()

    background_tasks.add_task(order_completed, order)

    return order


# Executing in background after 5sec
def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    # Redis Stream, *->id of event auto generate id
    redis.xadd('order_completed', order.dict(), '*')
