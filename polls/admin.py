from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import Choice, Question, AuthorBalance, TariffFixed, TariffVariable, CommonTariff
from .models import CommonTariffTwo, TariffVariableTwo, TariffFixedTwo
from django.contrib.auth import get_user_model


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text', 'author', ]}),
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


@admin.register(TariffFixed)
class TariffFixedInline(admin.ModelAdmin):
    list_display = ('author', 'get_current_price')


@admin.register(TariffVariable)
class TariffVariableInline(admin.ModelAdmin):
    list_display = ('author', 'get_current_price')


class CommonTariffInline(admin.TabularInline):
    model = CommonTariff


class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline, CommonTariffInline,)
    list_display = ('username', 'current_price', 'current_price_two')

    def current_price(self, obj):
        return obj.commontariff.get_current_tariff().get_current_price()

    def current_price_two(self, obj):
        return obj.commontarifftwo.get_current_price()


@admin.register(TariffVariableTwo)
class TariffVariableTwoAdmin(PolymorphicChildModelAdmin):
    base_model = TariffVariableTwo


@admin.register(TariffFixedTwo)
class TariffFixedTwoAdmin(TariffVariableTwoAdmin):
    base_model = TariffFixedTwo


@admin.register(CommonTariffTwo)
class CommonTariffTwoAdmin(PolymorphicParentModelAdmin):
    base_model = CommonTariffTwo
    child_models = (TariffVariableTwo, TariffFixedTwo)


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
