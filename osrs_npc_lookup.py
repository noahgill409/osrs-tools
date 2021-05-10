from imports import *
import osrs_classes as classes
import osrs_combat as cb


# Cox scaling formulas from De0 discord
# https://docs.google.com/spreadsheets/d/1ERBd9qAciV4FGddae2maT8focB6ytCm9y1hiu4Cm6jU?cm


def olm_def_scale_factor(n: int) -> float:
    scale_factor = (math.floor(math.sqrt(n-1)) + math.floor((7/10) * (n-1)) + 100) / 100
    return scale_factor


def olm_off_scale_factor(n: int) -> float:
    scale_factor = (math.floor(math.sqrt(n - 1))*7 + (n-1) + 100)/100
    return scale_factor


def olm_hp_scale_factor(n: int) -> float:
    scale_factor = (n - 3*math.floor(n/8) + 1) / 2
    return scale_factor


def olm_def_lookup(team_scale: int, challenge_mode: bool = False):

    olm_defence = math.floor(175 * olm_def_scale_factor(team_scale))
    olm_defence = math.floor(olm_defence * (3/2)) if challenge_mode else olm_defence

    def_bonus_stab = 50
    def_bonus_slash = 50
    def_bonus_crush = 50

    return olm_defence, def_bonus_stab, def_bonus_slash, def_bonus_crush


def olm_melee_hand(team_scale: int, challenge_mode: bool = False) -> classes.NPC:

    hand_defence, _, _, _ = olm_def_lookup(team_scale, challenge_mode)

    melee = math.floor(250 * olm_off_scale_factor(team_scale))
    ranged = math.floor(250 * olm_off_scale_factor(team_scale))
    magic = math.floor(175 * olm_off_scale_factor(team_scale))
    defence = math.floor(175 * olm_def_scale_factor(team_scale))
    hp = math.floor(600 * olm_hp_scale_factor(team_scale))

    melee = math.floor(1.5 * melee) if challenge_mode else melee
    ranged = math.floor(1.5 * ranged) if challenge_mode else ranged
    magic = math.floor(1.5 * magic) if challenge_mode else magic
    defence = math.floor(1.5 * defence) if challenge_mode else defence
    # hp scale factor on olm is 1 in CM

    attack = melee
    strength = melee

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
    hp = math.floor(600 * olm_hp_scale_factor(team_scale))
    return hp


def tek_hp(team_scale: int, challenge_mode: bool = False):
    # TODO: Implement fix
    return 450 + 450 * math.ceil((team_scale - 1) / 2)
