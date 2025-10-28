from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from youtube_transcript_api import YouTubeTranscriptApi
from .models import YoutubeVideo, Question, Option, TranscriptChunk
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from .generate_quiz import generate_quiz

ytt_api = YouTubeTranscriptApi()

# Create your views here.
def index(request):
    return render(request, 'ytquiz/ytquiz_home.html')

class QuizAPIView(APIView):
    def get(self, request):
        data = request.data
        video_id = request.GET.get('video_id')
        video = YoutubeVideo.objects.get(video_id=video_id)
        if video.is_ready:
            questions = Question.objects.filter(youtube_video=video)
            return Response({
                'status' : True,
                'message': 'Quiz Fetched',
                'data': {
                    'video_id' : video_id,
                    'questions' : [
                        {
                            'question' : question.question,
                            'options' : [option.option for option in question.options.all()]
                        } for question in questions
                    ]
                },
            })
        else:
            quiz_generated = generate_quiz(video_id)
            if quiz_generated:
                questions = Question.objects.filter(youtube_video=video)
                return Response({
                    'status' : True,
                    'message': 'Quiz Generated',
                    'data': {
                        'video_id' : video_id,
                        'questions' : [
                            {
                                'question' : question.question,
                                'options' : [option.option for option in question.options.all()]
                            } for question in questions
                        ]
                    },
                })
            else:
                return Response({
                    'status' : False,
                    'message': 'Quiz Generation Failed',
                    'data': {
                        'video_id' : video_id,
                    },
                })
                
    def post(self, request):
        data = request.data
        video_id = data.get('video_id')
        video , _ = YoutubeVideo.objects.get_or_create(video_id=video_id)
        
        if _ :
            try:
                transcript_list =  ytt_api.fetch(video_id)
            except Exception as e:
                print(e)
                return Response({
                'status' : False,
                'message': 'Video not found',
                'data': {
                    'video_id' : video_id,
                    'created' : False,
                    },
                })
                

            transcript = " ".join(chunk.text for chunk in transcript_list)
            chunk_size = len(transcript)//15
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
            chunks = splitter.create_documents([transcript])
            
            print(len(chunks))
            print(chunks[1])
            
            for chunk in chunks:
                video.transcript_chunk.add(TranscriptChunk.objects.create(
                    chunk_text = chunk.page_content
                ))

            
            
            return Response({
                'status' : True,
                'message': 'Video Created',
                'data': {
                    'video_id' : video_id,
                    'created' : True,
                    },
                })
            
        return Response({
                'status' : True,
                'message': 'Video already exists',
                'data': {
                    'video_id' : video_id,
                    'created' : True,
                    },
                })