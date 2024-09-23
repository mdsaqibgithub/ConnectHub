from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.db.models import Q


from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.pagination import Paginations
from django.utils.timezone import now
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler

from .serializers import *
from .models import *


# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }


class FriendRequestThrottle(UserRateThrottle):
    rate = "3/minute" # Limit  to 3 requests per minute

def register_page(request):
    return render(request, 'signup.html')

def login_page(request):
    return render(request, 'login.html')


def friend_list(request):
    return render(request, 'friend-list.html')

def friend_request(request):
    return render(request, 'friend-request.html')

def all_users(request):
    return render(request, 'all_users.html')

def logout_view(request):
    logout(request)
    return redirect('login-page')

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Override the global permission
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = self.get_tokens_for_user(user)
            user_serializer = UserAuthSerializer(user)
            response_data = {
                'user': user_serializer.data,
                'token': token
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class UserLoginView(APIView):
    permission_classes = [AllowAny]  # Override the global permission
    
    def post(self, request):
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')

        # Find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"details": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the password is valid
        if user.check_password(password):
            token = self.get_tokens_for_user(user)
            response_data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                },
                "tokens": token
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)
    


class SearchUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = Paginations
    serializer_class = UserAuthSerializer

    def get_queryset(self):
        query = self.request.query_params.get("search", "")
        if "@" in query:
            return User.objects.filter(email__iexact=query)
        return User.objects.filter(username__icontains=query)
    


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [FriendRequestThrottle]

    def post(self, request, user_id):
        try:
            to_user = User.objects.get(id=user_id)
            from_user = request.user

            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                return Response({"detail": "You have already sent a friend request to this user"}, status=status.HTTP_400_BAD_REQUEST)
            
            if from_user == to_user:
                return Response({"detail": "You cannot send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

            friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
            return Response({"success": "Friend request sent"}, status=status.HTTP_201_CREATED)
        except Throttled as e:
            # Handle throttling
            wait_time = int(e.wait)  # Get the wait time in seconds
            return Response(
                {"detail": f"You are sending requests too quickly. Please wait {wait_time} seconds and try again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )





class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get all pending friend requests where the current user is the 'to_user'
        pending_friend_requests = FriendRequest.objects.filter(to_user=user,  is_accepted=False)

        # Serialize the data (you can create a serializer if needed)
        friend_request_data = [
            {
                "request_id": friend_request.id,
                "from_user": friend_request.from_user.username,
                "sent_at": friend_request.created_at
            }

            for friend_request in pending_friend_requests
        ]

        return Response(friend_request_data, status=status.HTTP_200_OK)


class AcceptRejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id, action):
        friend_request = FriendRequest.objects.get(id=request_id)

        if friend_request.to_user != request.user:
            return Response({"details": "You are not authorized to request to this request"}, status=status.HTTP_403_FORBIDDEN)
        
        if action == 'accept':
            friend_request.is_accepted = True
            friend_request.save()
            return Response({"success": "Friend request accepted"}, status=status.HTTP_200_OK)
        
        elif action == 'reject':
            friend_request.is_accepted = False
            friend_request.save()
            return Response({"success": "Friend request rejected"}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        from_user_friends = FriendRequest.objects.filter(from_user=user, is_accepted=True).values_list('to_user', flat=True)


        to_user_friends = FriendRequest.objects.filter(to_user=user, is_accepted=True).values_list('from_user', flat=True)


        friend_ids = list(from_user_friends) + list(to_user_friends)


        if not friend_ids:
            return Response({"detail": "No friends found."}, status=status.HTTP_200_OK)

        friends_data = User.objects.filter(id__in=friend_ids)


        serializer = UserAuthSerializer(friends_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the current user
        current_user = request.user
        
        # Get the IDs of friends of the current user
        friend_requests = FriendRequest.objects.filter(
            Q(from_user=current_user, is_accepted=True) | 
            Q(to_user=current_user, is_accepted=True)
        )
        
        # Extract friend IDs
        friend_ids = set()
        for request in friend_requests:
            if request.from_user == current_user:
                friend_ids.add(request.to_user.id)
            else:
                friend_ids.add(request.from_user.id)

        # Exclude the current user and their friends from the user list
        users = User.objects.exclude(id=current_user.id).exclude(id__in=friend_ids)
        
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
            for user in users
        ]
        return Response(user_data, status=status.HTTP_200_OK)