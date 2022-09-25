# tweet/views.py
from django.shortcuts import render, redirect
from .models import TweetModel # 글쓰기 모델
from .models import TweetComment # 댓글쓰기 모델
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView


# Create your views here.
def home(request):
    user = request.user.is_authenticated  # 사용자가 인증을 받았는지 (로그인이 되어있는지)
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')


def tweet(request):
    if request.method == 'GET':  # 요청하는 방식이 GET 방식인지 확인하기
        user = request.user.is_authenticated  # 사용자가 로그인이 되어 있는지 확인하기
        if user:  #로그인이 된 상태에서 게시글을 읽어와야 하니까, 로그인 사용자를 검증 한 후에 TweetModel을 불러 준다.
            all_tweet = TweetModel.objects.all().order_by('-created_at') # TweetModel을 created_at의 역순으로 불러오는 코드
            return render(request, 'tweet/home.html', {'tweet': all_tweet}) # tweet/home.html을 화면에 띄우면서 {'tweet':all_tweet} 라는 데이터를 화면에 전달.
        else:  # 로그인이 되어 있지 않다면 
            return redirect('/sign-in')
    
    elif request.method == 'POST':  # 요청 방식이 POST 일때
        user = request.user  # 현재 로그인 한 사용자를 불러오기
        content = request.POST.get('my-content', '') # 글 작성이 되지 않았으면 빈칸으로
        tags = request.POST.get('tag', '').split(',')

        if content == '': #글이 빈칸이면 기존 tweet과 에러를 같이 출력
            all_tweet = TweetModel.objects.all().order_by('-created_at') # TweetModel을 created_at의 역순으로 불러오는 코드
            return render(request, 'tweet/home.html', {'error': '글은 공백일 수 없습니다!'}, {'tweet': all_tweet})

        else:
            my_tweet = TweetModel.objects.create(author=user, content=content) # 글 저장을 한번에!
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save() # my_tweet의 데이터를 가져오고 저장
            return redirect('/tweet')


def delete_tweet(request, id): # id는 게시글 고유의 id로써 게시글을 구분 하는 데에 사용 할 변수
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')


# homework 
@login_required
def detail_tweet(request, id): # tweet 상세보기 기능
    my_tweet = TweetModel.objects.get(id=id)
    tweet_comment = TweetComment.objects.filter(tweet_id=id).order_by('-created_at')
    return render(request,'tweet/tweet_detail.html',{'tweet':my_tweet,'comment':tweet_comment})


@login_required
def write_comment(request, id): # 댓글달기
    if request.method == 'POST':
        comment = request.POST.get("comment","")
        current_tweet = TweetModel.objects.get(id=id)

        TC = TweetComment()
        TC.comment = comment
        TC.author = request.user
        TC.tweet = current_tweet
        TC.save()

        return redirect('/tweet/'+str(id))

@login_required
def delete_comment(request, id): # 댓글삭제
    comment = TweetComment.objects.get(id=id)
    current_tweet = comment.tweet.id
    comment.delete()
    return redirect('/tweet/'+str(current_tweet))



class TagCloudTV(TemplateView): # 태그들을 모아놓는 태그클라우드를 만듦
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView): # 태그들을 모아서 화면에 전달하는 역할
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context
