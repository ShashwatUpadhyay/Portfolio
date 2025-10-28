from django.db import models
from base.models import BaseModel
import pandas as pd

# Create your models here.
class TranscriptChunk(BaseModel):
    chunk_text = models.TextField(null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)
    start_time = models.FloatField(null=True, blank=True)
    end_time = models.FloatField(null=True, blank=True)

class YoutubeVideo(BaseModel):
    video_id = models.CharField(max_length=100)
    is_open = models.BooleanField(default=True)
    transcript = models.TextField(null=True, blank=True)
    transcript_chunk = models.ManyToManyField(TranscriptChunk, related_name='transcript_chunks', null=True, blank=True)
    is_ready = models.BooleanField(default=False)
    
    def __str__(self):
        return self.video_id
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # if self.exam_file:
        #     self.import_question_from_excel()

            
    # def import_question_from_excel(self):
    #     df = pd.read_excel(self.exam_file.path)
        
    #     for index,row in df.iterrows():
    #         question_ = row['Question']
    #         chA = row['A']
    #         chB = row['B']
    #         chC = row['C']
    #         chD = row['D']
    #         answer = row['Answer']
    #         question = Question.objects.get_or_create(question = question_, exam = self)
    #         ch_A = Option.objects.get_or_create(question = question[0], option = chA, is_correct = answer == 'A')
    #         ch_B = Option.objects.get_or_create(question = question[0], option = chB, is_correct = answer == 'B')
    #         ch_C = Option.objects.get_or_create(question = question[0], option = chC, is_correct = answer == 'C')
    #         ch_D = Option.objects.get_or_create(question = question[0], option = chD, is_correct = answer == 'D')

class Question(BaseModel):
    youtube_video = models.ForeignKey(YoutubeVideo , on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question = models.TextField(null=True, blank=True)
    
    @property
    def all_options(self):
        return self.options.all()
    
    def __str__(self):
        return f'{self.youtube_video.video_id}'
    
class Option(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.question.question[:40]}-----{self.option[:20]}'