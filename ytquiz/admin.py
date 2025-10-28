from django.contrib import admin
from .models import YoutubeVideo, Question, Option, TranscriptChunk

# Register your models here.
admin.site.site_header = "Shashwat Admin"
admin.site.site_title = "Shashwat Admin Portal"
admin.site.index_title = "Welcome to Shashwat Researcher Portal"

admin.site.register(TranscriptChunk)
admin.site.register(YoutubeVideo)
admin.site.register(Question)
admin.site.register(Option)
