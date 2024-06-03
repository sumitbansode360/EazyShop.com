from django.shortcuts import render
from .models import *
# Create your views here.

def index(request):
    blogs = BlogPost.objects.all()
    context = {'blogs':blogs}
    return render(request,'blog/index.html',context)

def blogpost(request,id):
    post = BlogPost.objects.filter(blog_id=id)[0]
    context = {'post':post}
    return render(request,"blog/blogpost.html",context)