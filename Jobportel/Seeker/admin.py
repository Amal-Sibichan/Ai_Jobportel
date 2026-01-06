from django.contrib import admin
from .models import seeker,resume,Education,Experience,skill
# Register your models here.
admin.site.register(seeker)
admin.site.register(resume)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(skill)
