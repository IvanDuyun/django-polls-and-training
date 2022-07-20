from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Choice, Question, AuthorBalance
from django.contrib.auth import get_user_model


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text', 'author',]}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('author', 'question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


class AuthorInline(admin.StackedInline):
    model = AuthorBalance
    can_delete = False
    verbose_name_plural = 'author'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline,)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
