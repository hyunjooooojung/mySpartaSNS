import re
from django.shortcuts import render, redirect
from .models import UserModel
from django.http import HttpResponse
from django.contrib.auth import get_user_model # 사용자가 데이터베이스 안에 있는지 검사하는 함수
from django.contrib import auth
from django.contrib.auth.decorators import login_required


# Create your views here.
def sign_up_view(request):
    if request.method == 'GET':
        user = request.user.is_authenticated # 로그인 된 사용자가 요청하는지 검사
        if user: # 로그인이 되어있다면
            return redirect('/')
        else: # 로그인이 되어있지 않다면
            return render(request, 'user/signup.html')
    # if request.method == 'GET':  # GET메소드로 요청이 들어오는 경우
    #     return render(request, 'user/signup.html')
    #     # signup.html을 화면에 보여준다.

    elif request.method == 'POST': # POST메소드로 요청이 들어오는 경우
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        bio = request.POST.get('bio', '')

        if password != password2:
            # 비밀번호 두개가 일치하지 않으면 다시 signup.html화면을 보여준다.
            return render(request, 'user/signup.html', {'error' : '패스워드를 확인해주세요!'})
        else: # 비밀번호 두개가 같으면 아래 정보들을 저장해준다.
            if username == '' or password == '':
                return render(request, 'user/signup.html', {'error' : '사용자이름과 비밀번호는 필수값입니다!'})

            # get_user_model() 함수를 사용해서 데이터베이스 안에 uesername을 가진 사람이 있는지 확인
            exist_user = get_user_model().objects.filter(username=username)
            
            if exist_user:  # 사용자가 이미 존재하기 때문에 저장하지 않고 회원가입페이지로 다시 돌아감
                return render(request, 'user/signup.html', {'error' : '사용자가 이미 존재합니다!'})
            else:
                UserModel.objects.create_user(username=username, password=password, bio=bio)
                return redirect('/sign-in') # 비밀번호가 일치하면 로그인 페이지로 넘어간다


def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # 인증기능모듈 : 암호화된 비밀번호와 입력된 비밀번호와 일치하는지, 사용자와 맞는지까지 인증해줌
        me = auth.authenticate(request, username=username, password=password) 
        
        if me is not None: # 사용자가 비어있지 않다면
            auth.login(request, me) # 사용자가 있으면 me에 나의 정보를 입력한다 
            return redirect('/')
            # return HttpResponse(f"로그인 성공 : {me.username}") # 로그인에 성공하면 새로운 페이지에 화면 띄워준다.
        else: # 패스워드가 같지 않으면 다시 로그인하기 위해서 로그인 페이지로 redirect
            return render(request, 'user/signin.html', {'error': 'username 혹은 password를 확인해주세요! '})  # 로그인 실패
    elif request.method == 'GET':
        user = request.user.is_authenticated  # 사용자가 로그인 되어 있는지 검사 / 로그인의 여부만 검증 해 주는 기능
        if user:  # 로그인이 되어 있다면
            return redirect('/')
        else:  # 로그인이 되어 있지 않다면
            return render(request, 'user/signin.html')

@login_required # 로그인 한 사용자만 접근 할 수 있게 해 주는 기능 / 로그인을 하지 않으면 접근 안됨
def logout(request):
    auth.logout(request) # 인증 되어있는 정보를 없애기
    return redirect("/")


@login_required
def user_view(request):
    if request.method == 'GET':
        # 사용자를 불러오기, exclude와 request.user.username 를 사용해서 '로그인 한 사용자'를 제외하기
        user_list = UserModel.objects.all().exclude(username=request.user.username)
        return render(request, 'user/user_list.html', {'user_list': user_list})


@login_required
def user_follow(request, id):
    # 로그인한 사람
    me = request.user
    # 내가 방금 누른 사람 / 로그인한 사람이 팔로우할 사람
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all(): # 사용자모델에 내가 들어가 있지 않으면 팔로우
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/user')