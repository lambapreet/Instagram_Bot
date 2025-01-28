from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from post.models import Post
from notification.models import Notification

# Comment model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")  # Fixed `related_name`
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)

# Signal handler for creating notifications on comment creation
@receiver(post_save, sender=Comment)
def user_comment_post(sender, instance, created, **kwargs):
    if created:  # Ensure this only runs on new comment creation
        comment = instance
        post = comment.post
        text_preview = comment.body[:90]
        sender_user = comment.user
        notify = Notification(
            post=post,
            sender=sender_user,
            user=post.user,
            text_preview=text_preview,
            notification_types=2,
        )
        notify.save()

# Signal handler for deleting notifications on comment deletion
@receiver(post_delete, sender=Comment)
def user_del_comment_post(sender, instance, **kwargs):
    comment = instance
    post = comment.post
    sender_user = comment.user
    Notification.objects.filter(
        post=post, sender=sender_user, user=post.user, notification_types=2
    ).delete()
