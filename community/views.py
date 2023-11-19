from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Topic, Comment, User
from .forms import PostForm, UserForm
import datetime

from django.contrib.auth import get_user_model
User = get_user_model()

def get_timesince(datetime_arg):
	delta = abs(datetime_arg - datetime.datetime.now())
	if hasattr(delta, 'days'):
		if delta.days > 365:
			timeoutput = f'{delta.days // 365} ýyl öň'
		elif delta.days >= 7 and delta.days <= 30:
			timeoutput = f'{delta.days // 7} hepde öň'
		elif delta.days > 30 and delta.days <= 365:
			timeoutput = f'{delta.days // 30} aý öň'
		else:
			timeoutput = f'{delta.days} gün öň'
	
	if timeoutput == '0 gün öň':
		if hasattr(delta, 'seconds'):
			if delta.seconds >= 60 and delta.seconds < 3600:
				timeoutput = f'{delta.seconds // 60} minut öň'
			elif delta.seconds >= 3600 and delta.seconds < 86400:
				timeoutput = f'{delta.seconds // 3600} sagat öň'
			else:
				timeoutput = f'{delta.seconds} sekund öň'
		else:
			timeoutput = '1 sekund öň'

	return timeoutput


def community(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = Post.objects.filter(
        Q(topic__name__icontains=q) |
        Q(title__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    post_count = Post.objects.all().count()
    comments = Comment.objects.filter(Q(post__topic__name__icontains=q))
    # https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
    paginator = Paginator(posts, 5)
    page = request.GET.get('page', 1)
    try:
        post_pagin = paginator.page(page)
    except PageNotAnInteger:
        post_pagin = paginator.page(1)
    except EmptyPage:
        post_pagin = paginator.page(paginator.num_pages)

    for post in post_pagin:
        post.created = get_timesince(post.created)
    comments_dub, i = [], 0
    for comment in comments:
        comments_dub.append(comment)
        i += 1
        if i == 5:
            break

    context = {'topics': topics, 'post_count': post_count, 'comments': comments_dub,'post_pagin':post_pagin}
    return render(request, 'community/community.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    comments = post.comment_set.all().order_by('-created')
    participants = post.participants.all()
    if request.method == 'POST':
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)

    post.created = get_timesince(post.created)
    context = {'post': post, 'comments': comments,
               'participants': participants}
    return render(request, 'community/post.html', context)


@login_required(login_url='login')
def createPost(request):
    form = PostForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        post = Post.objects.create(
            author=request.user,
            topic=topic,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
        )
        post.participants.add(request.user)
        return redirect('community')
    context = {'form': form, 'topics': topics}
    return render(request, 'community/post_form.html', context)


@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)
    topics = Topic.objects.all()
    if request.user != post.author:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        post.name = request.POST.get('name')
        post.topic = topic
        post.description = request.POST.get('description')
        post.save()
        return redirect('community')
    context = {'form': form, 'topics': topics, 'post': post}
    return render(request, 'community/post_form.html', context)


@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.user != post.author:
        return HttpResponse('You are not allowed here.')
    if request.method == 'POST':
        post.delete()
        return redirect('community')
    return render(request, 'community/delete.html', {'obj': post})


@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    if request.user != comment.user:
        return HttpResponse('You are not allowed here.')
    if request.method == 'POST':
        comment.delete()
        return redirect('community')
    return render(request, 'community/delete.html', {'obj': comment})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'community/topics.html', {'topics': topics})


def activityPage(request):
    comments = Comment.objects.all()
    return render(request, 'community/activity.html', {'comments': comments})


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.post_set.all()
    comments = user.comment_set.all()
    topics = Topic.objects.all()
    posts_all_count = Post.objects.all().count

    for post in posts:
        post.created = get_timesince(post.created)
    context = {'user': user, 'post_pagin': posts, 'comments': comments, 'topics': topics, 'post_count': posts_all_count}
    return render(request, 'community/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'community/update-user.html', {'form': form})