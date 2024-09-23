from django.urls import path
from connection.views import *

urlpatterns = [
    # User Authentication
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('register-page/', register_page, name="signup-page"), 
    path('login/', UserLoginView.as_view(), name="login"),
    path('', login_page, name="login-page"), 
    path('logout/', logout_view, name='logout'),

    # User Management
    path('profile/', ProfileView.as_view(), name="profile"),
    path('search/', SearchUserView.as_view(), name="users"),
    path('user_list/', UserListView.as_view(), name='user_list'),

    # Friend Requests
    path('friend_request/<int:user_id>/', SendFriendRequestView.as_view(), name="friend_request"),
    path('friend_request_list/', FriendRequestListView.as_view(), name="friend_request_list"),
    path('requests/<int:request_id>/<str:action>/', AcceptRejectFriendRequestView.as_view(), name='accept-reject'),

    # Friend List
    path('friends/', FriendListView.as_view(), name='friends'),

    # Other Pages
    path('friend_list/', friend_list, name="friend_list"),
    path('friends_request/', friend_request, name="friends_request"),
    path('all_users/', all_users, name='all_users'),
    
]
