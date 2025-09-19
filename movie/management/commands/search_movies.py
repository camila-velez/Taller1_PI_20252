import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Search for movies based on a text prompt using embeddings"

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The search prompt')

    def handle(self, *args, **kwargs):
        # ✅ Load OpenAI API key
        load_dotenv('openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # ✅ Get the search prompt from command line
        prompt = kwargs['prompt']
        self.stdout.write(self.style.WARNING(f"Searching for movies similar to: {prompt}"))

        # ✅ Generate embedding for the search prompt
        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        prompt_emb = get_embedding(prompt)

        # ✅ Compute cosine similarity with each movie embedding
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        movies = Movie.objects.all()
        scored_movies = []

        for movie in movies:
            if not movie.emb:
                continue
            movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
            score = cosine_similarity(prompt_emb, movie_emb)
            scored_movies.append((movie.title, score))

        # ✅ Sort and show top 5
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        top5 = scored_movies[:5]

        self.stdout.write(self.style.SUCCESS("\nTop 5 resultados:\n"))
        for title, score in top5:
            self.stdout.write(f"{title} - {score:.4f}")
