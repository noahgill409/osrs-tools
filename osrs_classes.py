from imports import *
from bedevere.discrete_sums import *
import osrs_combat as cb
import osrs_gear as gear


class Style:

    magic_styles = [cb.accurate, cb.longrange]

    def __init__(self, combat_style: str, damage_type: str, bonus_tuple: Tuple[int, int, int],
                 attack_speed_modifier: int = 0):
        self.combat_style = combat_style
        self.damage_type = damage_type
        self.attack_bonus, self.strength_bonus, self.defence_bonus = bonus_tuple
        self.attack_speed_modifier = attack_speed_modifier


class MeleeStyle(Style):
    styles = {cb.attack: (3, 0, 0),
              cb.strength: (0, 3, 0),
              cb.defence: (0, 0, 3),
              cb.shared: (1, 1, 1), }

    def __init__(self, combat_style: str, damage_type: str, experience: str):
        """Create a style object from the name, type of damage, and experience awarded"""
        assert damage_type in cb.melee_damage_types

        bonus_tuple = MeleeStyle.styles[experience]
        super().__init__(combat_style, damage_type, bonus_tuple)


class RangedStyle(Style):
    styles = {cb.accurate: {cb.boost: (3, 3, 0), cb.attack_speed: 0, cb.distance: (1.00, 0.75, 0.50)},
              cb.rapid: {cb.boost: (0, 0, 0), cb.attack_speed: -1, cb.distance: (0.75, 1.00, 0.75)},
              cb.longrange: {cb.boost: (0, 0, 0), cb.attack_speed: 0, cb.distance: (0.50, 0.75, 1.00)}
              }

    def __init__(self, combat_style: str):
        """Create a style object from the name alone, should be uniform across ranged weapons"""
        bonus_tuple = RangedStyle.styles[combat_style][cb.boost]
        attack_speed_modifier = RangedStyle.styles[combat_style][cb.attack_speed]
        self.distance_modifier_tuple = RangedStyle.styles[combat_style][cb.distance]
        super().__init__(combat_style, cb.ranged, bonus_tuple, attack_speed_modifier)


class NPCStyle(Style):

    def __init__(self, damage_type: str):
        combat_style = 'NPC'
        damage_type = damage_type
        bonus_tuple = (1, 1, 1)

        super().__init__(combat_style, damage_type, bonus_tuple)


class DamageData:

    def __init__(self, damage_distribution: Union[dict, np.ndarray], attack_speed: int, accuracy: float = None):
        """Initializes an DamageData object from a damage distribution and attack speed.

        This class collects various aspects of a damaging attack into one object with different parameters, an optional
        parameter, accuracy, is given for niche purposes such as the dragon warhammer and bandos godsword markov
        chain construction where defence reduction for literal misses matters (tekton). It's also given to allow a
        simple function to output a DamageData object wherever possible without losing information that could be
        useful down the line"""

        self.max_hit = max(damage_distribution)
        self.attack_speed = attack_speed
        self.accuracy = accuracy

        if type(damage_distribution) == np.array:
            self.damage_distribution = {}

            for i in range(len(damage_distribution)):
                self.damage_distribution[i] = damage_distribution[i]

        else:
            self.damage_distribution = damage_distribution

        self.chance_to_damage = 1 - self.damage_distribution[0]
        self.mean_damage_per_hit = cb.mean_damage_per_hit(self.damage_distribution)

    def mean_damage_per_tick(self):
        return cb.mean_damage_per_tick(self.damage_distribution, self.attack_speed)

    def damage_distribution_array_pair(self) -> Tuple[np.array, np.array]:
        """Returns a pair of numpy arrays representing damage values and their associated probability

        Damage probabilities are inferred to be equal to 0 if not contained within the object's distribution and the
        damage array returns is equivalent to np.arange(shape=len(probability))"""

        n = max(self.damage_distribution) + 1
        damage = np.arange(n)
        probability = np.zeros(shape=n)

        for i in damage:
            try:
                probability[i] = self.damage_distribution[i]

            except KeyError:
                continue

        return damage, probability


