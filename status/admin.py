from django.contrib import admin, messages

from .models import Server, State, Alert

admin.site.register(Server)
admin.site.register(State)


class AlertAdmin(admin.ModelAdmin):
    actions = ('view_mail_body',)

    @admin.action(description='View mail body')
    def view_mail_body(self, request, queryset):
        for item in queryset:
            self.message_user(request, item.build_mail_body(), messages.SUCCESS)


admin.site.register(Alert, AlertAdmin)
