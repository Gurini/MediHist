from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile, NurseProfile, AdminProfile


# Register your models here.
class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'


class NurseProfileInline(admin.StackedInline):
    model = NurseProfile
    can_delete = False
    verbose_name_plural = 'Nurse Profile'
    fk_name = 'user'

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #Custom user admin
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'date_of_birth')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
                ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'date_of_birth', 'email', 'first_name', 'last_name')
        }),
    )

    def get_inline_instances(self, request, obj=None):
        #Display the appropriate inline based ob user_type
        if not obj:
            return []

        inlines = []
        if obj.user_type == 'DOCTOR':
            inlines.append(DoctorProfileInLine(self.model, self.admin_site))
        elif obj.user_type == 'NURSE':
            inlines.append(NurseProfileInLine(self.model, self.admin_site))
        elif obl.user_type == 'ADMIN':
            inlines.append(AdminProfileInLine(self.model, self.admin_site))

        return inlines


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'years_of_experience', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__email', 'license_number', 'hospital_affiliation']
    readonly_fields = ['user']


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'years_of_experience', 'is_available']
    list_filter = ['specialization', 'shift_time', 'is_available']
    search_fields = ['user__username', 'user__email', 'license_number', 'hospital_affiliation']
    readonly_fields = ['user']


@admin.register(AdminProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'user__email', 'department']
    readonly_fields = ['user']