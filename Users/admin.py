from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile, NurseProfile, AdminProfile, LabProfile


# Register your models here.
class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'
    fields = ['license_number', 'specialization', 'years_of_experience', 'hospital_affiliation', 'is_available']


class NurseProfileInline(admin.StackedInline):
    model = NurseProfile
    can_delete = False
    verbose_name_plural = 'Nurse Profile'
    fk_name = 'user'
    fields = ['license_number', 'specialization', 'years_of_experience', 'hospital_affiliation', 'shift_time', 'is_available']

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'
    fk_name = 'user'
    fields = ['department', 'role_description']

class LabProfileInline(admin.StackedInline):
    model = LabProfile
    can_delete = False
    verbose_name_plural = 'Lab Profile'
    fk_name = 'user'
    fields = ['employee_id', 'lab_department', 'qualification', 'years_of_experience', 'is_available']


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

    def save_model(self, request, obj, form, change):
        #Save the user and create the appropriate profile based on user_type
        super().save_model(request, obj, form, change)

        if not change:
            from django.contrib import messages
            messages.success(
                request,
                f'{obj.get_user_type_display()} profile created for {obj.username}.'
                f'Edit the user to update profile details.'
            )

    def get_inline_instances(self, request, obj=None):
        #Display the appropriate inline based ob user_type
        if not obj:
            return []

        inlines = []
        if obj.user_type == 'DOCTOR':
            inlines.append(DoctorProfileInline(self.model, self.admin_site))
        elif obj.user_type == 'NURSE':
            inlines.append(NurseProfileInline(self.model, self.admin_site))
        elif obj.user_type == 'ADMIN':
            inlines.append(AdminProfileInline(self.model, self.admin_site))

        return inlines


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'years_of_experience', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__email', 'license_number', 'hospital_affiliation']
    readonly_fields = ['user']

    def has_add_permission(self, request):
        #Prevent adding DoctorProfile directly since it should be created via User
        return False


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'years_of_experience', 'is_available']
    list_filter = ['specialization', 'shift_time', 'is_available']
    search_fields = ['user__username', 'user__email', 'license_number', 'hospital_affiliation']
    readonly_fields = ['user']

    def has_add_permission(self, request):
        #Prevent adding NurseProfile directly since it should be created via User
        return False


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'user__email', 'department']
    readonly_fields = ['user']

    def has_add_permission(self, request):
        #Prevent adding AdminProfile directly since it should be created via User
        return False


@admin.register(LabProfile)
class LabProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'lab_department', 'years_of_experience', 'is_available']
    list_filter = ['lab_department', 'is_available']
    serach_fields = ['user__username', 'user__email', 'employe_id']
    readonly_fields = ['user']

    def has_add_permission(self, request):
        return Falsen 