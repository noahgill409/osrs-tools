import math


def olm_def_lookup(team_scale: int, challenge_mode: bool = False):

    d_normal = {
        1: 175,
        2: 176,
        3: 178,
        4: 180,
        5: 182
    }

    d_cm = {
        1: 262,
        2: 264,
        3: 267,
        4: 270,
        5: 273
    }

    def_bonus_stab = 50
    def_bonus_slash = 50
    def_bonus_crush = 50

    if challenge_mode:
        return d_cm[team_scale], def_bonus_stab, def_bonus_slash, def_bonus_crush

    else:
        return d_normal[team_scale], def_bonus_stab, def_bonus_slash, def_bonus_crush


def tek_def_lookup(team_scale: int, challenge_mode: bool = False):

    d_normal = {
        1: 205,
        2: 207,
        3: 209,
        4: 211,
        5: 213
    }

    d_cm = {
        1: 246,
        2: 248,
        3: 250,
        4: 253,
        5: 255
    }

    def_bonus_stab = 155
    def_bonus_slash = 165
    def_bonus_crush = 105

    if challenge_mode:
        return d_cm[team_scale], def_bonus_stab, def_bonus_slash, def_bonus_crush

    else:
        return d_normal[team_scale], def_bonus_stab, def_bonus_slash, def_bonus_crush


def olm_hp(team_scale: int):
    return 600 + 300 * (team_scale - 1)


def tek_hp(team_scale: int):
    return 450 + 450 * math.ceil((team_scale - 1) / 2)
