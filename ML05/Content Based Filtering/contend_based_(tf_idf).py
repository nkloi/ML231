# -*- coding: utf-8 -*-
"""Contend_Based (TF-IDF).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jWBESNbnMj0kIFuln_8hWOryt9MSDmP1

### Tập dữ liệu sử dụng là ml-latest-small bao gồm: 100,000 ratings and 3,600 tag applications applied to 9,000 movies by 600 users. Last updated 9/2018.
"""

!https://files.grouplens.org/datasets/movielens/ml-latest-small.zip

"""# **Content_Based (TF-IDF)**
(chạy được) (Xây dựng tf-idf dựa trên titles và tags)
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Đọc tập tin movies.csv
df_movies = pd.read_csv('/content/drive/MyDrive/ml-latest-small/movies.csv')

# Đọc tập tin ratings.csv
df_ratings = pd.read_csv('/content/drive/MyDrive/ml-latest-small/ratings.csv')

# Đọc tập tin tags.csv
df_tags = pd.read_csv('/content/drive/MyDrive/ml-latest-small/tags.csv')

# Kết hợp thông tin từ các tập tin thành một bảng dữ liệu tổng hợp
df_combined = pd.merge(df_movies, df_ratings, on='movieId')
df_combined = pd.merge(df_combined, df_tags, on=['movieId', 'userId'])

# Xây dựng biểu diễn dữ liệu dựa trên tiêu đề và nhãn
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df_combined['title'] + ' ' + df_combined['tag'])

# Tính toán ma trận độ tương đồng cosine
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Hàm gợi ý phim tương tự
def get_similar_movies(movie_id, cosine_sim, N=5):
    # Lấy chỉ số của phim dựa trên movieId
    idx = df_movies[df_movies['movieId'] == movie_id].index[0]
    # Lấy điểm số độ tương đồng của phim đó với tất cả các phim khác
    sim_scores = list(enumerate(cosine_sim[idx]))
    # Sắp xếp các phim tương tự theo thứ tự giảm dần của độ tương đồng
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Lấy chỉ số của N phim tương tự hàng đầu
    top_similar_movies = sim_scores[1:N+1]  # Bỏ qua phim đầu tiên vì nó là chính phim đang xem xét

    # Lấy thông tin chi tiết về các phim tương tự
    similar_movie_ids = [df_movies.iloc[i[0]]['movieId'] for i in top_similar_movies]
    similar_movies = df_movies[df_movies['movieId'].isin(similar_movie_ids)]

    return similar_movies

# Gợi ý 5 phim tương tự với movieId là 1 "Toy Story (1995)"
similar_movies = get_similar_movies(1, cosine_sim, N=5)
similar_movies_dataframe = pd.DataFrame(similar_movies)
similar_movies_dataframe

"""# **Content_Based (TF-IDF)**
(chạy được) (Xây dựng tf-idf dựa trên nội dung phim)
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Đọc dữ liệu từ CSV
movies = pd.read_csv('/content/drive/MyDrive/ml-latest-small/movies.csv')
tags = pd.read_csv('/content/drive/MyDrive/ml-latest-small/tags.csv')

# Kết hợp thông tin từ movies và tags (nếu có) để tạo nội dung cho mỗi bộ phim
movies = pd.merge(movies, tags, on='movieId', how='left')

# Kiểm tra sự trùng lặp trong DataFrame và loại bỏ chúng
movies_no_duplicates = movies.drop_duplicates(subset=['movieId'])

# Kiểm tra xem có bất kỳ giá trị lặp lại nào trong cột 'movieId' không
duplicate_movie_ids = movies[movies.duplicated(['movieId'])]['movieId']

# Xử lý và chuyển đổi dữ liệu
movies['content'] = movies['genres'] + ' ' + movies['tag'].fillna('')

import re

# Hàm để bỏ năm trong tiêu đề của phim
def remove_year_from_title(title):
    # Sử dụng biểu thức chính quy để tìm và thay thế phần năm trong tiêu đề
    cleaned_title = re.sub(r'\(\d{4}\)', '', title).strip()
    return cleaned_title

# Sử dụng TF-IDF để vector hóa nội dung của các bộ phim
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(movies['content'])

# Tính ma trận tương đồng cosine
cosine_simm = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_recommendations(movie_title, num_recommendations, cosine_sim=cosine_simm, movies_df=movies):
    # Bỏ năm trong tiêu đề của phim đã cho
    cleaned_movie_title = remove_year_from_title(movie_title)

    # Lấy chỉ số của bộ phim có tiêu đề đã cho (sau khi đã bỏ năm)
    idx = movies_df.index[movies_df['title'].apply(remove_year_from_title) == cleaned_movie_title].tolist()[0]

    # Lấy các điểm tương đồng cặp với các bộ phim khác
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sắp xếp các bộ phim dựa trên điểm tương đồng
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Lấy chỉ số của các bộ phim
    movie_indices = [i[0] for i in sim_scores]

    # Lấy đề xuất (loại bỏ bộ phim đã truy vấn và các bộ phim trùng lặp)
    recommendations = movies_df.iloc[movie_indices]
    recommendations = recommendations[recommendations['title'].apply(remove_year_from_title) != cleaned_movie_title].drop_duplicates(subset=['title'])

    # Giới hạn kết quả theo số lượng đề xuất
    recommendations = recommendations.head(num_recommendations)[['title', 'genres']]

    return recommendations

# Lấy 5 bộ phim được đề xuất cho "Toy Story (1995)"
movie_title = "Toy Story (1995)"
num_recommendations = 5
recommendations = get_recommendations(movie_title, num_recommendations)

# Chuyển đổi Series thành DataFrame
df_recommendations = pd.DataFrame(recommendations)
df_recommendations