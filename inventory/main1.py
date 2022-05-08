from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

from starlette.requests import Request

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


class User(HashModel):
    userName: str
    name: str
    email: str
    trustIndex: float
    trustPoint: int
    

    class Meta:
        database = redis
    
@app.get('/users')
def all():
    return [format(pk) for pk in User.all_pks()]
        
        
@app.get('/users/{pk}')
def get(pk: str):
    return User.get(pk)


def format(pk: str):
    user = User.get(pk)
    return {
        'user_id': user.pk,
        'userName': user.userName,
        'name': user.name,
        'email': user.email,
        'trustIndex': user.trustIndex,
        'trustPoint': user.trustPoint,
    }


@app.post('/users')
async def create(request: Request):
    
    
    body = await request.json()
    
    user = User(
        userName=body['userName'],
        name=body['name'],
        email=body['email'],
        trustIndex=body['trustIndex'],
        trustPoint= int((3/7) * body['trustIndex'])
    )
    return user.save()

@app.delete('/users/{pk}')
def delete(pk: str):
    return User.delete(pk)
