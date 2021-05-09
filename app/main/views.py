from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries

#-------自訂檔案--------
from ..models import Movie, User
from .. import db
from . import main

'''主程式視圖涵式'''

@main.after_app_request
def after_request(response):
    '''回報緩慢的資料庫查詢'''
    for query in get_debug_queries():
        if query.duration >= current_app.config['IMOVIES_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParamteres: %s\nDuration: %fs\nContext: %s\n' % (
                    query.statement, query.parameters, query.duration, query.context
                )
            )
    return response



@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.filter((Movie.source == 'hot_movie') | (Movie.source == 'hot_top_movie')).order_by(Movie.write_in_time.desc()).paginate(
                                    page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    # movies = Movie.query.order_by(Movie.rate.desc()).all() #使用降冪排序
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    # movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('index.html', movies = movies, pagination = pagination)

@main.route('/index_sort_by_rate')
def index_sort_by_rate():
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.filter((Movie.source == 'hot_movie') | (Movie.source == 'hot_top_movie')).order_by(Movie.rate.desc().nullslast()).paginate(
                                    page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    # movies = Movie.query.order_by(Movie.rate.desc()).all() #使用降冪排序
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    # movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('index_sort_by_rate.html', movies = movies, pagination = pagination)


@main.route('/top250')
def top250():
    page = request.args.get('page',1, type=int)
    pagination = Movie.query.filter((Movie.source == 'top_movie') | (Movie.source == 'hot_top_movie')).order_by(Movie.write_in_time.desc()).paginate(
                                    page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    # movies = Movie.query.order_by(Movie.rate.desc()).all() #使用降冪排序
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    # movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('top250.html', movies = movies, pagination = pagination)

@main.route('/top_sort_by_rate')
def top250_sort_by_rate():
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.filter((Movie.source == 'top_movie') | (Movie.source == 'hot_top_movie')).order_by(Movie.rate.desc()).paginate(
                                    page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    # movies = Movie.query.order_by(Movie.rate.desc()).all() #使用降冪排序
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    # movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('top250_sort_by_rate.html', movies = movies, pagination = pagination)

@main.route('/add_movie/<int:id>')
@login_required
def add_movie(id):
    '''加入電影到電影清單視圖'''
    user = User.query.filter_by(username = current_user.username).first()
    movie = Movie.query.get_or_404(id)
    if user and movie not in user.movies and movie not in user.watched_movies:
        user.movies.append(movie)
        db.session.commit()
        flash('加入成功')
    
    elif movie in user.movies:
        flash('電影清單裡已經存在該電影')
    elif movie in user.watched_movies:
        flash('你已經看過這個電影囉')
    else:
        flash('加入失敗')
        
    return redirect(request.referrer)


@main.route('/user/movies')
@login_required
def user_movie_list():
    '''使用者電影清單視圖'''
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username = current_user.username).first()
    movie_lists = user.movies.all()
    pagination = user.movies.paginate(page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('user_movie_list.html', movies = movies, pagination = pagination, movie_lists = movie_lists)

@main.route('/user/add_watched_movie/<int:id>')
@login_required
def add_watched_movie(id):
    '''使用者加入已觀看的電影到已觀看電影清單'''
    user = User.query.filter_by(username = current_user.username).first()
    movie = Movie.query.get_or_404(id)
    if user and movie not in user.watched_movies:
        user.watched_movies.append(movie)
        user.movies.remove(movie)
        db.session.commit()
        flash('加入成功')
    elif movie in user.watched_movies:
        flash('你已經看過這個電影囉')
    else:
        flash('加入失敗')
    return redirect(request.referrer)

@main.route('/user/watched')
@login_required
def user_watched_movie():
    '''使用者已觀看清單視圖'''
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username = current_user.username).first()
    movies_lists = user.watched_movies.all()
    pagination = user.watched_movies.paginate(page, per_page = current_app.config['IMOVIES_MOVIES_PER_PAGE'], error_out = False)
    movies = pagination.items
    for movie in movies:
        if movie.rate is None:
            movie.rate = 0
    movies = sorted(movies, key=lambda x : x.rate, reverse=True)
    return render_template('user_watched_movie.html', movies = movies, movie_lists = movies_lists, pagination = pagination)

@main.route('/user/delete_movie/<int:id>')
@login_required
def delete_movie(id):
    '''刪除電影清單裡的電影'''
    user = User.query.filter_by(username = current_user.username).first()
    movie = Movie.query.get(id)
    if user and movie in user.movies:
        user.movies.remove(movie)
        db.session.commit()
        flash('刪除成功')
    else:
        flash('刪除失敗')
    return redirect(request.referrer)

@main.route('/user/delete_watched_movie/<int:id>')
@login_required
def delete_watched_movie(id):
    '''刪除已觀看電影清單裡的電影'''
    user = User.query.filter_by(username = current_user.username).first()
    movie = Movie.query.get(id)
    if user and movie in user.watched_movies:
        user.watched_movies.remove(movie)
        db.session.commit()
        flash('刪除成功')
    else:
        flash('刪除失敗')
    return redirect(request.referrer)
    
