import logging
from django.db.models import Q
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.hashers import make_password
from forum.form import PostForm, LoginUserForm
from django.core.cache import cache
from .form import LoginUserForm
from .models import LoginUser, Basic_Information, Column, Post, Comment, Notice
from notifications.signals import notify

logger = logging.getLogger(__name__)
PAGE_NUM = 50


# Create your views here.


def get_forum_info():
    post_number = Post.objects.count()
    account_number = LoginUser.objects.count()

    info = {
        "post_number": post_number,
        "account_number": account_number,
    }
    return info


def userlogin(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['password']
        next = request.POST['next']
        print(username)
        print(password)

        user = auth.authenticate(username=username, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            user.save()
            return HttpResponseRedirect(next)
        else:
            return HttpResponse(" Failed to login ")


    else:
        next = request.GET.get('next', None)
        if next is None:
            next = reverse_lazy('index')
        return render(request, 'page-login.html', {'next': next})


def userlogout(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))


class IndexView(ListView):
    """Home page"""
    model = Post
    queryset = Post.objects.all()
    template_name = 'index.html'
    context_object_name = 'post_list'

    paginate_by = 15

    def get_context_data(self, **kwargs):
        kwargs['foruminfo'] = get_forum_info()
        return super(IndexView, self).get_context_data(**kwargs)


def get_queryset(self):
    user_posts = Post.objects.filter(author=self.request.user)
    return user_posts


def singletopic(request, post_pk):
    post_pk = int(post_pk)
    post = Post.objects.get(pk=post_pk)
    comment_list = post.comment_set.all()
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    title = post.title
    visited_ips = cache.get(title, [])

    if ip not in visited_ips:
        post.save()
        visited_ips.append(ip)
    cache.set(title, visited_ips, 15 * 60)
    return render(request, 'page-single-topic.html', {'post': post, 'comment_list': comment_list})


def userregister(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        # password_confirm = request.POST.get("password_confirm", "")
        email = request.POST.get("email", "")
        gender = request.POST.get("gender", "")
        age = request.POST.get("age", "")
        country = request.POST.get("country", "")

        form = LoginUserForm(request.POST)
        user = LoginUser(username=username, password=password, email=email)
        user.password = make_password(password)
        user.check_password(password)
        user.save()

        return render(request, 'signupsuccess.html')

        errors = []
        if form.is_valid():
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            new_user = form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
        else:
            for k, v in form.errors.items():
                errors.append(v.as_text())
            return HttpResponse(errors)

    else:
        return render(request, 'page-signup.html')


@login_required(login_url=reverse_lazy('user_login'))
def PostCreate(request):
    if request.method == 'POST':
        title = request.POST.get("title")
        content = request.POST.get("message")

        author = LoginUser.objects.get(username=request.user)
        new_post = Post(title=title, author=author, content=content, column_id=request.POST.get("form-control"))
        new_post.save()

        return render(request, 'index.html')
    else:
        return render(request, 'page-create-topic.html')


@login_required(login_url=reverse_lazy('user_login'))
def makecomment(request):
    if request.method == 'POST':
        comment = request.POST.get("message", "")
        post_id = request.POST.get("post_id", "")
        comment_id = request.POST.get("comment_id", "")

        user = LoginUser.objects.get(username=request.user)
        p = Post.objects.get(pk=int(post_id))
        author = LoginUser.objects.get(id=p.author_id)
        p.comment_num += 1

        if comment_id:
            p_comment = Comment.objects.get(pk=comment_id)
            c = Comment(
                post=p, author=user, comment_parent=p_comment, content=comment)
            c.save()
        else:
            c = Comment(post=p, author=user, content=comment)
            c.save()
        p.save()
        author.save()

        # send message
        url = p.get_absolute_url()
        if comment_id:
            recipient = p_comment.get_user()
            notify.send(sender=user, recipient=recipient, verb='commented on your', url=url)
        else:
            recipient = p.author
            notify.send(sender=user, recipient=recipient, verb='Reply to you', url=url)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def columnall(request):
    column_list = Column.objects.all()
    return render(request, 'page-categories.html', {'column_list': column_list})


def columndetail(request, column_pk):
    column_pk = int(column_pk)
    column = Column.objects.get(pk=column_pk)
    post_list = column.post_set.all()
    paginator = Paginator(post_list, 15)
    page = request.GET.get('page', 1)
    current_page = int(page)
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except (EmptyPage, InvalidPage):
        post_list = paginator.page(paginator.num_pages)

    return render(request, 'page-categories-single.html', {
        'column': column,
        'post_list': post_list,
    })




def search(request):
    search_word = request.GET.get('wd', '').strip()
    condition = None
    paginate_by = 15

    for word in search_word.split('|'):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)
    search_content = []
    if condition is not None:
        search_content = Post.objects.filter(condition)
    content = {}
    content['search_word'] = search_word
    content['search_content'] = search_content
    content['search_content_number'] = search_content.count()

    return render(request, 'search-result.html', content)


class UserPostView(ListView):
    """User page"""
    template_name = 'page-single_threads.html'
    context_object_name = 'user_posts'
    paginate_by = PAGE_NUM

    def get_queryset(self):
        user_posts = Post.objects.filter(author=self.request.user)
        return user_posts


def visualized(request):
    return render(request, 'visualization.html')


