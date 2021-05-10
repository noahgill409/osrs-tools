# from imports import *
from osrs_classes import *
# from bedevere.markov import *
import osrs_gear as gear
import osrs_markov


WHIPPER = Player(
    attack=75,
    strength=72,
    defence=70,
    ranged=77,
    magic=77,
    hitpoints=73,
    prayer=74,
    gear_list=gear.presets['abyssal whip scuff'],
    style=MeleeStyle(cb.flick, cb.slash, cb.attack),
    prayers=None,
    overload=False,
    slayer_task=False
)

RAPIER = Player(
    attack=75,
    strength=74,
    defence=70,
    ranged=77,
    magic=77,
    hitpoints=76,
    prayer=74,
    gear_list=gear.presets['ghrazi rapier scuff'],
    style=MeleeStyle(cb.stab, cb.stab, cb.strength),
    prayers=None,
    overload=False,
    slayer_task=False
)

STAFFER = Player(
    attack=75,
    strength=67,
    defence=63,
    ranged=77,
    magic=77,
    hitpoints=73,
    prayer=74,
    gear_list=gear.presets['staff of light scuff'],
    style=MeleeStyle(cb.slash, cb.slash, cb.strength),
    prayers=None,
    overload=False,
    slayer_task=False
)

SAND_CRAB = NPC(
    attack=1,
    strength=1,
    defence=1,
    ranged=1,
    magic=1,
    hitpoints=60,
    defence_bonuses=(0, 0, 0, 0, 0),
    style=NPCStyle(cb.crush),
    types=None
)

AMMONITE_CRAB = NPC(
    attack=1,
    strength=1,
    defence=1,
    ranged=1,
    magic=1,
    hitpoints=100,
    defence_bonuses=(0, 0, 0, 0, 0),
    style=NPCStyle(cb.crush),
    types=None
)




def sandbox():
    pass


def sandbox_two(attacker: Player, defender: NPC, potion_decay: int = None):
    pot_decay = potion_decay if potion_decay else 11    # minutes
    re_aggro_ratio = 1 - ((12 + 10 + 0) / 3000)   # ticks lost per 30 minutes

    # clear the field
    attacker.neutralize_buff()
    attacker.super_combat_potion()
    expected_hits_list = []

    max_health = defender.hitpoints

    for minute in range(pot_decay):
        damage_data = attacker.attack_npc(defender)
        max_hit = damage_data.max_hit

        crab_absorbing_mc = osrs_markov.health_markov_chain(attacker, defender)
        expected_hits = crab_absorbing_mc.expected_steps[0][0]
        expected_hits_list.append(expected_hits)

        # per level stats printout
        eff_atk = attacker.attack + attacker.attack_pot_bonus
        eff_str = attacker.strength + attacker.strength_pot_bonus
        info_string = 'ATK: {:2.0f} STR: {:2.0f}' \
                      '\n\tXP/HR: {:4.2f}\tMax Hit: {:2.0f}'
        ticks_per_kill = attacker.attack_speed * expected_hits
        xp_per_kill = max_health * 4
        xp_per_tick = xp_per_kill / ticks_per_kill
        xp_per_hour = xp_per_tick * 6000
        print(info_string.format(eff_atk, eff_str, xp_per_hour, max_hit))

        attacker.tick_down()

    mean_expected_hits = np.mean(expected_hits_list)
    # it takes mean expected hits to deal 60 damage -> 240 style xp
    # it takes weapon speed ticks per hit
    mean_ticks_per_kill = attacker.attack_speed * mean_expected_hits
    xp_per_kill = max_health * 4
    mean_xp_per_tick = xp_per_kill / mean_ticks_per_kill
    mean_xp_per_hour = mean_xp_per_tick * 6000
    mean_xp_per_hour_scuffed = mean_xp_per_hour * re_aggro_ratio

    print('mean\n\tXP/HR: {:4.2f}'.format(mean_xp_per_hour_scuffed))


if __name__ == '__main__':

    trials_run = 1e1
    sandbox_two(RAPIER, SAND_CRAB)


