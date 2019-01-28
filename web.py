#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    print("Sorry, but Clonenames requires Python 3. Please install it to play!")
    print("Exiting now...")
    sys.exit()

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

import random


import clonenames

app = Flask(__name__)
socketio = SocketIO(app)

games = dict()


@app.route(u'/')
def home_page():
    return render_template(u'index.html')


@app.route(u'/start', methods = [u'GET', u'POST'])
def start_page():
    if request.method == u'POST':
        game = clonenames.Board(request.form.get(u'words'))
        game.load_settings(
            teams = int(request.form.get(u'number')),
            size = int(request.form.get(u'size')))

        room = generate_room_code()

        games[room] = game

        return redirect(url_for(u'game_page', room = room))

    elif request.method == u'GET':
        return render_template(u'start.html', words = clonenames.wordlists)


@app.route(u'/game', methods = [u'GET', u'POST'])
def game_page():
    if request.args.get(u'room'):
        room = request.args.get(u'room')
        return render_template(
            u'game.html',
            show_input = False,
            show_code = True,
            room = room,
            host = True,
            words = games[room].table())

    else:
        try:
            if request.method == u'GET':
                return render_template(
                    u'game.html',
                    show_input = True)

            elif request.method == u'POST':
                room = request.form.get(u'room', False).upper()
                if check_room_code(room):
                    game = games[room]

                    return render_template(
                        u'game.html',
                        show_input = False,
                        show_code = True,
                        room = room,
                        host = request.form.get(u'host', False) == u'on',
                        words = game.table())

                else:
                    return render_template(
                        u'game.html',
                        show_input = True,
                        show_room_alert = True)

        except AttributeError:
            return redirect(url_for(u'home_page'))

# @app.route(u'/statistics')
# def stats_page():
#     return render_template(u'statistics.html',
#         rooms = [games[game].statistics() for game in games])


@socketio.on(u'join')
def join(data):
    join_room(data[u'room'])


@socketio.on(u'clicked')
def handle_host_click(json):
    room_code = json[u'room']

    socketio.emit(u'revealed', {
        u'text': u'Host clicked on {word}'.format(
            word = games[room_code].get(json['id'])[u'word']),
        u'id': u'#{id}'.format(id = json[u'id']),
        u'class': games[room_code].get(json['id'])[u'team']}, room = json['room'])


def generate_room_code():
    letters = u''.join(random.sample(list(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))
    while letters in games.keys():
        return generate_room_code()

    return letters


def check_room_code(code):
    return code in games.keys()


if __name__ == '__main__':
    socketio.run(app, debug=True, host=u'0.0.0.0')
