from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
from dotenv import load_dotenv
import os
import numpy as np
from openai import OpenAI

from.models import Movie

# Create your views here.

def home(request):
    searchTerm = request.GET.get('searchMovie')
    movies = Movie.objects.all()
    searchTerm = request.GET.get('searchMovie', '')
    if searchTerm: 
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies, 'searchTerm': searchTerm})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email', '')
    return render(request, 'signup.html', {'email': email})

def statistics_view(request):
    matplotlib.use('Agg') 
    all_movies = Movie.objects.all() 

    # =====================
    # Gráfica 1: por año
    # =====================
    movie_counts_by_year = {} 
    for movie in all_movies: 
        year = movie.year if movie.year else "None" 
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    bar_width = 0.5 
    bar_positions = range(len(movie_counts_by_year)) 

    plt.bar(bar_positions, list(movie_counts_by_year.values()), width=bar_width, align='center') 
    plt.title('Movies per year') 
    plt.xlabel('Year') 
    plt.ylabel('Number of movies') 
    plt.xticks(bar_positions, list(movie_counts_by_year.keys()), rotation=90) 
    plt.subplots_adjust(bottom=0.3) 

    buffer = io.BytesIO() 
    plt.savefig(buffer, format='png') 
    buffer.seek(0) 
    plt.close() 

    image_png = buffer.getvalue() 
    buffer.close() 
    graphic_year = base64.b64encode(image_png).decode('utf-8') 

    # =====================
    # Gráfica 2: por género
    # =====================
    movie_counts_by_genre = {}
    for movie in all_movies:
        genre = movie.genre if movie.genre else "None"
        movie_counts_by_genre[genre] = movie_counts_by_genre.get(genre, 0) + 1

    plt.figure()
    plt.bar(range(len(movie_counts_by_genre)), list(movie_counts_by_genre.values()), width=bar_width, align='center')
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(range(len(movie_counts_by_genre)), list(movie_counts_by_genre.keys()), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO() 
    plt.savefig(buffer, format='png') 
    buffer.seek(0) 
    plt.close() 

    image_png = buffer.getvalue() 
    buffer.close() 
    graphic_genre = base64.b64encode(image_png).decode('utf-8') 

    # =====================
    # Renderizar ambas gráficas
    # =====================
    return render(request, 'statistics.html', {
        'graphic_year': graphic_year,
        'graphic_genre': graphic_genre
    })

# Cargar API key
load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recommendation(request):
    recommended_movie = None
    user_prompt = ""

    if request.method == "POST":
        user_prompt = request.POST.get("prompt", "")

        if user_prompt.strip():
            # Generar embedding del prompt
            response = client.embeddings.create(
                input=[user_prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

            # Buscar la película más similar
            max_similarity = -1
            for movie in Movie.objects.all():
                if not movie.emb:
                    continue
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                similarity = cosine_similarity(prompt_emb, movie_emb)

                if similarity > max_similarity:
                    max_similarity = similarity
                    recommended_movie = movie

    return render(request, "recomendation.html", {
        "prompt": user_prompt,
        "movie": recommended_movie
    })