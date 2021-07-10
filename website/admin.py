from django.contrib import admin
from website.models import Issue, Service, UserProfile, Bounty, Solution, Taker, Comment, Payment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource

class ServiceAdmin(admin.ModelAdmin):
     list_display=[] 
     for x in Service._meta.get_fields(): 
         list_display.append(str(x.name))

class BountyAdmin(admin.ModelAdmin):
    list_display = ('issue','price','user','created','ends','checkout_id')

class UserProfileAdmin(admin.ModelAdmin):
    list_display=('user','balance','payment_service', 'payment_service_email')

class IssueAdmin(admin.ModelAdmin):
    list_display=[]
    for x in Issue._meta.get_fields():
        if x.name not in "service_id,winner_id,taker,solution,comment,payment":
            list_display.append(str(x.name))
    readonly_fields = ("created","modified")
    list_display_links = ("title",)

class TakerAdmin(admin.ModelAdmin):
    list_display=('user','issue','created')

class CommentAdmin(admin.ModelAdmin):
    list_display=('username','issue','service_comment_id','created','updated','content')

class SolutionAdmin(admin.ModelAdmin):
    list_display=('issue','user','url','status','created','modified')

admin.site.unregister(User)

UserAdmin.list_display = ('id','username','email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('content_type',
        'user',
        'action_time',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
admin.site.register(Session, SessionAdmin)

admin.site.register(LogEntry, LogEntryAdmin)

admin.site.register(Issue, IssueAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Bounty, BountyAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(Taker, TakerAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Payment)
