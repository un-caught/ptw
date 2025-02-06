from django.contrib import admin
from .models import SafetyPrecaution, WorkLocationIsolation, PersonalSafety, Hazards, PTWForm, NHISForm


# Register your models here.
admin.site.register(SafetyPrecaution)
admin.site.register(WorkLocationIsolation)
admin.site.register(PersonalSafety)
admin.site.register(Hazards)
admin.site.register(PTWForm)
admin.site.register(NHISForm)
