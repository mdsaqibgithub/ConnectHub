from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active')

# Custom actions for accepting and rejecting friend requests
def accept_friend_requests(modeladmin, request, queryset):
    queryset.update(is_accepted=True)
    modeladmin.message_user(request, "Selected friend requests have been accepted.")

def reject_friend_requests(modeladmin, request, queryset):
    queryset.update(is_accepted=False)
    modeladmin.message_user(request, "Selected friend requests have been rejected.")

accept_friend_requests.short_description = 'Accept selected friend requests'
reject_friend_requests.short_description = 'Reject selected friend requests'

# Custom admin class for Friend Request

@admin.register(FriendRequest)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    actions = [accept_friend_requests, reject_friend_requests, "hellloo"]