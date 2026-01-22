# accounts/models.py
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_relations")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_relations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow")
        ]

    def __str__(self):
        return f"{self.follower} -> {self.following}"
