from imports import *
import osrs_classes as classes
import osrs_combat as cb


def 

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


def olm_melee_hand(team_scale: int, challenge_mode: bool = False) -> classes.NPC:
    attack_strength_ranged_normal = {
        1: 250,
        2: 270,
        3: 272,
        4: 275,
        5: 295,
        7: 300,
    }

    defence_normal = {
        1: 175,
        2: 176,
        3: 178,
        4: 180,
        5: 182,
        7: 185,
    }

    magic_normal = {
        1: 175,
        2: 189,
        3: 190,
        4: 192,
        5: 206,
        7: 210,
    }

    attack_strength_ranged_cm = {
        1: 375,
        2: 405,
        3: 408,
        4: 412,
        5: 442,
    }

    defence_cm = {
        1: 262,
        2: 264,
        3: 267,
        4: 270,
        5: 273,
    }

    magic_cm = {
        1: 262,
        2: 283,
        3: 285,
        4: 288,
        5: 309,
    }

    asr_dict = attack_strength_ranged_cm if challenge_mode else attack_strength_ranged_normal
    def_dict = defence_cm if challenge_mode else defence_normal
    mag_dict = magic_cm if challenge_mode else magic_normal

    attack = asr_dict[team_scale]
    strength = asr_dict[team_scale]
    defence = def_dict[team_scale]
    ranged = asr_dict[team_scale]
    magic = mag_dict[team_scale]
    hp = olm_hp(team_scale)

    def_bonus_stab = 50
    def_bonus_slash = 50
    def_bonus_crush = 50
    def_bonus_ranged = 50
    def_bonus_magic = 50

    npc = classes.NPC(attack, strength, defence, ranged, magic, hp,
                      (def_bonus_stab, def_bonus_slash, def_bonus_crush, def_bonus_ranged, def_bonus_magic),
                      style=classes.NPCStyle(cb.ranged), types=cb.dragon)

    return npc


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