class Mob:

    def __init__(self, attack: int, strength: int, defence: int, ranged: int, magic: int, hitpoints: int,
                 attack_bonus_tuple: Tuple[int, int, int, int, int],
                 defence_bonus_tuple: Tuple[int, int, int, int, int],
                 strength_bonus_tuple: Tuple[int, int, float], style: Style):

        self.attack = attack
        self.strength = strength
        self.defence = defence
        self.ranged = ranged
        self.magic = magic
        self.hitpoints = hitpoints

        self._defence_current = self.defence
        self._hitpoints_current = self.hitpoints

        self.attack_bonus_stab, self.attack_bonus_slash, self.attack_bonus_crush, \
            self.attack_bonus_ranged, self.attack_bonus_magic = attack_bonus_tuple

        self.defence_bonus_stab, self.defence_bonus_slash, self.defence_bonus_crush, \
            self.defence_bonus_ranged, self.defence_bonus_magic = defence_bonus_tuple

        self.strength_bonus_melee, self.strength_bonus_ranged, self.strength_bonus_magic = strength_bonus_tuple

        self._attack_bonus_dictionary = {
            cb.stab: self.attack_bonus_stab,
            cb.slash: self.attack_bonus_slash,
            cb.crush: self.attack_bonus_crush,
            cb.ranged: self.attack_bonus_ranged,
            cb.magic: self.attack_bonus_magic
        }

        self._defence_bonus_dictionary = {
            cb.stab: self.defence_bonus_stab,
            cb.slash: self.defence_bonus_slash,
            cb.crush: self.defence_bonus_crush,
            cb.ranged: self.defence_bonus_ranged,
            cb.magic: self.defence_bonus_magic
        }

        self._strength_bonus_dictionary = {
            cb.melee: self.strength_bonus_melee,
            cb.ranged: self.strength_bonus_ranged,
            cb.magic: self.strength_bonus_magic
        }

        self.style = style

        self.attack_pot_bonus = 0
        self.strength_pot_bonus = 0
        self.defence_pot_bonus = 0
        self.ranged_pot_bonus = 0
        self.magic_pot_bonus = 0

    def max_hit(self, modifier: cb.modifier_types, special_modifier: cb.modifier_types = 1.00) -> int:
        """Returns the max hit a Mob is capable of dealing with melee or ranged damage"""
        if self.style.damage_type in cb.melee_damage_types:
            stat = self.strength
            strength_bonus = self.strength_bonus_melee
            pot_bonus = self.strength_pot_bonus

        elif self.style.damage_type == cb.ranged:
            stat = self.ranged
            strength_bonus = self.strength_bonus_ranged
            pot_bonus = self.ranged_pot_bonus

        else:
            raise Exception(self.style.damage_type)

        return cb.max_hit(stat, strength_bonus, self.style.strength_bonus, pot_bonus, modifier, special_modifier)

    def maximum_attack_roll(self, attack_modifier: cb.modifier_types, roll_modifier: cb.modifier_types = 1.00) -> int:
        """Returns the maximum attack roll for melee, ranged, and TODO:magic attacks"""
        if self.style.damage_type in cb.melee_damage_types:
            stat = self.attack
            pot_bonus = self.attack_pot_bonus

        elif self.style.damage_type == cb.ranged:
            stat = self.ranged
            pot_bonus = self.ranged_pot_bonus

        else:
            raise Exception(self.style.damage_type)

        effective_accuracy_level = cb.effective_accuracy_level(stat, self.style.attack_bonus, pot_bonus,
                                                               attack_modifier)
        maximum_roll = cb.maximum_roll(effective_accuracy_level, self._attack_bonus_dictionary[self.style.damage_type],
                                       roll_modifier)
        return maximum_roll

    def maximum_defence_roll(self, damage_type: str, defence_modifier: cb.modifier_types,
                             roll_modifier: cb.modifier_types = 1.00) -> int:
        """Returns the maximum defence roll for melee and ranged defence and TODO:magic defence"""
        effective_accuracy_level = cb.effective_accuracy_level(self.defence_current, self.style.defence_bonus,
                                                               self.defence_pot_bonus, defence_modifier)
        maximum_roll = cb.maximum_roll(effective_accuracy_level, self._defence_bonus_dictionary[damage_type],
                                       roll_modifier)
        return maximum_roll

    @property
    def defence_current(self) -> int:
        """Returns the current defence level, rounded up to the nearest integer"""
        return math.ceil(self._defence_current)

    @defence_current.setter
    def defence_current(self, value: Union[float, int]):
        """Sets the current defence level to a float or integer value"""
        self._defence_current = value

    def modify_defence_flat(self, amount: int):
        """Modifies defence by an amount: positive for increase, negative for decrease. Preserves float values"""
        unadjusted_defence = self._defence_current + amount
        adjusted_defence = max([0, unadjusted_defence])             # cannot be negative
        adjusted_defence = min([self.defence, adjusted_defence])    # cannot be greater than base defence

        self.defence_current = adjusted_defence

    def modify_defence_percent(self, modifier: cb.modifier_types):
        """Multiply the current defence by the modifier(s)"""
        self.defence_current = self._defence_current * modifier

    @property
    def hitpoints_current(self) -> int:
        """Returns the current amount of hitpoints"""
        return self._hitpoints_current

    @hitpoints_current.setter
    def hitpoints_current(self, value: int):
        """Sets the current hitpoints, a negative value will set to zero"""
        self._hitpoints_current = max([0, value])

    def damage(self, amount: int):
        """Reduces the current hitpoints by amount, cannot reduce below 0"""
        self.hitpoints_current = self.hitpoints_current - amount

    def heal(self, amount: int):
        """Increases the current hitpoints by amount, can exceed base level"""
        self.hitpoints_current = self.hitpoints_current + amount

    def alive(self) -> bool:
        """Returns True if hitpoints are greater than 0"""
        return not self.hitpoints_current == 0

    def neutralize_buff(self):
        """Returns all potion bonuses to the baseline, 0"""
        self.attack_pot_bonus = 0
        self.strength_pot_bonus = 0
        self.defence_pot_bonus = 0
        self.ranged_pot_bonus = 0
        self.magic_pot_bonus = 0


