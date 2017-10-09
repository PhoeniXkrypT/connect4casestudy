
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

import models

ROWS = 6
COLS = 7

# Create your views here.
def login(request):
    """
    Write your login view here
    :param request:
    :return:
    """
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('games')
        else:
            context['message'] = 'Incorrect credentials'
    return render(request, 'connect4/login.html', context)

def logout(request):
    """
    write your logout view here
    :param request:
    :return:
    """
    auth_logout(request)
    return redirect('login')

def signup(request):
    """
    write your user sign up view here
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'connect4/signup.html', {'form': form})

@login_required(login_url='/connect4/login/')
def games(request):
    """
    Write your view which controls the game set up and selection screen here
    :param request:
    :return:
    """
    uid = request.user.id
    games = models.Game.objects.filter(Q(player1=uid) | Q(player2=uid))
    cur_games = games.filter(status='Ongoing')
    concl_games = games.filter(status='Over')
    join_games = models.Game.objects.filter(status='New')
    user = request.user
    context = {'user': user, 'cur_games': cur_games, 'concl_games': concl_games, \
               'join_games': join_games}
    return render(request, 'connect4/games.html', context)

def _game_won(board, i, j):
    current_player = board[i][j]

    def recurse(board, i, j, ri, rj, count=0):
        if count == 4:
            return count
        elif i < 0 or i >= ROWS or j < 0 or j >= COLS:
            return count
        if board[i][j] != current_player:
            return count
        return recurse(board, i+ri, j+rj, ri, rj, count+1)

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for ri, rj in directions:
        c = recurse(board, i, j, ri, rj, 0)
        if c == 4:
            return True

        c2 = recurse(board, i, j, -ri, -rj, 0)
        if c2 == 4 or (c + c2 - 1) == 4:
            return True
    return False

def _fill_board(coins):
    board = [['--' for _ in xrange(COLS)] for _ in xrange(ROWS)]
    for each in coins.values():
        board[each['row']][each['column']] = each['player_id']
    return board

@login_required(login_url='/connect4/login/')
def play(request):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    # print gid
    gid = 1
    context = {'topic': 'Play'}
    game = models.Game.objects.get(id=gid)
    currentplayer = game.player1
    board = _fill_board(game.coin_set)
    currentplayer = game.player1 if game.last_move.player == game.player2 \
                    else game.player2

    if request.method == 'POST':
        col = int(request.POST.get('move'))
        row, r_val = 0, game.coin_set.filter(column=col)
        if r_val:
            row = r_val.order_by('-row')[0].row + 1
        if row >= ROWS:
            context['message'] = "Invalid move! Column %d is full." % (col)
        else:
            game.make_move(currentplayer, row, col)
            board = _fill_board(game.coin_set)
            if _game_won(board, row, col):
                game.status = 'Over'
                game.winner = currentplayer
                game.save()
                context['won'] = 'User%s WON!!!' % (currentplayer)

    context['board'] = board[::-1]
    print "CURRENT: ", currentplayer, "\nGAME: ", game
    return render(request, 'connect4/play.html', context)

