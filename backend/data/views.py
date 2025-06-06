from data.models import *
from django.http import JsonResponse
from data.services import *
from data.serializers import *
import logging
import json
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import sys
from django.utils import translation
from django.conf import settings
from .forms import LanguagePreferenceForm
from django.shortcuts import render
from django.utils.translation import gettext as _
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

 
from rich import print

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    logger.info(f"[DATA_VIEWS][GET_USER_DATA]Request: {request.user.username}")
    
    profileID = request.GET.get("userID")
    friendshipID = None
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user
        btnType = _("Edit profile")
        actionType = "edit"
    else:
        user = CustomUser.objects.filter(id = profileID).first()
        friendship = get_frienship(profileID, request.user.id)
        if friendship:
            friendshipID =  friendship.id
            if friendship.status == "approved":
                btnType = _("Delete friend")
                actionType = "delete"
            elif friendship.status == "pending" and friendship.sender == request.user:
                btnType = _("Friend request sent")
                actionType = "request"
            else:
                btnType = _("Accept request")
                actionType = "accept"
        else:
            btnType = _("Add friend")
            actionType = "add"
        
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    matches_played = get_matches_count(user.id)
    matches_won = get_win_cout(user.id)
    matches_lost = matches_played - matches_won
    
    user_data = {
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar.url if user.avatar else None,
        "btnType": btnType,
        "actionType": actionType,
        "matches_played": matches_played,
        "matches_won": matches_won,
        "matches_lost": matches_lost,
        "user_id": user.id,
        "friendshipID": friendshipID
    }
    return JsonResponse(user_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_matches(request):
    logger.info(f"[DATA_VIEWS][GET_USER_MATCHES]Request {request.user.username}")
    
    profileID = request.GET.get("userID")
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user 
    else:
        user = CustomUser.objects.filter(id = profileID).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    matches = get_user_3_matches(user.id)
    match_data = {
        "matches": list(MatchSummarySerializer(matches, many=True, context={"user": user}).data),
    }

    return JsonResponse(match_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_user_matches(request):
    logging.info(f"[DATA_VIEWS][GET_USER_MATCHES]request: {request.user.username}")
    profileID = request.GET.get("userID")
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user 
    else:
        user = CustomUser.objects.filter(id = profileID).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    matches = get_all_matches(user.id)
    match_data = {
        "matches": list(MatchSummarySerializer(matches, many=True, context={"user": user}).data),
    }
    return JsonResponse(match_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_tournaments(request):
    logging.info(f"[DATA_VIEWS][GET_USER_TOURNAMENTS]request: {request.user.username}")
    profileID = request.GET.get("userID")
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user
    else:
        user = CustomUser.objects.filter(id=profileID).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    tournaments = get_user_3_tournaments(user.id)
    tournaments_data = {
        "tournaments": TournamentSummarySerializer(tournaments, many=True, context={"user": user}).data,
    }
    return JsonResponse(tournaments_data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_user_tournaments(request):
    logging.info(f"[DATA_VIEWS][GET_ALL_USER_TOURNAMENTS]request: {request.user.username}")
    profileID = request.GET.get("userID")
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user
    else:
        user = CustomUser.objects.filter(id=profileID).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    tournaments = get_all_tournaments(user.id)
    tournaments_data = {
        "tournaments": TournamentSummarySerializer(tournaments, many=True, context={"user": user}).data,
    }
    return JsonResponse(tournaments_data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_user_data(request):
    logging.info(f"[DATA_VIEWS][EDIT_USER_DATA]request: {request.user.username}")

    newUsername = request.POST.get('newUsername')
    newMail = request.POST.get('newMail')
    newAvatar = request.FILES.get('newAvatar')
    preferred_language = request.POST.get('preferred_language')

    user = request.user
    
    try:
        # Check if username or email already exists
        if newUsername and CustomUser.objects.exclude(id=user.id).filter(username=newUsername).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)

        if newMail and CustomUser.objects.exclude(id=user.id).filter(email=newMail).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        if newUsername:
            user.username = newUsername
        if newMail:
            user.email = newMail
        if newAvatar:
            user.avatar = newAvatar
        if preferred_language:
            user.preferred_language = preferred_language
            translation.activate(preferred_language)
            request.session[settings.LANGUAGE_COOKIE_NAME] = preferred_language

        user.save()
        
        updated_user_data = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar.url if user.avatar else None,
            "preferred_language": user.preferred_language,
        }
                
        return JsonResponse({"message": "Successfully edited", "user_data": updated_user_data}, status=200)
    
    except Exception as e:
        logger.error(f"Error edting user data: {e}")
        return JsonResponse({"error": "Oopsie, something went wrong"}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_friends(request):
    logging.info(f"[DATA_VIEWS][GET_USER_FRIENDS]request: {request.user.username}")
    user = request.user
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    friends = get_friends(user.id)
    return JsonResponse(friends, safe=False)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_friend(request):
    logging.info(f"[DATA_VIEWS][ADD_FRIEND]request: {request.user.username}")
    user = request.user
    friendID = request.data.get('userID')
    if friendID is None:
        return JsonResponse({"message": "Missing data"}, status=400)
    add_new_friend(user.id, friendID)
    return JsonResponse({"success": True, "message": "Friend request sent"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_friend(request):
    logging.info(f"[DATA_VIEWS][DELETE_FRIEND]request: {request.user.username}")
    user = request.user
    friendID = request.data.get("userID")
    if friendID is None:
        return JsonResponse({"message": "Missing data"}, status=400)
    remove_friend(user.id, friendID)
    return JsonResponse({"success": True, "message": "Friend removed"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def friends_requests(request):
    logging.info(f"[DATA_VIEWS][FRIENDS_REQUESTS]request: {request.user.username}")
    user = request.user
    fRequests = get_friendship_requests(user.id)

    return JsonResponse(fRequests, safe=False)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friendship(request):
    logging.info(f"[DATA_VIEWS][ACCEPT_FRIENDSHIP]request: {request.user.username}")
    friendship_id = request.data.get("friendshipID")
    accept_friend(friendship_id)
    return JsonResponse({"success": True, "message": "friendship created"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_friendship(request):
    logging.info(f"[DATA_VIEWS][CANCEL_FRIENDSHIP]request: {request.user.username}")
    friendship_id = request.data.get("friendshipID")
    cancel_friend(friendship_id)
    return JsonResponse({"success": True, "message": "friendship canceled"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_user(request):
    logging.info(f"[DATA_VIEWS][SEARCH_USER]request: {request.user.username}")
    username = request.GET.get("friendUsername")
    try:
        user = CustomUser.objects.get(username=username)
        return JsonResponse({"user_id": user.id})
    except CustomUser.DoesNotExist:
        return JsonResponse({"user_id": None})

# API to get the current user's language preference
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    logging.info(f"[DATA_VIEWS][GET_PROFILE]request: {request.user.username}")
    try:
        user = request.user
        profile_data = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
            "preferred_language": user.preferred_language if hasattr(user, 'preferred_language') else settings.LANGUAGE_CODE,
            # Include other profile fields as needed
        }
        return JsonResponse(profile_data, status=200)
    except Exception as e:
        logger.error(f"Error getting profile data: {e}")
        return JsonResponse({"error": "Failed to retrieve profile data"}, status=500)