class NPC(Mob):

    def __init__(self, attack: int, strength: int, defence: int, ranged: int, magic: int, hitpoints: int,
                 defence_bonuses: tuple, style: Style, types: Union[str, List[str]] = None):

        attack_bonus_tuple = (0, 0, 0, 0, 0)
        defence_bonus_tuple = defence_bonuses
        strength_bonus_tuple = (0, 0, 0)

        super().__init__(attack, strength, defence, ranged, magic, hitpoints, attack_bonus_tuple, defence_bonus_tuple,
                         strength_bonus_tuple, style)

        if type(types) == str:
            self.types = [types]

        elif type(types) == list:
            self.types = types

        else:
            self.types = []

    def npc_maximum_defence_roll(self, damage_type: str) -> int:
        """Return the maximum defensive roll of an NPC"""
        modifier = 1

        return self.maximum_defence_roll(damage_type, modifier)

    def is_type(self, types: Union[str, List[str]]) -> bool:
        """Returns true if the NPC is all of the types passed to the function, false if it is not at least one"""
        if type(types) == str:
            types = [types]

        return all(t in self.types for t in types)


class Player(Mob):
    gear_dataframe = gear.get_gear_from_csv()
    maxed_stats = (99, 99, 99, 99, 99, 99, 99)

    def __init__(self, attack: int, strength: int, defence: int, ranged: int, magic: int, hitpoints: int, prayer: int,
                 gear_list: Union[str, List[str]], style: Style, prayers: Union[str, List[str]] = None,
                 overload: bool = True, slayer_task: bool = True):
        """Initialize a Player object with stats, gear, style, and optionally: prayers, overload, and slayer task

        Parameters:
            attack (int): Attack level
            strength (int): Strength level
            defence (int): Defence level
            ranged (int): Ranged level
            magic (int): Magic level
            hitpoints (int): Hitpoints level
            prayer (int): Prayer level
            gear_list (Union[str, List[str]]): A string or list of strings containing all of the equipped gear, for now
                                                the first item in the list must be the weapon
            style (Style): Style object containing information such as bonuses, damage type, and other modifiers
            prayers (Union[str, List[str]]): A string or list of strings with the names of prayers to activate
            overload (bool): If true, intitialize the player with an overload(+) boost
            slayer_task (bool): If true, the slayer helm (i) bonus can have an effect

        """

        self.prayer = prayer

        if type(gear_list) == str:
            gear_list = [gear_list]

        self.equipment_df, self.equipment_bonus = gear.gear_lookup(Player.gear_dataframe, gear_list)
        self.weapon_information = self.equipment_df.loc[gear_list[0]]

        self.special_accuracy_modifier = 1 + self.weapon_information['special accuracy']
        self.special_damage_modifier_1 = 1 + self.weapon_information['special damage 1']
        self.special_damage_modifier_2 = 1 + self.weapon_information['special damage 2']
        self.special_defence_roll = self.weapon_information['special defence roll']

        eb = self.equipment_bonus

        attack_bonus_stab = eb['stab attack']
        attack_bonus_slash = eb['slash attack']
        attack_bonus_crush = eb['crush attack']
        attack_bonus_ranged = eb['ranged attack']
        attack_bonus_magic = eb['magic attack']

        attack_bonus_tuple = (attack_bonus_stab, attack_bonus_slash, attack_bonus_crush, attack_bonus_ranged,
                              attack_bonus_magic)

        defence_bonus_stab = eb['stab defence']
        defence_bonus_slash = eb['slash defence']
        defence_bonus_crush = eb['crush defence']
        defence_bonus_ranged = eb['ranged defence']
        defence_bonus_magic = eb['magic defence']

        defence_bonus_tuple = (defence_bonus_stab, defence_bonus_slash, defence_bonus_crush, defence_bonus_ranged,
                               defence_bonus_magic)

        strength_bonus_melee = eb['melee strength']
        strength_bonus_ranged = eb['ranged strength']
        strength_bonus_magic = eb['magic damage']

        strength_bonus_tuple = (strength_bonus_melee, strength_bonus_ranged, strength_bonus_magic)

        self.prayer_bonus = eb['prayer']

        super().__init__(attack, strength, defence, ranged, magic, hitpoints, attack_bonus_tuple, defence_bonus_tuple,
                         strength_bonus_tuple, style)

        self.attack_speed = self.weapon_information['attack speed'] + self.style.attack_speed_modifier

        # initialize prayer bonuses
        self.prayer_modifier_attack = 1
        self.prayer_modifier_strength = 1
        self.prayer_modifier_defence = 1
        self.prayer_modifier_magical_defence = 1

        self._prayer_modifier_dict = {
            cb.attack: self.prayer_modifier_attack,
            cb.strength: self.prayer_modifier_strength,
            cb.defence: self.prayer_modifier_defence,
            cb.magical_defence: self.prayer_modifier_magical_defence
        }

        if prayers:
            self.pray(prayers)

        if overload:
            self.overload_plus()

        self.slayer_task = slayer_task

    def super_combat_potion(self):
        """Applies a super combat potion buff to the player's base stats"""
        bonuses = cb.potion_boost_super_combat(self.attack, self.strength, self.defence)
        self.attack_pot_bonus, self.strength_pot_bonus, self.defence_pot_bonus = bonuses

    def overload_plus(self):
        """Applies an overload(+) buff to the player's base stats"""
        bonuses = cb.potion_boost_overload_plus(self.attack, self.strength, self.defence, self.ranged, self.magic)
        self.attack_pot_bonus, self.strength_pot_bonus, self.defence_pot_bonus, self.ranged_pot_bonus, \
            self.magic_pot_bonus = bonuses

    def tick_down(self, n: int = None):
        """Reduces combat stats by n levels, down to the baseline. Default value is 1."""
        levels_down = n if n else 1

        def tick_pot(pot_bonus: int) -> int:
            return max([pot_bonus - levels_down, 0])

        self.attack_pot_bonus = tick_pot(self.attack_pot_bonus)
        self.strength_pot_bonus = tick_pot(self.strength_pot_bonus)
        self.defence_pot_bonus = tick_pot(self.defence_pot_bonus)
        self.ranged_pot_bonus = tick_pot(self.ranged_pot_bonus)
        self.magic_pot_bonus = tick_pot(self.magic_pot_bonus)

    def _reset_prayers(self):
        """Reset all prayer attack_strength_modifiers to base value, 1"""
        for key in self._prayer_modifier_dict.keys():
            self._prayer_modifier_dict[key] = 1

    def pray(self, prayers: Union[str, list]):
        if type(prayers) == str:
            prayers = [prayers]

        self._reset_prayers()

        for prayer in prayers:
            prayer_dict = cb.prayer_modifier_dict[prayer]

            for key, val in prayer_dict.items():
                if key == cb.attack:
                    self.prayer_modifier_attack *= val

                elif key == cb.strength:
                    self.prayer_modifier_strength *= val

                elif key == cb.defence:
                    self.prayer_modifier_defence *= val

                elif key == cb.magical_defence:
                    self.prayer_modifier_magical_defence *= val

                else:
                    raise Exception

    def wearing(self, items: Union[str, List[str]]):
        if type(items) == str:
            items = [items]

        wearing_items = True

        for item in items:
            try:
                self.equipment_df.loc[item]

            except KeyError:
                wearing_items = False
                break

        return wearing_items

    def void_modifier(self):
        """Returns an accuracy and damage modifier depending on the gear equipped and active style"""

        void_pieces = ['void knight helm', 'void knight top', 'void knight robe', 'void knight gloves']
        elite_void_pieces = void_pieces[:]
        elite_void_pieces[1:3] = ['elite void top', 'elite void robe']

        void_equipped = self.wearing(void_pieces)
        elite_void_equipped = self.wearing(elite_void_pieces)

        if void_equipped:
            attack_modifier = 0.1*((self.style.damage_type in cb.melee_damage_types) or
                                   (self.style.damage_type == cb.ranged)) \
                              + 0.45*(self.style.damage_type == cb.magic)
            strength_modifier = 0.1*((self.style.damage_type in cb.melee_damage_types) or
                                     (self.style.damage_type == cb.ranged))

        elif elite_void_equipped:
            attack_modifier = 0.1*((self.style.damage_type in cb.melee_damage_types) or
                                   (self.style.damage_type == cb.ranged)) \
                              + 0.45*(self.style.damage_type == cb.magic)
            strength_modifier = 0.1 * (self.style.damage_type in cb.melee_damage_types) \
                                + 0.125 * (self.style.damage_type == cb.ranged) \
                                + 0.025 * (self.style.damage_type == cb.magic)

        else:
            attack_modifier, strength_modifier = (0, 0)

        return 1 + attack_modifier, 1 + strength_modifier

    def slayer_modifier(self):
        """Returns the accuracy and damage modifier if the slay helm (i) is equipped and Player on task"""
        bonus = self.slayer_task and self.wearing('slayer helmet (i)') * \
                ((1/6)*(self.style.damage_type in cb.melee_damage_types) +
                 0.15*(self.style.damage_type == cb.ranged or self.style.damage_type == cb.magic))

        return 1 + bonus, 1 + bonus

    def salve_modifier(self, other: NPC):
        """Returns the accuracy and damage modifier if the salve amulet is equipped and the opponent is undead"""
        salve_i_equipped = self.wearing('salve (i)')
        salve_ei_equipped = self.wearing('salve (ei)')

        bonus = other.is_type(cb.undead)*(0.2*salve_ei_equipped + (1/6)*salve_i_equipped)

        return 1 + bonus, 1 + bonus

    def inquisitor_modifier(self):
        """Returns the accuracy and damage modifier provided from equipped inquisitor pieces and attack style"""
        damage_type = self.style.damage_type

        helm = self.wearing("inquisitor's great helm")
        chest = self.wearing("inquisitor's hauberk")
        legs = self.wearing("inquisitor's plateskirt")
        piece_bonus = 0.005

        set_effect = helm and chest and legs
        set_bonus = 0.01

        bonus = (damage_type == cb.crush)*(piece_bonus*(helm + chest + legs) + set_bonus*set_effect)
        return 1 + bonus, 1 + bonus

    def dragon_modifier(self, other: NPC):
        """Returns the attack and damage modifier provided from equipped weapon, attack style, opponent"""
        bonus = (other.is_type(cb.dragon)) * \
                (0.20*self.wearing('dragon hunter lance') + 0.30*self.wearing('dragon hunter crossbow'))

        return 1 + bonus, 1 + bonus

    def attack_strength_modifiers(self, other: NPC) -> Tuple[float, float]:
        """Handles logical consistency of modifiers and returns an attack and strength modifier tuple"""

        # Gear section
        # void and salve can both modify
        # salve has priority to slayer helmet
        # void and inquisitor do not function together (void is binary, inquisitor works w/ each piece though)
        void_attack_mod, void_strength_mod = self.void_modifier()
        slayer_attack_mod, slayer_strength_mod = self.slayer_modifier()
        salve_attack_mod, salve_strength_mod = self.salve_modifier(other)
        inquisitor_attack_mod, inquisitor_strength_mod = self.inquisitor_modifier()
        dragon_attack_mod, dragon_strength_mod = self.dragon_modifier(other)

        assert not (inquisitor_attack_mod == 1.025 and slayer_attack_mod > 1)
        assert not (slayer_attack_mod > 1 and void_attack_mod > 1)

        # salve bonus > slayer helm bonus
        priority_attack_mod = max(slayer_attack_mod, salve_attack_mod)
        priority_strength_mod = max(slayer_strength_mod, salve_strength_mod)

        gear_attack_mod = math.prod([void_attack_mod, priority_attack_mod, inquisitor_attack_mod, dragon_attack_mod])
        gear_strength_mod = math.prod([void_strength_mod, priority_strength_mod, inquisitor_strength_mod,
                                       dragon_strength_mod])

        # TODO: consider the way the wiki words dragonsbane items, test against in-game values, and see what's up

        # Prayer application
        attack_modifier = gear_attack_mod * self.prayer_modifier_attack
        strength_modifier = gear_strength_mod * self.prayer_modifier_strength

        assert attack_modifier >= 1 and strength_modifier >= 1

        return attack_modifier, strength_modifier

    def player_max_hit(self, other: NPC, special_modifier: cb.modifier_types = 1.00) -> int:
        """Returns the max hit a Player is capable of dealing with melee or ranged, given the gear and bonuses

        These bonuses are handled logically by the Player.attack_strength_modifiers function"""

        _, strength_modifier = self.attack_strength_modifiers(other)

        return self.max_hit(strength_modifier, special_modifier)

    def player_maximum_attack_roll(self, other: NPC, roll_modifier: cb.modifier_types = 1.00) -> int:
        """Returns the maximum attack roll (against an NPC) for melee, ranged, and TODO: magic attacks"""

        attack_modifier, _ = self.attack_strength_modifiers(other)

        return self.maximum_attack_roll(attack_modifier, roll_modifier)

    def attack_npc(self, other: NPC, special_attack: bool = False) -> DamageData:
        """Returns accuracy and max hit against an NPC, special attack assumed to be false by default"""
        if special_attack:
            attack_roll_modifier = self.special_accuracy_modifier
            damage_modifier = [self.special_damage_modifier_1, self.special_damage_modifier_2]
            damage_type_defence_roll = self.special_defence_roll

        else:
            attack_roll_modifier, damage_modifier = (1, 1)
            damage_type_defence_roll = self.style.damage_type

        attack_roll = self.player_maximum_attack_roll(other, attack_roll_modifier)
        defence_roll = other.npc_maximum_defence_roll(damage_type_defence_roll)
        accuracy = cb.accuracy(attack_roll, defence_roll)
        max_hit = self.player_max_hit(other, damage_modifier)
        attack_distribution = cb.hit_distribution(max_hit, accuracy)
        AttackDistribution = DamageData(attack_distribution, self.attack_speed, accuracy)

        return AttackDistribution

    def chinchompa(self, other: NPC, targets: int = 1, distance: int = None) -> DamageData:
        """Returns a DamageData object representing a chinchompa thrown at many NPCs"""
        assert isinstance(self.style, RangedStyle)
        maximum_targets = 11
        targets = min([maximum_targets, targets])

        if distance:
            mod_tuple = self.style.distance_modifier_tuple

            range_tuple = ((0 <= distance <= 3), (4 <= distance <= 6), (7 <= distance))
            attack_roll_modifier = float(np.dot(mod_tuple, range_tuple))

        else:
            attack_roll_modifier = 1

        damage_modifier = 1

        attack_roll = self.player_maximum_attack_roll(other, attack_roll_modifier)
        defence_roll = other.npc_maximum_defence_roll(cb.ranged)
        accuracy = cb.accuracy(attack_roll, defence_roll)
        max_hit = self.player_max_hit(other, damage_modifier)
        attack_distribution_given_hit = cb.hit_distribution(max_hit, prob_hit=1, num=targets)   # all or nothing distr.
        attack_distribution_modified = {}

        for key, val in attack_distribution_given_hit.items():
            attack_distribution_modified[key] = val * accuracy

        attack_distribution_modified[0] += 1 - accuracy
        ChinchompaAttack = DamageData(attack_distribution_modified, self.attack_speed, accuracy)

        return ChinchompaAttack

    def scythe_attack(self, other: NPC) -> DamageData:
        """Returns a distribution of scythe damage and probability values"""
        assert self.wearing('scythe of vitur')

        MainAttack = self.attack_npc(other)
        base_max_hit = MainAttack.max_hit
        accuracy = MainAttack.accuracy

        distributions = [MainAttack.damage_distribution]
        damage_modifiers = [0.5, 0.25]

        for modifier in damage_modifiers:
            distributions.append(cb.hit_distribution(math.floor(base_max_hit * modifier), accuracy))

        combined_distribution = convolution_list(distributions)
        ScytheAttack = DamageData(combined_distribution, self.attack_speed, 1 - (1 - accuracy)**len(distributions))

        return ScytheAttack

    def dharok_attack(self, other: NPC) -> DamageData:
        """Returns a distribution of scythe damage and probability values"""
        dharok_set = [
            "dharok's greataxe",
            "dharok's helm",
            "dharok's platebody",
            "dharok's platelegs"
        ]
        assert self.wearing(dharok_set)

        self.hitpoints_current = 1
        max_hit_scale_factor = 1 + ((self.hitpoints - self.hitpoints_current)/100 * (self.hitpoints / 100))

        attack_roll_modifier, damage_modifier = (1, max_hit_scale_factor)
        damage_type_defence_roll = self.style.damage_type

        attack_roll = self.player_maximum_attack_roll(other, attack_roll_modifier)
        defence_roll = other.npc_maximum_defence_roll(damage_type_defence_roll)
        accuracy = cb.accuracy(attack_roll, defence_roll)
        max_hit = self.player_max_hit(other, damage_modifier)
        attack_distribution = cb.hit_distribution(max_hit, accuracy)
        AttackDistribution = DamageData(attack_distribution, self.attack_speed, accuracy)

        return AttackDistribution

    def dharok_one_to_zero(self, other: NPC) -> DamageData:
        dharok_distribution = self.dharok_attack(other)
        dharok_distribution.attack_speed = 8
        return dharok_distribution



    def crossbow_distribution(self, other: NPC, style_bonus_attack: int, style_bonus_strength: int, pot_bonus: int,
                              attack_modifier: cb.modifier_types, strength_modifier: cb.modifier_types,
                              bolt_type: str, kandarin_hard_diary: bool = True) -> dict:
        """TODO: Make this work with the new styleReturns a crossbow damage/probability distribution

        TODO: implement the other bolts actually"""
        if bolt_type != 'ruby':
            raise Exception

        base_spec_chance, damage_modifier = cb.enchanted_bolts_spec_chance[bolt_type]

        spec_chance = base_spec_chance*(1 + kandarin_hard_diary*0.10)

        base_acc, base_max = self.attack_npc(other, style_bonus_attack, style_bonus_strength, pot_bonus, "ranged",
                                             attack_modifier, strength_modifier)

        spec_acc, _ = self.attack_npc(other, style_bonus_attack, style_bonus_strength, pot_bonus, "ranged",
                                             attack_modifier, strength_modifier, attack_roll_modifier=2)

        spec_acc = max([1*(bolt_type == "diamond"), spec_acc])

        ranged_visible = self.ranged + pot_bonus

        # modifies spec_max by flat % or % visible ranged level depending on bolt type
        spec_max = math.floor(base_max*(1 + damage_modifier*(bolt_type in cb.enchanted_bolts_flat_percent)) +
                                        ranged_visible*(bolt_type in cb.enchanted_bolts_percent_visible_ranged_level))

        spec_max = (bolt_type != 'ruby')*spec_max + (bolt_type == 'ruby')*min([math.floor(other.hitpoints_current*0.20),
                                                                               100])

        base_distribution = cb.hit_distribution(base_max, base_acc)

        for dmg, prob in base_distribution.items():
            base_distribution[dmg] = prob*(1-spec_chance)

        spec_distribution = {
            0: 1 - spec_acc,
            spec_max: spec_acc
        }

        for dmg, prob in spec_distribution.items():
            if dmg in base_distribution:
                base_distribution[dmg] += prob*spec_chance

            else:
                base_distribution[dmg] = prob*spec_chance

        prob_sum = sum(base_distribution.values())
        assert math.fabs(prob_sum - 1) < 1e10

        return base_distribution

