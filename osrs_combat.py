from imports import *

# Constants and literal references
attack = "attack"
strength = "strength"
defence = "defence"
magical_defence = "magical defence"
melee = "melee"
ranged = "ranged"
magic = "magic"
prayer = "prayer"
hitpoints = "hitpoints"
hp = hitpoints

damage = "damage"
style = "style"
boost = "boost"
attack_speed = "attack speed"
stab = "stab"
slash = "slash"
crush = "crush"
shared = "shared"
accurate = "accurate"
rapid = "rapid"
longrange = "longrange"
short = accurate
medium = rapid
long = longrange
distance = "distance"

melee_damage_types = [stab, slash, crush]

pray_bonus_dict = {
    "piety": 1.23,
    "chivalry": 1.18,
    "ultimate strength": 1.15,
    "superhuman strength": 1.10,
    "burst of strength": 1.05,
    "none": 1.00
}

piety = "piety"
chivalry = "chivalry"
rigour = "rigour"
augury = "augury"

prayer_modifier_dict = {
    piety: {attack: 1.20, strength: 1.23, defence: 1.25},
    rigour: {attack: 1.20, strength: 1.23, defence: 1.25},
    augury: {attack: 1.25, strength: 1.00, defence: 1.25, magical_defence: 1.25}
}

undead = 'undead'
demon = 'demon'
dragon = 'dragon'
kalphite = 'kalphite'
kurask = 'kurask'
vorkath = 'vorkath'
fire = 'fire'

spt = 0.6       # seconds per tick
tps = spt**-1   # ticks per second
modifier_types = Union[float, int, List[Union[float, int]]]

enchanted_bolts_spec_chance = {'opal': (0.05, 0.10), 'ruby': (0.06, 0), 'diamond': (0.10, 0.15),
                               'dragonstone': (0.06, 0.20), 'onyx': (0.11, 0.20)}

enchanted_bolts_flat_percent = ['diamond', 'onyx']
enchanted_bolts_percent_visible_ranged_level = ['opal', 'dragonstone']


def effective_accuracy_level(stat: int, style_bonus: int, pot_bonus: int, modifier: modifier_types) -> int:
    """Returns the effective attack, ranged attack, or defense level"""
    if type(modifier) == list:
        modifier = math.prod(modifier)

    return math.floor((stat + pot_bonus) * modifier + 8 + style_bonus)


def effective_strength_level(stat: int, style_bonus: int, pot_bonus: int, modifier: modifier_types) -> int:
    """Returns the effective melee or ranged strength level"""
    if type(modifier) == list:
        modifier = math.prod(modifier)

    return math.floor((stat + pot_bonus) * modifier + style_bonus)


def maximum_roll(effective_accuracy_level_: int, stat_bonus: int, roll_modifier: Union[float, int] = 1) -> int:
    """Returns the maximum attack, ranged attack, or defense roll"""

    return effective_accuracy_level_ * (stat_bonus + 64) * roll_modifier


def accuracy(maximum_offensive_roll: int, maximum_defensive_roll: int) -> float:
    """Returns the accuracy given the offensive roll of the attacker and the defensive roll of the target"""

    if maximum_offensive_roll > maximum_defensive_roll:
        return 1 - (maximum_defensive_roll + 2) / (2*(maximum_offensive_roll+1))

    else:
        return maximum_offensive_roll / (2*(maximum_defensive_roll+1))


def dwh_chance_to_land(maximum_offensive_roll: int, maximum_defensive_roll: int, max_hit: int) -> float:
    """Returns the chance for a DWH to land a hit and not roll a 0 for damage"""

    base_acc = accuracy(maximum_offensive_roll, maximum_defensive_roll)
    return base_acc * (1 - 1/(max_hit+1))


def accuracy_bgs_special_attack(maximum_attack_roll: int, maximum_defence_roll: int) -> float:
    """Returns the accuracy of a bandos godsword special attack"""

    return accuracy(2*maximum_attack_roll, maximum_defence_roll)


def base_damage(stat: int, strength_bonus: int, style_bonus: int, pot_bonus: int, modifier: modifier_types) -> float:
    """Returns the base damage formula for the melee or ranged attack style"""

    effective_strength = effective_strength_level(stat, style_bonus, pot_bonus, modifier)
    return 1.3 + effective_strength / 10 + strength_bonus / 80 + effective_strength * strength_bonus / 640


