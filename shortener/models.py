import uuid

from django.db import models
from django.contrib.auth import get_user_model


class Link(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(unique=True, db_index=True, max_length=50)
    url = models.URLField(db_index=True)
    is_active = models.BooleanField(default=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(null=True, default=None)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='links')

    def __str__(self):
        return f"{self.key} for {self.url}"
