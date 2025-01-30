from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import CustomUser
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
import re
import random
# Create your views here.
def generate_session_token(length=10):
    return ''.join(random.SystemRandom().choice([chr(i) for i in range(97,123)]+[str(i) for i in range(10)]) for _ in range(length))

@csrf_exempt
def signing(request):
    if not request.method=='POST':
        return JsonResponse({'error':'Send a post request with valid parameter only'})

    username = request.POST['email']
    password = request.POST['password']

    if not re.match('^[\w\.-]+@[\w\.-]+$', username):
        return JsonResponse({'error':'Enter a valid email'})
    if len(password)<3:
        return JsonResponse({'error':'Password needs to be atleast 3 char long'})
    
    UserModel=get_user_model()
    try:
        user=UserModel.objects.get(email=username)
        if user.check_password(password):
            usr_dict=UserModel.objects.filter(email=username).values().first()
            usr_dict.pop('password')

            if user.session_token != "0":
                user.session_token="0"
                user.save()
                return JsonResponse({'error':'Previous session exists!'})
            
            token= generate_session_token()
            user.session_token=token
            user.save()
            login(request, user)
            return JsonResponse({'token':token, 'user':usr_dict})
        else:
            return JsonResponse({'error':'Invalid password'})
    except UserModel.DoesNotExist:
        return JsonResponse({'error':'Invalid email'})