def max_hit(stat: int, strength_bonus: int, style_bonus: int, pot_bonus: int, modifier: modifier_types,
            special_modifier: modifier_types = 1.00) -> int:
    """Returns the max hit for melee or ranged"""
    spec_max = base_damage(stat, strength_bonus, style_bonus, pot_bonus, modifier)

    if not type(special_modifier) == list:
        special_modifier = [special_modifier]

    for sm in special_modifier:
        spec_max = math.floor(spec_max * sm)

    return spec_max


def hit_distribution(max_hit: int, prob_hit: float, num: int = 1) -> dict:
    """Returns a dictionary containing damage amounts and their associated probabilities d[dmg] = prob"""

    damage_distribution: dict = n_convolution_discrete_uniform(max_hit, num)
    adjusted_distribution = {}

    for key, val in damage_distribution.items():
        adjusted_distribution[key] = val * prob_hit

    adjusted_distribution[0] += 1 - prob_hit
    return adjusted_distribution


def mean_damage_per_hit(distribution: dict) -> float:
    """Returns the mean damage per hit given a distribution of damage values and probabilities"""

    weighted_contributions = np.empty(shape=len(distribution.keys()))

    for i, pair in enumerate(distribution.items()):
        weighted_contributions[i] = math.prod(pair)

    return sum(weighted_contributions)


def mean_damage_per_tick(distribution: dict, attack_speed: int) -> float:
    """Returns the mean damage per tick given a distribution of damage values and probabilities, as well as atk spd"""

    return mean_damage_per_hit(distribution) / attack_speed


def random_damage(distribution: Union[dict, np.array]) -> int:
    """Returns a random damage value given a distribution of damage and probability pairs"""

    if type(distribution) == dict:
        choices = []
        probabilities = []

        for key, val in distribution.items():
            choices.append(key)
            probabilities.append(val)

        return random.choices(choices, probabilities)[0]

    elif type(distribution) == np.array:
        choices = np.arange(len(distribution))
        return random.choices(choices, distribution)[0]


def damage_per_tick(max_hit_: int, accuracy_: float, attack_speed: int, max_hp: int = None) -> float:
    """TODO: add capability for non discrete uniform random distributions"""
    hit = max_hit_
    hp = max_hp

    # overkill dps if maximum hitpoints is provided
    if max_hp:
        hit_range = range(0, max_hit_)
        avg_hit = (sum(map(lambda x: (x+1)*(hit-x/2), hit_range)) + (hp-hit)*(hit*(hit+1)/2)) / (hp*(hit + 1))

    else:
        avg_hit = hit / 2

    damage_per_hit = avg_hit * accuracy_    # average damage per hit

    return damage_per_hit / attack_speed


def potion_boost_super_attack(level_attack: int) -> int:
    """Returns the boost given by a super attack potion given the attack level"""

    return 5 + math.floor(level_attack * 0.15)


def potion_boost_super_strength(level_strength: int) -> int:
    """Returns the boost given by a super strength potion given the attack level"""
    return 5 + math.floor(level_strength * 0.15)


def potion_boost_super_defence(level_defence: int) -> int:
    """Returns the boost given by a super defence potion given the attack level"""

    return 5 + math.floor(level_defence * 0.15)


def potion_boost_super_combat(level_attack: int, level_strength: int, level_defence: int) -> Tuple[int, int, int]:
    """Returns the boost given to attack, strength, and defence from a super combat potion given the levels"""

    boost_attack = potion_boost_super_attack(level_attack)
    boost_strength = potion_boost_super_strength(level_strength)
    boost_defence = potion_boost_super_defence(level_defence)

    return boost_attack, boost_strength, boost_defence


def potion_boost_ranging(level_ranged: int) -> int:
    """Returns the boost given to ranged level"""
    return 4 + math.floor(level_ranged * 0.10)


def imbued_heart(level_magic: int) -> int:
    """Returns the magic level boost"""
    return 1 + math.floor(level_magic * 0.10)


def potion_boost_overload_plus(level_attack: int, level_strength: int, level_defence: int, level_ranged: int,
                               level_magic: int) -> Tuple[int, int, int, int, int]:
    """Returns a 5-tuple containing the attack, strength, defence, ranged, and magic bonuses from an overload+"""

    boost_attack = 6 + math.floor(level_attack * 0.16)
    boost_strength = 6 + math.floor(level_strength * 0.16)
    boost_defence = 6 + math.floor(level_defence * 0.16)
    boost_ranged = 6 + math.floor(level_ranged * 0.16)
    boost_magic = 6 + math.floor(level_magic * 0.16)

    return boost_attack, boost_strength, boost_defence, boost_ranged, boost_magic
