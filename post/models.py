from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
import uuid

# Assuming you have a Notification model in notification.models
from notification.models import Notification


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True, default=uuid.uuid1)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="Picture")
    caption = models.CharField(max_length=10000, verbose_name="Caption")
    posted = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("post-details", args=[str(self.id)])


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")


@receiver(post_save, sender=Likes)
def user_liked_post(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        sender_user = instance.user
        notify = Notification(post=post, sender=sender_user, user=post.user)
        notify.save()


@receiver(post_delete, sender=Likes)
def user_unliked_post(sender, instance, **kwargs):
    post = instance.post
    sender_user = instance.user
    notify = Notification.objects.filter(post=post, sender=sender_user, notification_types=1)
    notify.delete()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')


@receiver(post_save, sender=Follow)
def user_follow(sender, instance, created, **kwargs):
    if created:
        sender_user = instance.follower
        following = instance.following
        notify = Notification(sender=sender_user, user=following, notification_types=3)
        notify.save()


@receiver(post_delete, sender=Follow)
def user_unfollow(sender, instance, **kwargs):
    sender_user = instance.follower
    following = instance.following
    notify = Notification.objects.filter(sender=sender_user, user=following, notification_types=3)
    notify.delete()


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()


@receiver(post_save, sender=Post)
def add_post_to_stream(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        followers = Follow.objects.filter(following=user)

        for follower in followers:
            stream = Stream(post=instance, user=follower.follower, date=instance.posted, following=user)
            stream.save()
