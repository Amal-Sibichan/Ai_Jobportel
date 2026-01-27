from django.contrib import admin
from .models import seeker,resume,Education,Experience,skill,application
from recruiter.models import Recruter,documents,job
# Register your models here.
admin.site.register(seeker)
admin.site.register(resume)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(skill)
admin.site.register(Recruter)
admin.site.register(documents)
admin.site.register(job)
admin.site.register(application)

