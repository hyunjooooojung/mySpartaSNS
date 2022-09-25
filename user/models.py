#user/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.
class UserModel(AbstractUser): # 장고가 제공하는 클래스를 사용할건데 거기에 뭔가 수정할 것이다.(상속해서))
    class Meta:
        db_table = "my_user"  # 나의 db테이블 이름

    # 장고가 제공하는 AbstractUser 클래스에 bio만 추가한 클래스 생성
    bio = models.CharField(max_length=256, default='')
    # 장고에서 사용할 유저모델은 settings.py에 AUTH_USER_MODEL로 선언되어있음.
    # UserModel에 ManyToManyField를 추가했음.
    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followee')
    