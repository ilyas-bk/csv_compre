from django.contrib import admin

from .models import MatchRoom


@admin.register(MatchRoom)
class MatchRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "is_party_a_uploaded", "is_completed")
    readonly_fields = ("id", "invite_token", "party_a_hashes", "party_a_lookup", "matched_results", "match_count")
