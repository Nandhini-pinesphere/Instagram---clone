from django.shortcuts import render ,get_object_or_404, redirect
from django.contrib.auth.models import User
from userauths.models import Profile
from django.core.paginator import Paginator
from django.urls import resolve
from post.models import Post,Follow ,Stream
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from userauths.forms import EditProfileForm ,UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login



# Create your views here.



def userProfile(request , username):
    user = get_object_or_404(User , username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts= profile.favourite.all()

    #Tracking profile stats
    post_count = Post.objects.filter(user=user).order_by('-posted').count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()


    # Follow status
    follow_status = Follow.objects.filter(following=user , follower=request.user).exists()

    #pagination
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)
    context = {
          'posts_paginator' : posts_paginator,
          'profile' : profile,
          'posts' : posts,
          'url_name' : url_name,
          'post_count': post_count,
          'following_count':following_count,
          'followers_count':followers_count,
          'follow_status': follow_status,

    }   
    return render(request, 'profile.html' , context)

def follow(request , username, option):
    user = request.user
    following = get_object_or_404(User , username=username)
    try:
        f,created = Follow.objects.get_or_create(follower=user , following=following)
        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following , user=user).all().delete()
        else:
            posts = Post.objects.filter(user=following)[:10]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post , user=user , date=post.posted , following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile' , args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile' , args=[username]))
    

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # Profile.get_or_create(user=request.user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hurray your account was created!!')

            # Automatically Log In The User
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],)
            login(request, new_user)
            #return redirect('editprofile')
            return redirect('/')  


    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'sign-up.html', context)

def editProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image') #this
            profile.first_name = form.cleaned_data.get('first_name')  
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.bio = form.cleaned_data.get('bio')
            #profile.url = form.cleaned_data.get('url')
            profile.save()
            return redirect('profile' , profile.user.username)
    else:
        form = EditProfileForm()
        
    context = {
        
          'form' : form,
          
     }  
    return render(request, 'edit-profile.html' , context) 




