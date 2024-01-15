from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import signals
from django.urls import reverse_lazy


# Create your models here.
class LoginUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    privilege = models.CharField(max_length=200, default=0, verbose_name=u'privilege')

    class Meta:
        db_table = 'LoginUser'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_username()

    def get_first_name(self):
        text = str(self.username)[0:1]
        if text.isalpha():
            return text.lower()
        else:
            return 'u'


class Basic_Information(models.Model):
    uid = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default='')
    age = models.PositiveIntegerField(verbose_name='Age')
    GENDER_CHOICE = ((u'm', u'Male'), (u'f', u'Female'),)
    gender = models.CharField(verbose_name='Gender', max_length=2, choices=GENDER_CHOICE)
    country = models.CharField(verbose_name='Country', max_length=50)


class Column(models.Model):
    name = models.CharField(verbose_name='Column Name', max_length=30)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='column_manager', on_delete=models.PROTECT)  # 版主
    description = models.TextField(verbose_name='Column Introduction')
    post_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'Column'
        ordering = ['-post_number']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('single_category', kwargs={"column_pk": self.pk})

    def get_number(self):
        class_map = {
            "affection": 1,
            "achievement": 2,
            "bonding": 3,
            "enjoy_the_moment": 4,
            "leisure": 5,
            "nature": 6,
            "exercise": 7
        }
        text = str(self.name)
        text = class_map[text]
        return text


class Post(models.Model):
    title = models.CharField(verbose_name='Title', max_length=64)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='post_author', on_delete=models.PROTECT)
    column = models.ForeignKey(Column, verbose_name='Column', on_delete=models.CASCADE, )
    content = models.CharField(verbose_name='Content', max_length=3000)
    photo = models.CharField(verbose_name='Photo', max_length=128, null=True)
    created_at = models.DateField(verbose_name='Created At', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated At', auto_now=True, null=True)
    comment_num = models.IntegerField(default=0)  # number of comments

    class Meta:
        db_table = 'post'
        ordering = ['-created_at']
        verbose_name_plural = 'post'

    def get_absolute_url(self):
        return reverse_lazy('single_topic', kwargs={"post_pk": self.pk})

    def get_first_name(self):
        text = str(self.author)[0:1]
        if text.isalpha():
            return text.lower()
        else:
            return 'u'

    def get_column(self):
        class_map = {
            "affection": 1,
            "achievement": 2,
            "bonding": 3,
            "enjoy_the_moment": 4,
            "leisure": 5,
            "nature": 6,
            "exercise": 7
        }
        text = str(self.column)
        text = class_map[text]
        return text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comment_parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='childcomment', on_delete=models.PROTECT)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comment'
        ordering = ['-created_at']
        verbose_name_plural = 'comment'

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse_lazy('post_detail', kwargs={"post_pk": self.post.pk})

    def get_user(self):
        return self.author


class Notice(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notice_sender', on_delete=models.PROTECT)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notice_receiver', on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    event = GenericForeignKey('content_type', 'object_id')

    type = models.IntegerField()  # type 0:comment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notice'
        ordering = ['-created_at']


def post_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(
            entity.updated_at)[:19]:  # No editing for post posts released for the first time
        column = entity.column
        column.post_number += 1
        column.save()


def post_delete(sender, instance, signal, *args, **kwargs):  # delete post, number of posts -1
    entity = instance
    column = entity.column
    column.post_number -= 1
    column.save()


def comment_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]:
        if entity.author != entity.post.author:  # No notice for comment yourself
            event = Notice(
                sender=entity.author,
                receiver=entity.post.author,
                event=entity,
                type=0)
            event.save()
        if entity.comment_parent is not None:  # notice for comment others
            if entity.author.id != entity.comment_parent.author.id:  # No notice for comment yourself
                event = Notice(
                    sender=entity.author,
                    receiver=entity.comment_parent.author,
                    event=entity,
                    type=0)
                event.save()


def application_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]:
        event = Notice(
            sender=entity.sender,
            receiver=entity.receiver,
            event=entity,
            type=1)
        event.save()


# The message response function is registered
signals.post_save.connect(comment_save, sender=Comment)
signals.post_save.connect(post_save, sender=Post)
signals.post_delete.connect(post_delete, sender=Post)
