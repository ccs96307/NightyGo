# -*- coding: utf-8 -*-
turns = 0
deadStone = []


# ========================= Turns =========================
def get_turns():
    return turns


def set_turns(turn):
    global turns
    turns = turn


# ========================= deadStones =========================
def set_deadStones(deadStones):
    global deadStone
    deadStone = deadStones


def get_deadStones():
    return deadStone
