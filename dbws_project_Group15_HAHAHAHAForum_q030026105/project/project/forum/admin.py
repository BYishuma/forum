from django.contrib import admin
from .models import LoginUser, Basic_Information, Column, Post, Comment,  Notice
# Register your models here.
admin.site.register(LoginUser)
admin.site.register(Basic_Information)
admin.site.register(Column)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Notice)
