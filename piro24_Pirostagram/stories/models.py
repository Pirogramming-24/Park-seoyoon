# stories/models.py
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def default_expires_at():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    # ✅ 유저당 스토리 1개 강제
    author = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="story",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ 활성/만료 기준
    expires_at = models.DateTimeField(default=default_expires_at)

    def refresh_expiry(self):
        self.expires_at = default_expires_at()
        self.save(update_fields=["expires_at", "updated_at"])

    def __str__(self):
        return f"Story({self.author.username})"


class StoryItem(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="items",
    )
    image = models.ImageField(upload_to="stories/%Y/%m/%d/")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"StoryItem(story={self.story_id}, order={self.order})"
