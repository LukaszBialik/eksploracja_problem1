from RatingSystem import RatingSystem
from RatingLib import Movie, User
import csv
import collections


class MySystem(RatingSystem):
    def __init__(self):
        super().__init__()

        with open('../data/movie.csv', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for line in csv_reader:
                m_id = int(line[0])
                if m_id in Movie.index:
                    main_genre = line[2].split('|')[0]
                    Movie.index[m_id].genres.append(main_genre)

        self.movie_avg = {}
        self.global_genre_avg = {}

        genre_sum = collections.defaultdict(float)
        genre_count = collections.defaultdict(int)

        total_sum = 0
        total_count = 0
        for movie in Movie.index.values():
            total_sum += sum(movie.ratings)
            total_count += len(movie.ratings)
        self.global_avg_movies_rating = total_sum / total_count if total_count > 0 else 3.0

        for movie_id, movie in Movie.index.items():
            c_movie = 5.0 - len(movie.ratings) if len(movie.ratings) < 5 else 0
            n_ratings = len(movie.ratings)
            avg = (sum(movie.ratings) + c_movie * self.global_avg_movies_rating) / (n_ratings + c_movie)
            self.movie_avg[movie_id] = avg

            if n_ratings > 0 and len(movie.genres) > 0:
                genre = movie.genres[0]
                genre_sum[genre] += sum(movie.ratings)
                genre_count[genre] += n_ratings


        for genre in genre_sum.keys():
            self.global_genre_avg[genre] = genre_sum[genre] / genre_count[genre]

    def rate(self, user, movie):
        target_movie = Movie.index[movie]

        avg_movie_rating = self.movie_avg.get(movie, self.global_avg_movies_rating)

        if len(user.ratings) == 0:
            return round(avg_movie_rating * 2) / 2


        c_user = 55.0 - len(user.ratings) if len(user.ratings) < 55 else 0
        n_user_ratings = len(user.ratings)
        user_movies_average = (sum(user.ratings.values()) + c_user * self.global_avg_movies_rating) / (n_user_ratings + c_user)


        user_genre_bias = 0
        if len(target_movie.genres) > 0:
            movie_genre = target_movie.genres[0]
            user_genre_ratings = [rating for movie_id, rating in user.ratings.items()
                                  if len(Movie.index[movie_id].genres) > 0 and Movie.index[movie_id].genres[0] == movie_genre]

            if len(user_genre_ratings) > 0:
                c_user_genre = 30 - len(user_genre_ratings) if len(user_genre_ratings) < 30 else 0
                user_genre_rating = ((sum(user_genre_ratings) + c_user_genre * user_movies_average) /
                                     (len(user_genre_ratings) + c_user_genre))

                global_genre_rating = self.global_genre_avg.get(movie_genre, self.global_avg_movies_rating)
                user_genre_bias = user_genre_rating - global_genre_rating
                user_genre_bias = round(user_genre_bias * 2) / 2


        prediction = round(user_movies_average + user_genre_bias + avg_movie_rating)/2
        return min(5.0 ,max(prediction,0.5))

    def __str__(self):
        return 'System created by 155956 and 156094'
