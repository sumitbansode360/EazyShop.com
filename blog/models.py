from django.db import models
# Create your models here.

class BlogPost(models.Model):
    blog_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=200,default='admin')
    title = models.CharField(max_length=150,unique=True)
    h0 = models.CharField(max_length=150)
    content_h0 = models.CharField(max_length=5000)
    h1 = models.CharField(max_length=150)
    content_h1 = models.CharField(max_length=5000)
    h2 = models.CharField(max_length=150)
    content_h2 = models.CharField(max_length=5000)
    pub_date = models.DateField()
    thumbnail = models.ImageField( upload_to="blog/blog_img")

    def __str__(self) -> str:
        return self.title