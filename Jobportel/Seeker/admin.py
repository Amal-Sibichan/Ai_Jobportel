from django.contrib import admin
from .models import seeker,resume,Education,Experience,skill
from recruiter.models import Recruter,documents
# Register your models here.
admin.site.register(seeker)
admin.site.register(resume)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(skill)
admin.site.register(Recruter)
admin.site.register(documents)
