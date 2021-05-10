from imports import *
from osrs_npc_lookup import olm_def_lookup
from osrs_classes import *
from bedevere.markov import *
import osrs_markov
import osrs_gear as gear
import osrs_npc_lookup as npc
from mpl_toolkits.mplot3d import Axes3D


PlayerBGS = Player(*Player.maxed_stats, gear_list=gear.presets['bgs'],
                   style=MeleeStyle(cb.aggressive, cb.slash, cb.strength), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerDWH = Player(*Player.maxed_stats, gear_list=gear.presets['dwh (bandos diary)'],
                   style=MeleeStyle(cb.accurate, cb.crush, cb.attack), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerDWHInquisitor = Player(*Player.maxed_stats, gear_list=gear.presets['dwh (inquisitor)'],
                             style=MeleeStyle(cb.accurate, cb.crush, cb.attack), prayers=cb.piety, overload=True,
                             slayer_task=False)

PlayerScythe = Player(*Player.maxed_stats, gear_list=gear.presets['scythe (bandos)'],
                   style=MeleeStyle(cb.chop, cb.slash, cb.strength), prayers=cb.piety, overload=True,
                   slayer_task=False)

PlayerScytheInquisitor = Player(*Player.maxed_stats, gear_list=gear.presets['scythe (inquisitor)'],
                                style=MeleeStyle(cb.jab, cb.crush, cb.strength), prayers=cb.piety, overload=True,
                                slayer_task=False)

PlayerScytheInquisitorChop = Player(*Player.maxed_stats, gear_list=gear.presets['scythe (inquisitor)'],
                                    style=MeleeStyle(cb.chop, cb.slash, cb.strength), prayers=cb.piety, overload=True,
                                    slayer_task=False)

PlayerLance = Player(*Player.maxed_stats, gear_list=gear.presets['dhl'],
                     style=MeleeStyle(cb.lunge, cb.stab, cb.shared), prayers=cb.piety, overload=True,
                     slayer_task=False)

PlayerLanceInquisitor = Player(*Player.maxed_stats, gear_list=gear.presets['dhl_inq'],
                               style=MeleeStyle(cb.pound, cb.crush, cb.shared), prayers=cb.piety, overload=True,
                               slayer_task=False)

PlayerDharok = Player(*Player.maxed_stats, gear_list=gear.presets['dharok'],
                      style=MeleeStyle(cb.hack, cb.slash, cb.strength), prayers=cb.piety, overload=True,
                      slayer_task=False)

PlayerDharokBGS = Player(*Player.maxed_stats, gear_list=gear.presets['dharok_bgs'],
                         style=MeleeStyle(cb.aggressive, cb.slash, cb.strength), prayers=cb.piety, overload=True,
                         slayer_task=False)

PlayerDharokDWH = Player(*Player.maxed_stats, gear_list=gear.presets['dharok_dwh'],
                         style=MeleeStyle(cb.accurate, cb.crush, cb.attack), prayers=cb.piety, overload=True,
                         slayer_task=False)


def blaze_king_melee_hand(trials: Union[float, int]):
    bins = math.floor(trials**(1/3))
    kill_times_list = []
    specials_used_list = []
    scale = 100
    MeleeHand = npc.olm_melee_hand(team_scale=scale, challenge_mode=False)
    MeleeHand.defence_current = 0

    dharok_dmg_ary, dharok_prb_ary = PlayerDharok.dharok_one_to_zero(MeleeHand).damage_distribution_array_pair()

    for trial in range(int(trials)):
        tick = 0    # refresh olm object, start timer
        MeleeHand.defence_current = MeleeHand.defence
        MeleeHand.hitpoints_current = MeleeHand.hitpoints

        dwh_hits_landed = 0
        dwh_hits_target = 3
        bgs_damage_dealt = 0
        bgs_damage_target = 75
        specials_used = 0

        while dwh_hits_landed < dwh_hits_target:
            dmg_ary, prb_ary = PlayerDharokDWH.attack_npc(MeleeHand, special_attack=True).damage_distribution_array_pair()
            damage = random.choices(dmg_ary, prb_ary)[0]
            tick += PlayerDharokDWH.attack_speed
            specials_used += 1

            if damage > 0:
                MeleeHand.modify_defence_percent(0.7)
                MeleeHand.damage(damage)
                dwh_hits_landed += 1

        while bgs_damage_dealt < bgs_damage_target:
            dmg_ary, prb_ary = PlayerDharokBGS.\
                attack_npc(MeleeHand, special_attack=True).damage_distribution_array_pair()
            damage = random.choices(dmg_ary, prb_ary)[0]
            tick += PlayerDharokBGS.attack_speed
            specials_used += 1

            if damage > 0:
                MeleeHand.modify_defence_flat(-1 * damage)
                MeleeHand.damage(damage)
                bgs_damage_dealt += damage

        while MeleeHand.alive():
            damage = random.choices(dharok_dmg_ary, dharok_prb_ary)[0]
            tick += 8   # one to zero
            MeleeHand.damage(damage)

        kill_times_list.append(tick)
        specials_used_list.append(specials_used)

    kill_times_ary = np.asarray(kill_times_list)
    specials_used_ary = np.asarray(specials_used_list)

    mean_kill_time = np.mean(kill_times_ary)
    mean_specs_used = np.mean(specials_used_ary)
    print("Mean kill time:\n\t{:5.0f}\tticks\n\t{:5.0f}\tminutes".format(mean_kill_time, mean_kill_time/100))
    print("Mean specs used to reach 0 defence:\n\t{:5.0f}\tspecs".format(mean_specs_used))

    plt.hist(kill_times_ary, bins=bins)
    plt.show()

    plt.hist(specials_used_ary, bins=list(range(specials_used_ary.min(), specials_used_ary.max())))
    plt.show()


def defence_reduction_calculations(scale, specs=None):
    GreatOlm = npc.olm_melee_hand(team_scale=scale, challenge_mode=False)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    # SpecDWH = PlayerDWHInquisitor.attack_npc(GreatOlm, special_attack=True)

    max_hit_bgs = SpecBGS.max_hit
    # max_hit_dwh = SpecDWH.max_hit

    bgs_defence_range_accuracy = np.zeros(shape=GreatOlm.defence + 1)
    dwh_defence_range_chance_to_land = np.zeros(shape=GreatOlm.defence + 1)

    for dl in range(GreatOlm.defence + 1):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWHInquisitor.attack_npc(GreatOlm,
                                                                              special_attack=True).chance_to_damage

    Q_dwh, R_dwh = osrs_markov.dwh_transition_matrix_generator(GreatOlm.defence, dwh_defence_range_chance_to_land)
    Q_bgs, R_bgs = osrs_markov.bgs_transition_matrix_generator(GreatOlm.defence, max_hit_bgs,
                                                               bgs_defence_range_accuracy)

    defence_states = np.arange(GreatOlm.defence, -1, -1)
    DWHMarkovChain = AbsorbingMarkovChain(Q_dwh, R_dwh, defence_states)
    BGSMarkovChain = AbsorbingMarkovChain(Q_bgs, R_bgs, defence_states)

    starting_probability_distribution = np.zeros(shape=defence_states.shape)
    starting_probability_distribution[0] = 1

    num_specs = specs if specs else scale
    spec_arrangements = [(i, num_specs - i) for i in range(num_specs + 1)]
    # colors = ['r', 'g', 'b', 'c', 'm', 'y']

    fig, axes = plt.subplots(num_specs+1, num_specs+1, sharex=True, sharey=True)
    title_string = '{:d}D, {:d}B, AVGDEF={:.1f}'
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
            # ax.set(xlabel="Reduced defence level")
            # ax.set(ylabel="Probability mass, P(Def=X)")
            ax.set_title(title_string.format(num_dwh, num_bgs, defence_space[num_dwh, num_bgs]))
            ax.vlines(defence_states, 0, distribution_space[num_dwh, num_bgs, :])

    plt.show()

    fig2 = plt.subplot()
    #plt.xlabel("Reduced defence level")
    #plt.ylabel("Probability mass, P(Def=X)")
    # plt.title('{:d} spec weapons distributions (num dwh, num bgs)'.format(num_specs))
    # plt.title('{:d} DWH {:d} BGS'.format(num_specs))

    # for (num_dwh, num_bgs), color in zip(spec_arrangements, colors):
    for num_dwh, num_bgs in spec_arrangements:
        plt.vlines(defence_states, 0, distribution_space[num_dwh, num_bgs, :])
        plt.plot(defence_states, distribution_space[num_dwh, num_bgs, :])

    plt.legend(spec_arrangements)
    plt.show()

    for num_dwh, num_bgs in spec_arrangements:
        plt.plot(defence_states, distribution_space[num_dwh, num_bgs, :])

    plt.legend(spec_arrangements)
    plt.show()


# def special_attack_distribution(player: Player, other: NPC):
#     spec = player.attack_npc(other, special_attack=True)
#     defence_range_accuracy = np.zeros(shape=other.defence + 1)
#     spec_damage_array, _ = spec.damage_distribution_array_pair()
#     spec_prob_array = np.empty(shape=(other.defence+1, len(spec_damage_array)))
#
#     for dl in range(other.defence + 1):
#         other.defence_current = dl
#         _, spec_prob_array[dl, :] = player.attack_npc(other, special_attack=True).damage_distribution_array_pair()


def kill_time_simple_method(trials: Union[float, int], num_specs: int, team_scale: int = None,
                            challenge_mode: bool = False):
    trials = int(trials)

    if not team_scale:
        team_scale = num_specs

    GreatOlm = npc.olm_melee_hand(team_scale, challenge_mode)

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

    spec_arrangements = [(i, num_specs - i) for i in range(num_specs + 1)]
    ticks = np.ndarray(shape=(len(spec_arrangements), trials))
    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    tic = time.time()

    ticks_def = {}

    for dl in range(GreatOlm.defence + 1):
        ticks_def[dl] = []

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
            dl = GreatOlm.defence_current

            while GreatOlm.alive():
                GreatOlm.damage(random.choices(Scythe_dmg_array, Scythe_prob_array[dl, :])[0])
                tick += PlayerScythe.attack_speed

            ticks[index, trial] = tick
            ticks_def[GreatOlm.defence_current].append(tick)

        min_ticks = int(ticks[index, :].min())
        max_ticks = int(ticks[index, :].max())
        x = np.arange(GreatOlm.defence + 1)
        y = np.arange(min_ticks, max_ticks + 1)
        xv, yv = np.meshgrid(x, y)
        z = np.ndarray(x.size * y.size)

        for sub_index, (xi, yi) in enumerate(zip(xv.flat, yv.flat)):
            counter = Counter(ticks_def[xi])
            z[sub_index] = counter[yi] / trials if yi in counter.keys() else np.nan

        zv = z.reshape(xv.shape)

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.scatter(xv, yv, zv)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()

    mean_ticks = np.asarray([np.mean(ticks[index, :]) for index in range(len(spec_arrangements))])
    plot_tuples = []

    min_ticks = int(ticks.min())
    max_ticks = int(ticks.max())
    x = np.arange(GreatOlm.defence + 1)
    y = np.arange(min_ticks, max_ticks + 1)
    xv, yv = np.meshgrid(x, y)
    z = np.ndarray(x.size * y.size)

    for index, (xi, yi) in enumerate(zip(xv.flat, yv.flat)):
        counter = Counter(ticks_def[xi])
        z[index] = counter[yi]/trials if yi in counter.keys() else np.nan

    zv = z.reshape(xv.shape)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.scatter(xv, yv, zv)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()

    for sa, mt in zip(spec_arrangements, mean_ticks):
        print(sa, mt)

    toc = time.time()


def kill_time_variable_dwh_bgs(trials: Union[float, int], num_dwh: int, num_bgs: int, num_var: int,
                               team_scale: int = None, challenge_mode: bool = False):
    trials = int(trials)

    if not team_scale:
        team_scale = sum([num_dwh, num_bgs, num_var])

    GreatOlm = npc.olm_melee_hand(team_scale=team_scale, challenge_mode=challenge_mode)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    SpecDWH = PlayerDWH.attack_npc(GreatOlm, special_attack=True)
    AttackScythe = PlayerScythe.scythe_attack(GreatOlm)
    AttackLance = PlayerLance.attack_npc(GreatOlm)

    bgs_defence_range_accuracy = np.zeros(shape=GreatOlm.defence + 1)
    dwh_defence_range_chance_to_land = np.zeros(shape=GreatOlm.defence + 1)

    BGS_spec_dmg_array, _ = SpecBGS.damage_distribution_array_pair()
    DWH_spec_dmg_array, _ = SpecDWH.damage_distribution_array_pair()
    Scythe_dmg_array, _ = AttackScythe.damage_distribution_array_pair()
    Lance_dmg_array, _ = AttackLance.damage_distribution_array_pair()

    BGS_spec_prob_array = np.empty(shape=(GreatOlm.defence+1, len(BGS_spec_dmg_array)))
    DWH_spec_prob_array = np.empty(shape=(GreatOlm.defence+1, len(DWH_spec_dmg_array)))
    Scythe_prob_array = np.empty(shape=(GreatOlm.defence+1, len(Scythe_dmg_array)))
    Lance_prob_array = np.empty(shape=(GreatOlm.defence+1, len(Lance_dmg_array)))

    for dl in range(GreatOlm.defence + 1):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        _, BGS_spec_prob_array[dl, :] = PlayerBGS.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, DWH_spec_prob_array[dl, :] = PlayerDWH.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, Scythe_prob_array[dl, :] = PlayerScythe.scythe_attack(GreatOlm).damage_distribution_array_pair()
        _, Lance_prob_array[dl, :] = PlayerLance.attack_npc(GreatOlm).damage_distribution_array_pair()

        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWH.attack_npc(GreatOlm, special_attack=True).chance_to_damage

    Q_dwh, R_dwh, dwh_states = osrs_markov.dwh_transition_matrix_generator_compact(GreatOlm.defence,
                                                                       dwh_defence_range_chance_to_land)
    DWHMarkovChain = AbsorbingMarkovChain(Q_dwh, R_dwh, dwh_states)

    Q_bgs, R_bgs = osrs_markov.bgs_transition_matrix_generator(GreatOlm.defence, SpecBGS.max_hit,
                                                               bgs_defence_range_accuracy)
    bgs_states = np.arange(GreatOlm.defence, -1, -1)
    BGSMarkovChain = AbsorbingMarkovChain(Q_bgs, R_bgs, bgs_states)

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

            if dwh_lands < 2:
                if damage := random.choices(DWH_spec_dmg_array, DWH_spec_prob_array[GreatOlm.defence_current, :])[0]:
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

    return ticks


def kill_time_mixed_inquisitor(trials: Union[float, int], num_specs: int, team_scale: int = None,
                            challenge_mode: bool = False):
    trials = int(trials)

    if not team_scale:
        team_scale = num_specs

    base_def_lvl, def_bonus_stab, def_bonus_slash, def_bonus_crush = olm_def_lookup(team_scale=team_scale,
                                                                                    challenge_mode=challenge_mode)
    GreatOlm = NPC(295, 295, base_def_lvl, 295, 206, 1800, (def_bonus_stab, def_bonus_slash, def_bonus_crush, 50, 50),
                   style=NPCStyle(cb.ranged), types=cb.dragon)

    SpecBGS = PlayerBGS.attack_npc(GreatOlm, special_attack=True)
    SpecDWH = PlayerDWH.attack_npc(GreatOlm, special_attack=True)
    SpecDWHInquisitor = PlayerDWHInquisitor.attack_npc(GreatOlm, special_attack=True)
    AttackScythe = PlayerScythe.scythe_attack(GreatOlm)
    AttackScytheInquisitor = PlayerScytheInquisitor.scythe_attack(GreatOlm)
    AttackScytheInquisitorChop = PlayerScytheInquisitorChop.scythe_attack(GreatOlm)

    m = GreatOlm.defence + 1

    bgs_defence_range_accuracy = np.zeros(shape=m)
    dwh_defence_range_chance_to_land = np.zeros(shape=m)
    dwh_inq_defence_range_chance_to_land = np.zeros(shape=m)

    BGS_spec_dmg_array, _ = SpecBGS.damage_distribution_array_pair()
    DWH_spec_dmg_array, _ = SpecDWH.damage_distribution_array_pair()
    DWH_Inq_spec_dmg_array, _ = SpecDWHInquisitor.damage_distribution_array_pair()
    Scythe_dmg_array, _ = AttackScythe.damage_distribution_array_pair()
    Scythe_Inq_dmg_array, _ = AttackScytheInquisitor.damage_distribution_array_pair()
    Scythe_Inq_chop_dmg_array, _ = AttackScytheInquisitorChop.damage_distribution_array_pair()

    BGS_spec_prob_array = np.empty(shape=(m, len(BGS_spec_dmg_array)))
    DWH_spec_prob_array = np.empty(shape=(m, len(DWH_spec_dmg_array)))
    DWH_Inq_spec_prob_array = np.empty(shape=(m, len(DWH_Inq_spec_dmg_array)))
    Scythe_prob_array = np.empty(shape=(m, len(Scythe_dmg_array)))
    Scythe_Inq_prob_array = np.empty(shape=(m, len(Scythe_Inq_dmg_array)))
    Scythe_Inq_chop_prob_array = np.empty(shape=(m, len(Scythe_Inq_chop_dmg_array)))

    for dl in range(m):  # pre-generate accuracy rolls from 0 back to initial defence
        GreatOlm.defence_current = dl
        _, BGS_spec_prob_array[dl, :] = PlayerBGS.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, DWH_spec_prob_array[dl, :] = PlayerDWH.attack_npc(GreatOlm,
                                                             special_attack=True).damage_distribution_array_pair()
        _, DWH_Inq_spec_prob_array[dl, :] = PlayerDWHInquisitor.attack_npc(GreatOlm, special_attack=True)\
            .damage_distribution_array_pair()
        _, Scythe_prob_array[dl, :] = PlayerScythe.scythe_attack(GreatOlm).damage_distribution_array_pair()
        _, Scythe_Inq_prob_array[dl, :] = PlayerScytheInquisitor.scythe_attack(GreatOlm)\
            .damage_distribution_array_pair()
        _, Scythe_Inq_chop_prob_array[dl, :] = PlayerScytheInquisitorChop.scythe_attack(GreatOlm)\
            .damage_distribution_array_pair()

        bgs_defence_range_accuracy[dl] = PlayerBGS.attack_npc(GreatOlm, special_attack=True).accuracy
        dwh_defence_range_chance_to_land[dl] = PlayerDWH.attack_npc(GreatOlm, special_attack=True).chance_to_damage

    num_dwh, num_bgs = (2, 2)
    ticks = np.ndarray(shape=(num_dwh + 1, trials))
    colors = ['r', 'g', 'b', 'c', 'm', 'y']
    tic = time.time()

    for num_dwh_inq in range(num_dwh + 1):

        for trial in range(trials):
            GreatOlm.hitpoints_current = GreatOlm.hitpoints
            GreatOlm.defence_current = GreatOlm.defence
            tick = 0

            dwh_pid_order = random.sample(range(num_dwh), num_dwh)

            for pid in dwh_pid_order:

                if pid < num_dwh_inq:
                    if damage := random.choices(DWH_Inq_spec_dmg_array,
                                                DWH_Inq_spec_prob_array[GreatOlm.defence_current, :])[0]:
                        GreatOlm.modify_defence_percent(0.7)
                        GreatOlm.damage(damage)

                else:
                    if damage := random.choices(DWH_spec_dmg_array,
                                                DWH_spec_prob_array[GreatOlm.defence_current, :])[0]:
                        GreatOlm.modify_defence_percent(0.7)
                        GreatOlm.damage(damage)

            for i in range(num_bgs):
                damage = random.choices(BGS_spec_dmg_array, BGS_spec_prob_array[GreatOlm.defence_current, :])[0]
                GreatOlm.modify_defence_flat(-damage)
                GreatOlm.damage(damage)

            tick += num_dwh*PlayerDWH.attack_speed + num_bgs*PlayerBGS.attack_speed
            jab_defence_level_maximum = 19

            while GreatOlm.alive():
                pid_order = random.sample(range(num_dwh + num_bgs), num_dwh + num_bgs)

                for pid in pid_order:
                    tick += PlayerScythe.attack_speed

                    if pid < num_dwh_inq:

                        if GreatOlm.defence_current <= jab_defence_level_maximum:
                            GreatOlm.damage(random.choices(Scythe_Inq_dmg_array,
                                                           Scythe_Inq_prob_array[GreatOlm.defence_current, :])[0])

                        else:
                            GreatOlm.damage(random.choices(Scythe_Inq_chop_dmg_array,
                                                           Scythe_Inq_chop_prob_array[GreatOlm.defence_current, :])[0])

                    else:
                        GreatOlm.damage(random.choices(Scythe_dmg_array,
                                                       Scythe_prob_array[GreatOlm.defence_current, :])[0])

                    if not GreatOlm.alive():
                        break

                else:
                    continue

                break

            ticks[num_dwh_inq, trial] = tick

    mean_ticks = np.asarray([np.mean(ticks[index, :]) for index in range(num_dwh + 1)])
    plot_tuples = []

    for num_dwh_inq in range(num_dwh + 1):
        slice_counter = Counter(ticks[num_dwh_inq, :])
        x = sorted(slice_counter.keys())
        y = [slice_counter[t] for t in x]
        plot_tuples.append((x, y))

    for num_inq, mt in zip(range(num_dwh + 1), mean_ticks):
        print(num_inq, mt)

    toc = time.time()
    print(toc - tic)

    fig = plt.subplot()
    title_string = '{:d} DWH, {:d} BGS, AVG DEF = {:.1f}'
    plt.xlabel("Kill time (ticks)")
    plt.ylabel("Probability mass, P(Kill time = X)")


    for (x, y), color in zip(plot_tuples, colors):
        # plt.vlines(defence_states, 0, distribution_space[num_dwh, num_bgs, :], colors=color)
        plt.plot(x, y, color=color)

    plt.legend(['No inquisitor', '1 Inquisitor', '2 Inquisitor'])

    plt.show()


if __name__ == '__main__':
    # defence_reduction_calculations(scale=7)

    trials_run = 1e6
    blaze_king_melee_hand(trials_run)

    # kill_time_simple_method(trials=trials_run, num_specs=7, team_scale=7, challenge_mode=False)
    # kill_time_variable_dwh_bgs(trials_run, 2, 2, 1)
    # kill_time_mixed_inquisitor(trials=trials_run, num_specs=4, team_scale=5, challenge_mode=False)

    # spec_arrangements = []      # [(3, 2, 2)]
    # people = 7
    # for i in range(people + 1):
    #     for j in range(people + 1 - i):
    #         for k in range(people + 1 - i - j):
    #             if not sum([i, j, k]) == 7:
    #                 continue
    #
    #             spec_arrangements.append((i, j, k))
    #
    # arrangement_ticks = []
    #
    # for sa in spec_arrangements:
    #     num_dwh, num_bgs, num_var = sa
    #     ticks = kill_time_variable_dwh_bgs(trials_run, num_dwh, num_bgs, num_var)
    #     arrangement_ticks.append(ticks)


