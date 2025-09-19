import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Asigna imágenes existentes desde media/movie/images a las películas por nombre"

    def handle(self, *args, **kwargs):
        images_folder = 'media/movie/images/'

        if not os.path.exists(images_folder):
            self.stderr.write(f"⚠ Carpeta no encontrada: {images_folder}")
            return

        movies = Movie.objects.all()
        self.stdout.write(f"🔎 Encontradas {movies.count()} películas en la BD")

        for movie in movies:
            # 🔹 Se asume que los archivos siguen el formato: m_{nombre}.png
            #     Ejemplo: película "Titanic" → m_Titanic.png
            filename = f"m_{movie.title}.png"
            image_path_full = os.path.join(images_folder, filename)

            if os.path.exists(image_path_full):
                movie.image = os.path.join('movie/images', filename)  # type: ignore # ruta relativa
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Imagen asignada a {movie.title}"))
            else:
                self.stderr.write(f"❌ No se encontró imagen para {movie.title} → esperado {filename}")

        self.stdout.write(self.style.SUCCESS("Proceso terminado ✅"))