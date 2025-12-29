from django.db import models
from cloudinary.models import CloudinaryField


class User_Data(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    first_name = models.CharField(max_length=100, default='')
    surname = models.CharField(max_length=100, default='')

    email = models.EmailField(unique=True)

    # ✅ Cloudinary fields
    profile_picture = CloudinaryField(
        'image',
        blank=True,
        null=True
    )

    cover_photo = CloudinaryField(
        'image',
        blank=True,
        null=True
    )

    bio = models.TextField(default='')
    work = models.CharField(max_length=255, default='')
    education = models.CharField(max_length=255, default='')
    location = models.CharField(max_length=255, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    user = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    content = models.TextField(blank=True)

    # ✅ Cloudinary image
    image = CloudinaryField(
        'image',
        blank=True,
        null=True
    )

    # ✅ Cloudinary video
    video = CloudinaryField(
        'video',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username}"


class Friend(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    )

    user = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    friend = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user} → {self.friend} ({self.status})"


class Like(models.Model):
    user = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


class Comment(models.Model):
    user = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField()

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class CommentLike(models.Model):
    user = models.ForeignKey(
        User_Data,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')