import csv
import hashlib
import io
import json
import secrets

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import MatchRoom
from .owner import attach_owner_cookie, is_room_owner, resolve_owner_key, set_owner_cookie


def parse_csv_file(file_obj, salt: str) -> dict[str, str]:
    """Return mapping of record_hash -> original identifier (first column)."""
    decoded_file = file_obj.read().decode("utf-8").splitlines()
    reader = csv.reader(decoded_file)
    next(reader, None)

    lookup: dict[str, str] = {}
    for row in reader:
        if not row:
            continue
        original_val = str(row[0]).strip()
        clean_val = original_val.lower()
        if clean_val:
            salted = f"{clean_val}{salt}"
            hashed = hashlib.sha256(salted.encode("utf-8")).hexdigest()
            lookup[hashed] = original_val
    return lookup


def build_matches_csv(party_a_lookup: dict[str, str], party_b_lookup: dict[str, str]) -> tuple[str, int]:
    common_hashes = set(party_a_lookup) & set(party_b_lookup)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["party_a", "party_b"])
    for record_hash in sorted(common_hashes):
        writer.writerow([party_a_lookup[record_hash], party_b_lookup[record_hash]])
    return output.getvalue(), len(common_hashes)


def party_b_invite_url(request: HttpRequest, room: MatchRoom) -> str:
    path = reverse(
        "party_b_upload",
        kwargs={"room_id": room.id, "invite_token": room.invite_token},
    )
    return request.build_absolute_uri(path)


def complete_match(room: MatchRoom, party_b_lookup: dict[str, str]) -> None:
    party_a_lookup = json.loads(room.party_a_lookup)
    matched_csv, match_count = build_matches_csv(party_a_lookup, party_b_lookup)

    room.matched_results = matched_csv
    room.match_count = match_count
    room.is_completed = True
    room.party_a_hashes = ""
    room.party_a_lookup = ""
    room.save()


def get_owned_room(request: HttpRequest, room_id) -> MatchRoom | HttpResponseForbidden:
    room = get_object_or_404(MatchRoom, id=room_id)
    if not is_room_owner(request, room):
        return HttpResponseForbidden("You do not have access to this room.")
    return room


def home(request: HttpRequest) -> HttpResponse:
    owner_key, is_new_owner = resolve_owner_key(request)

    if request.method == "POST":
        name = request.POST.get("name", "").strip() or "Untitled Room"
        salt = secrets.token_hex(32)
        room = MatchRoom.objects.create(name=name, secret_salt=salt, owner_key=owner_key)
        response = redirect("match_room", room_id=room.id)
        if is_new_owner:
            set_owner_cookie(response, owner_key)
        return response

    rooms = MatchRoom.objects.filter(owner_key=owner_key).order_by("-id")
    response = render(request, "home.html", {"rooms": rooms})
    return attach_owner_cookie(request, response)


def upload_and_match_view(request: HttpRequest, room_id) -> HttpResponse:
    room_or_response = get_owned_room(request, room_id)
    if isinstance(room_or_response, HttpResponseForbidden):
        return room_or_response
    room = room_or_response
    context: dict = {"room": room}

    if room.is_completed:
        return render(request, "match_room.html", context)

    if request.method == "POST" and request.FILES.get("csv_file"):
        if room.is_party_a_uploaded:
            return HttpResponseBadRequest("Party A has already uploaded. Share the invite link with Party B.")

        current_lookup = parse_csv_file(request.FILES["csv_file"], room.secret_salt)
        room.party_a_hashes = ",".join(current_lookup)
        room.party_a_lookup = json.dumps(current_lookup)
        room.is_party_a_uploaded = True
        room.save()

        context["message"] = "Your file was uploaded successfully! Send the link below to Party B."
        context["party_b_invite_url"] = party_b_invite_url(request, room)
        return render(request, "match_room.html", context)

    if room.is_party_a_uploaded:
        context["party_b_invite_url"] = party_b_invite_url(request, room)

    return render(request, "match_room.html", context)


def room_status(request: HttpRequest, room_id) -> HttpResponse:
    room_or_response = get_owned_room(request, room_id)
    if isinstance(room_or_response, HttpResponseForbidden):
        return room_or_response
    room = room_or_response
    return JsonResponse(
        {
            "is_completed": room.is_completed,
            "is_party_a_uploaded": room.is_party_a_uploaded,
            "match_count": room.match_count,
        }
    )


def party_b_upload_view(request: HttpRequest, room_id, invite_token: str) -> HttpResponse:
    room = get_object_or_404(MatchRoom, id=room_id, invite_token=invite_token)
    context: dict = {"room": room}

    if room.is_completed:
        return render(request, "party_b_upload.html", context)

    if not room.is_party_a_uploaded:
        context["error"] = "Party A has not uploaded their file yet. Please try again later."
        return render(request, "party_b_upload.html", context)

    if request.method == "POST" and request.FILES.get("csv_file"):
        current_lookup = parse_csv_file(request.FILES["csv_file"], room.secret_salt)
        complete_match(room, current_lookup)
        context["message"] = "Match calculation complete!"
        return render(request, "party_b_upload.html", context)

    return render(request, "party_b_upload.html", context)


def build_download_response(room: MatchRoom) -> HttpResponse:
    filename = f"{room.name.replace(' ', '_')}_matches.csv"
    response = HttpResponse(room.matched_results, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def download_results(request: HttpRequest, room_id) -> HttpResponse:
    room = get_object_or_404(MatchRoom, id=room_id)
    if not room.is_completed or not room.matched_results:
        return HttpResponseBadRequest("No results available.")

    if not is_room_owner(request, room):
        return HttpResponseForbidden("You do not have access to this room.")

    return build_download_response(room)


def download_results_party_b(request: HttpRequest, room_id, invite_token: str) -> HttpResponse:
    room = get_object_or_404(MatchRoom, id=room_id, invite_token=invite_token)
    if not room.is_completed or not room.matched_results:
        return HttpResponseBadRequest("No results available.")

    return build_download_response(room)