# def spec_dragon_claws_npc(self, other: NPC, pot_bonus: int, attack_modifier: Union[float, list],
#                           strength_modifier: Union[float, list], special_modifier: Union[float, list] = 1.00):
#
#     style_bonus_attack = 0
#     style_bonus_strength = 3
#     damage_type = "slash"
#
#     p, base_max = self.attack_npc(other, style_bonus_attack, style_bonus_strength, pot_bonus,
#                                                   damage_type, attack_modifier, strength_modifier)
#
#     a = base_max + math.floor(base_max * 0.5) + 2*math.floor(math.floor(base_max * 0.5) * 0.5)
#     b = base_max + 2*math.floor(base_max * 0.5)
#     c = 2*math.floor(base_max * 0.75)
#     d = math.floor(base_max * 1.50)
#     e = 2
#
#     # mean_damage_per_hit

# def attack_npc_magic(self, other: NPC, style: int, pot_bonus, attack_modifier: Union[float, list],
#                       strength_modifier: Union[float, list]):
#     magic_accuracy = accuracy(self.maximum_magic_roll(style, pot_bonus, attack_modifier),
#                                other.maximum_defence_roll("magic"))
#     magic_max_hit = self.max_magic_hit(style, pot_bonus, strength_modifier)
#
#     return magic_accuracy, magic_max_hit
