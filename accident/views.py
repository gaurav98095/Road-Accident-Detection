from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
import operator
from django.urls import reverse_lazy
from django.contrib.staticfiles.views import serve

from django.db.models import Q
import os
import tensorflow as tf
from PIL import Image
import numpy as np
from tensorflow.keras.preprocessing import image


def predictModel(request):
    server_url = os.getcwd()

    for x in Post.objects.all(): 
        link_from_query = str(x.file)

        if link_from_query[-3:]=='jpg' and x.predicted ==False:
                
            link_from_query = '\\'+'media\\' + link_from_query
            link_from_query= link_from_query.replace("/","\\")
            link = server_url+str(link_from_query)
            model = tf.keras.models.load_model('model.h5')

            
            img = image.load_img(link, target_size = (180,180))
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis = 0)
            print(model.predict(img))
            if model.predict(img)[0][1]<0.5:
                x.isAccident = True
            x.predicted = True
            x.save()


    return home(request)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'accident/home.html', context)

def search(request):
    template='accident/home.html'

    query=request.GET.get('q')

    result=Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(content__icontains=query))
    paginate_by=2
    context={ 'posts':result }
    return render(request,template,context)
   


def getfile(request):
   return serve(request, 'File')


class PostListView(ListView):
    model = Post
    template_name = 'accident/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 2


class UserPostListView(ListView):
    model = Post
    template_name = 'accident/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'accident/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'accident/post_form.html'
    fields = ['title', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'accident/post_form.html'
    fields = ['title', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'accident/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'accident/about.html', {'title': 'About'})
