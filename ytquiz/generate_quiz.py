from .models import YoutubeVideo, Question, Option, TranscriptChunk
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import Literal
from django.conf import settings


def generate_quiz(video_id):
    try:
        video = YoutubeVideo.objects.get(video_id=video_id)
        chunks = video.transcript_chunk.all()
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # or another supported model name
            temperature=0.2,
            max_tokens=None,  # use default or set a limit
            timeout=None,
            api_key=settings.GOOGLE_API_KEY,
        )
        
        class QuestionOptionOutput(BaseModel):
            question: str = Field(description='Question from the context')
            A: str = Field(description='Option A')
            B: str = Field(description='Option B')
            C: str = Field(description='Option C')
            D: str = Field(description='Option D') 
            correct_option: Literal["A", "B", "C", "D"] = Field(
                description='Correct answer — must be one of A, B, C, or D'
            )
            
        parser = PydanticOutputParser(pydantic_object=QuestionOptionOutput)
        
        for chunk in chunks:
            context = chunk.chunk_text
            prompt = PromptTemplate(
                template='''
                    Generate a question from given context with 4 relevant options each from the context below. 
                    Each question should have 1 correct answer and other the closly right. 
                    The correct answer should be one of the options. 
                    The output should be in the following format:
                    {format_instructions}
                    Context: {context}
                    ''',
                input_variables=['context'],
                partial_variables={'format_instructions': parser.get_format_instructions()}
            )

            chain = prompt | llm | parser
            
            chain_result = chain.invoke({'context': context}).dict()
            
            question = Question.objects.create(
                youtube_video=video,
                question=chain_result['question']
            )
            
            Option.objects.create(
                question=question,
                option=chain_result['A'],
                is_correct=(chain_result['correct_option'] == 'A')
            )
            Option.objects.create(
                question=question,
                option=chain_result['B'],
                is_correct=(chain_result['correct_option'] == 'B')
            )
            Option.objects.create(
                question=question,
                option=chain_result['C'],
                is_correct=(chain_result['correct_option'] == 'C')
            )
            Option.objects.create(
                question=question,
                option=chain_result['D'],
                is_correct=(chain_result['correct_option'] == 'D')
            )
    except Exception as e:
        print(e)
        return False
    video.is_ready = True
    video.save()
    return True