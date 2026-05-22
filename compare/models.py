import secrets
import uuid

from django.db import models


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


class MatchRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    secret_salt = models.CharField(max_length=64, default="mvp_default_salt_123")
    invite_token = models.CharField(max_length=64, default=generate_invite_token, editable=False)
    party_a_hashes = models.TextField(blank=True, default="")
    party_a_lookup = models.TextField(blank=True, default="")
    matched_results = models.TextField(blank=True, default="")
    match_count = models.PositiveIntegerField(default=0)
    is_party_a_uploaded = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
