from imports import *
from osrs_npc_lookup import olm_def_lookup
from osrs_classes import *
from markov import *
import osrs_markov
import osrs_gear as gear


PlayerBGS = Player(*Player.maxed_stats, gear_list=gear.presets['bgs'],
                   style=MeleeStyle('aggressive', cb.slash, cb.strength), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerDWH = Player(*Player.maxed_stats, gear_list=gear.presets['dwh (bandos)'],
                   style=MeleeStyle('accurate', cb.crush, cb.attack), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerScythe = Player(*Player.maxed_stats, gear_list=gear.presets['scythe (bandos)'],
                   style=MeleeStyle('chop', cb.slash, cb.strength), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerLance = Player(*Player.maxed_stats, gear_list=gear.presets['dhl'],
                     style=MeleeStyle('lunge', cb.stab, cb.shared), prayers=cb.piety, overload=True,
                     slayer_task=False)


def defence_reduction_calculations():
    base_def_lvl, def_bonus_stab, def_bonus_slash, def_bonus_crush = olm_def_lookup(team_scale=5, challenge_mode=False)
    GreatOlm = NPC(295, 295, base_def_lvl, 295, 206, 1800, (def_bonus_stab, def_bonus_slash, def_bonus_crush, 50, 50),
                   style=NPCStyle(cb.ranged), types=cb.dragon)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    SpecDWH = PlayerDWH.attack_npc(GreatOlm, special_attack=True)

    max_hit_bgs = SpecBGS.max_hit
    max_hit_dwh = SpecDWH.max_hit

    bgs_defence_range_accuracy = np.zeros(shape=GreatOlm.defence + 1)
    dwh_defence_range_chance_to_land = np.zeros(shape=GreatOlm.defence + 1)

    for dl in range(GreatOlm.defence + 1):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWH.attack_npc(GreatOlm, special_attack=True).chance_to_damage

    Q_dwh, R_dwh = osrs_markov.dwh_transition_matrix_generator(GreatOlm.defence, dwh_defence_range_chance_to_land)
    Q_bgs, R_bgs = osrs_markov.bgs_transition_matrix_generator(GreatOlm.defence, max_hit_bgs,
                                                               bgs_defence_range_accuracy)

    defence_states = np.arange(GreatOlm.defence, -1, -1)
    DWHMarkovChain = AbsorbingMarkovChain(Q_dwh, R_dwh, defence_states)
    BGSMarkovChain = AbsorbingMarkovChain(Q_bgs, R_bgs, defence_states)

    starting_probability_distribution = np.zeros(shape=defence_states.shape)
    starting_probability_distribution[0] = 1

    num_specs = 4
    spec_arrangements = [(i, num_specs - i) for i in range(num_specs + 1)]
    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    fig, axes = plt.subplots(num_specs+1, num_specs+1, sharex=True, sharey=True)
    title_string = '{:d} DWH, {:d} BGS, AVG DEF = {:.1f}'
    defence_space = np.zeros(shape=(num_specs+1, num_specs+1))
    distribution_space = np.zeros(shape=(num_specs+1, num_specs+1, len(defence_states)))

    for num_dwh in range(num_specs+1):
        GreatOlm.defence_current = GreatOlm.defence
        current_probability_distribution = starting_probability_distribution.copy()

        current_probability_distribution = DWHMarkovChain.probability_distribution(current_probability_distribution,
                                                                                   num_dwh)

        for num_bgs in range(num_specs+1):
            current_probability_distribution = BGSMarkovChain.probability_distribution(current_probability_distribution,
                                                                                       num_bgs)

            distribution_space[num_dwh, num_bgs, :] = current_probability_distribution
            defence_space[num_dwh, num_bgs] = BGSMarkovChain.mean_state(current_probability_distribution)

            ax = axes[num_dwh, num_bgs]
            ax.set(xlabel="Reduced defence level")
            ax.set(ylabel="Probability mass, P(Def=X)")
            ax.set_title(title_string.format(num_dwh, num_bgs, defence_space[num_dwh, num_bgs]))
            ax.vlines(defence_states, 0, distribution_space[num_dwh, num_bgs, :])

    plt.show()

    fig2 = plt.subplot()
    plt.xlabel("Reduced defence level")
    plt.ylabel("Probability mass, P(Def=X)")
    plt.title('{:d} spec weapons distributions'.format(num_specs))
    plt.legend(spec_arrangements)

    for (num_dwh, num_bgs), color in zip(spec_arrangements, colors):
        # plt.vlines(defence_states, 0, distribution_space[num_dwh, num_bgs, :], colors=color)
        plt.plot(defence_states, distribution_space[num_dwh, num_bgs, :], color=color)

    plt.show()


def kill_time_simple_method(trials: Union[float, int]):
    trials = int(trials)

    base_def_lvl, def_bonus_stab, def_bonus_slash, def_bonus_crush = olm_def_lookup(team_scale=5, challenge_mode=False)
    GreatOlm = NPC(295, 295, base_def_lvl, 295, 206, 1800, (def_bonus_stab, def_bonus_slash, def_bonus_crush, 50, 50),
                   style=NPCStyle(cb.ranged), types=cb.dragon)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    SpecDWH = PlayerDWH.attack_npc(GreatOlm, special_attack=True)
    AttackScythe = PlayerScythe.scythe_attack(GreatOlm)

    bgs_defence_range_accuracy = np.zeros(shape=GreatOlm.defence + 1)
    dwh_defence_range_chance_to_land = np.zeros(shape=GreatOlm.defence + 1)

    BGS_spec_dmg_array, _ = SpecBGS.damage_distribution_array_pair()
    DWH_spec_dmg_array, _ = SpecDWH.damage_distribution_array_pair()
    Scythe_dmg_array, _ = AttackScythe.damage_distribution_array_pair()

    BGS_spec_prob_array = np.empty(shape=(GreatOlm.defence + 1, len(BGS_spec_dmg_array)))
    DWH_spec_prob_array = np.empty(shape=(GreatOlm.defence + 1, len(DWH_spec_dmg_array)))
    Scythe_prob_array = np.empty(shape=(GreatOlm.defence + 1, len(Scythe_dmg_array)))

    for dl in range(GreatOlm.defence + 1):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        _, BGS_spec_prob_array[dl, :] = PlayerBGS.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, DWH_spec_prob_array[dl, :] = PlayerDWH.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, Scythe_prob_array[dl, :] = PlayerScythe.scythe_attack(GreatOlm).damage_distribution_array_pair()

        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWH.attack_npc(GreatOlm, special_attack=True).chance_to_damage

    Q_dwh, R_dwh, dwh_states = osrs_markov.dwh_transition_matrix_generator_compact(GreatOlm.defence,
                                                                                   dwh_defence_range_chance_to_land)
    DWHMarkovChain = AbsorbingMarkovChain(Q_dwh, R_dwh, dwh_states)

    Q_bgs, R_bgs = osrs_markov.bgs_transition_matrix_generator(GreatOlm.defence, SpecBGS.max_hit,
                                                               bgs_defence_range_accuracy)
    bgs_states = np.arange(GreatOlm.defence, -1, -1)
    BGSMarkovChain = AbsorbingMarkovChain(Q_bgs, R_bgs, bgs_states)

    num_specs = 4
    spec_arrangements = [(i, num_specs - i) for i in range(num_specs + 1)]
    ticks = np.ndarray(shape=(len(spec_arrangements), trials))
    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    tic = time.time()

    for index, (num_dwh, num_bgs) in enumerate(spec_arrangements):

        for trial in range(trials):
            GreatOlm.hitpoints_current = GreatOlm.hitpoints
            GreatOlm.defence_current = GreatOlm.defence
            tick = 0

            for i in range(num_dwh):
                if damage := random.choices(DWH_spec_dmg_array, DWH_spec_prob_array[GreatOlm.defence_current, :])[0]:
                    GreatOlm.modify_defence_percent(0.7)
                    GreatOlm.damage(damage)

            for i in range(num_bgs):
                damage = random.choices(BGS_spec_dmg_array, BGS_spec_prob_array[GreatOlm.defence_current, :])[0]
                GreatOlm.modify_defence_flat(-damage)
                GreatOlm.damage(damage)

            tick += num_dwh*PlayerDWH.attack_speed + num_bgs*PlayerBGS.attack_speed

            while GreatOlm.alive():
                GreatOlm.damage(random.choices(Scythe_dmg_array, Scythe_prob_array[GreatOlm.defence_current, :])[0])
                tick += PlayerScythe.attack_speed

            ticks[index, trial] = tick

    mean_ticks = np.asarray([np.mean(ticks[index, :]) for index in range(len(spec_arrangements))])

    for sa, mt in zip(spec_arrangements, mean_ticks):
        print(sa, mt)

    toc = time.time()

    print(toc - tic)


def kill_time_variable_dwh_bgs(trials: Union[float, int]):
    trials = int(trials)

    base_def_lvl, def_bonus_stab, def_bonus_slash, def_bonus_crush = olm_def_lookup(team_scale=5, challenge_mode=False)
    GreatOlm = NPC(295, 295, base_def_lvl, 295, 206, 1800, (def_bonus_stab, def_bonus_slash, def_bonus_crush, 50, 50),
                   style=NPCStyle(cb.ranged), types=cb.dragon)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    SpecDWH = PlayerDWH.attack_npc(GreatOlm, special_attack=True)
    AttackScythe = PlayerScythe.scythe_attack(GreatOlm)

    bgs_defence_range_accuracy = np.zeros(shape=GreatOlm.defence + 1)
    dwh_defence_range_chance_to_land = np.zeros(shape=GreatOlm.defence + 1)

    BGS_spec_dmg_array, _ = SpecBGS.damage_distribution_array_pair()
    DWH_spec_dmg_array, _ = SpecDWH.damage_distribution_array_pair()
    Scythe_dmg_array, _ = AttackScythe.damage_distribution_array_pair()

    BGS_spec_prob_array = np.empty(shape=(GreatOlm.defence+1, len(BGS_spec_dmg_array)))
    DWH_spec_prob_array = np.empty(shape=(GreatOlm.defence+1, len(DWH_spec_dmg_array)))
    Scythe_prob_array = np.empty(shape=(GreatOlm.defence+1, len(Scythe_dmg_array)))

    for dl in range(GreatOlm.defence + 1):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        _, BGS_spec_prob_array[dl, :] = PlayerBGS.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, DWH_spec_prob_array[dl, :] = PlayerDWH.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, Scythe_prob_array[dl, :] = PlayerScythe.scythe_attack(GreatOlm).damage_distribution_array_pair()

        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWH.attack_npc(GreatOlm, special_attack=True).chance_to_damage

    Q_dwh, R_dwh, dwh_states = osrs_markov.dwh_transition_matrix_generator_compact(GreatOlm.defence,
                                                                       dwh_defence_range_chance_to_land)
    DWHMarkovChain = AbsorbingMarkovChain(Q_dwh, R_dwh, dwh_states)

    Q_bgs, R_bgs = osrs_markov.bgs_transition_matrix_generator(GreatOlm.defence, SpecBGS.max_hit,
                                                               bgs_defence_range_accuracy)
    bgs_states = np.arange(GreatOlm.defence, -1, -1)
    BGSMarkovChain = AbsorbingMarkovChain(Q_bgs, R_bgs, bgs_states)

    # logic sandbox
    # 3 specs: 1, 1, 1
    # 4 specs: 2, 1, 1
    # 5 specs: 2, 1, 2

    num_dwh, num_bgs, num_var = (1, 1, 2)
    num_specs = sum([num_dwh, num_bgs, num_var])

    tic = time.time()
    ticks = np.zeros(shape=trials)

    for trial in range(trials):
        GreatOlm.hitpoints_current = GreatOlm.hitpoints
        GreatOlm.defence_current = GreatOlm.defence
        tick = 0

        dwh_lands = 0

        for i in range(num_dwh):
            tick += PlayerDWH.attack_speed

            if damage := random.choices(DWH_spec_dmg_array, DWH_spec_prob_array[GreatOlm.defence_current, :])[0]:
                dwh_lands += 1
                GreatOlm.modify_defence_percent(0.7)
                GreatOlm.damage(damage)

        for i in range(num_var):

            if damage := dwh_lands < 2 and random.choices(DWH_spec_dmg_array,
                                                          DWH_spec_prob_array[GreatOlm.defence_current, :])[0]:
                dwh_lands += 1
                tick += PlayerDWH.attack_speed
                GreatOlm.modify_defence_percent(0.7)
                GreatOlm.damage(damage)

            else:
                tick += PlayerBGS.attack_speed
                damage = random.choices(BGS_spec_dmg_array, BGS_spec_prob_array[GreatOlm.defence_current, :])[0]
                GreatOlm.modify_defence_flat(-damage)
                GreatOlm.damage(damage)

        for i in range(num_bgs):
            tick += PlayerBGS.attack_speed
            damage = random.choices(BGS_spec_dmg_array, BGS_spec_prob_array[GreatOlm.defence_current, :])[0]
            GreatOlm.modify_defence_flat(-damage)
            GreatOlm.damage(damage)

        while GreatOlm.alive():
            GreatOlm.damage(random.choices(Scythe_dmg_array, Scythe_prob_array[GreatOlm.defence_current, :])[0])
            tick += PlayerScythe.attack_speed

        ticks[trial] = tick

    mean_ticks = np.mean(ticks)
    info_string = '{:d} DWH, {:d} Fill DWH, {:d} BGS, Avg kill ticks = {:.1f}'
    print(info_string.format(num_dwh, num_var, num_bgs, mean_ticks))

    toc = time.time()

    print(toc - tic)


if __name__ == '__main__':
    # defence_reduction_calculations()
    # kill_time_simple_method(trials=1e4)
    kill_time_variable_dwh_bgs(trials=1e6)

