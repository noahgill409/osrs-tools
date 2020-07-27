from osrs_classes import *
from osrs_combat import *
from discrete_sums import *
from markov import *

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from time import time

tic = time()

# TODO: Fix this to meet the current format of osrs_classes.py


def dwh_damage_distribution(dwh_max: int):
	# give discrete uniform distribution from 1 to max
	return n_convolution_discrete_uniform_non_standard_range((1, dwh_max), 1)


# NPCs
vasa = NPC(attack=1, strength=1, defence=466, ranged=903, magic=903, hitpoints=22950,
		   defence_bonuses=(170, 190, 50, 60, 400))
crystal = NPC(attack=1, strength=1, defence=267, ranged=1, magic=267, hitpoints=9178,
			  defence_bonuses=(-5, 180, 180, 0, 0))

NPCs = [vasa, crystal]
maximum_possible_defence = max(npc.defence for npc in NPCs)

# bandos armor attack and strength bonuses
gamer_dwh = Player(99, 99, 99, 99, 99, 99, 99, (0, 0, 164, 0, 0), (146, 0, 0), (0, 0, 0, 0, 0))
gamer_bgs = Player(99, 99, 99, 99, 99, 99, 99, (0, 169, 0, 0, 0), (189, 0, 0), (0, 0, 0, 0, 0))
gamer_scy = Player(99, 99, 99, 99, 99, 99, 99, (0, 147, 0, 0, 0), (132, 0, 0), (0, 0, 0, 0, 0))
gamer_rap = Player(99, 99, 99, 99, 99, 99, 99, (161, 0, 0, 0, 0), (155, 0, 0), (0, 0, 0, 0, 0))

bandos_attack_bonus = [1.20]
bandos_strength_bonus = [1.23]

# # inquisitor attack and strength bonuses
# gamer_dwh = Player(99, 99, 99, 99, 99, 99, 99, (0, 0, 200, 0, 0), (140, 0, 0), (0, 0, 0, 0, 0))
#
# inquisitor_attack_bonus = [1.20, 1.025]
# inquisitor_strength_bonus = [1.23, 1.025]

# ranged
gamer_void_tb = Player(99, 99, 99, 99, 99, 99, 99, (0, 0, 0, 109, 0), (0, 87, 0), (0, 0, 0, 0, 0))
gamer_arma_tb = Player(99, 99, 99, 99, 99, 99, 99, (0, 0, 0, 184, 0), (0, 87, 0), (0, 0, 0, 0, 0))
gamer_arma_cb = Player(99, 99, 99, 99, 99, 99, 99, (0, 0, 0, 214, 0), (0, 129, 0), (0, 0, 0, 0, 0))


# 248.1% damage modifier from tbow, 140% accuracy modifier
void_attack_bonus = [1.20, 1.125, 1.40]
void_strength_bonus = [1.23, 1.125, 2.481]

arma_tb_attack_bonus = [1.20, 1.40]
arma_tb_strength_bonus = [1.23, 2.481]

arma_cb_attack_bonus = [1.20]
arma_cb_strength_bonus = [1.23]

# overload assumption at 99
pot_bonus = 21

# Max hits where applicable, scythe is unique due to its non-discrete-uniform distribution so no need to pre-calculate
_, bgs_spec_max = gamer_bgs.spec_bgs(other=vasa, pot_bonus=pot_bonus, attack_modifier=bandos_attack_bonus,
									 strength_modifier=bandos_strength_bonus)
_, rap_max = gamer_rap.attack_npc(other=crystal, style_bonus_attack=0, style_bonus_strength=3, pot_bonus=pot_bonus,
								  damage_type="stab", attack_modifier=bandos_attack_bonus,
								  strength_modifier=bandos_strength_bonus)

# _, dwh_spec_max = gamer_dwh.spec_dwh_npc(other=vasa, pot_bonus=pot_bonus, attack_modifier=inquisitor_attack_bonus,
# 										 strength_modifier=inquisitor_strength_bonus)

_, dwh_spec_max = gamer_dwh.spec_dwh_npc(other=vasa, pot_bonus=pot_bonus, attack_modifier=bandos_attack_bonus,
										 strength_modifier=bandos_strength_bonus)

_, tb_arma_max = gamer_arma_tb.attack_npc(other=vasa, style_bonus_attack=0, style_bonus_strength=0, pot_bonus=pot_bonus,
										  damage_type="ranged", attack_modifier=arma_tb_attack_bonus,
										  strength_modifier=arma_tb_strength_bonus)


# Distinction between land/hit:
# land		DWH successfully hits and rolls NOT zero ie. {1, 2, 3, ... k}, P(damage > 0 | P(hit | def, bonus)))
# hit		BGS successfully hits and rolls any value in {0, 1, 2, ... k}, P(hit | def, bonus)

prob_land_DWH_vasa = np.empty(shape=vasa.defence + 1)
prob_land_DWH_crystal = np.empty(shape=crystal.defence + 1)

prob_hit_BGS_vasa = np.empty(shape=vasa.defence + 1)
prob_hit_BGS_crystal = np.empty(shape=crystal.defence + 1)

prob_hit_rap_crystal = np.empty(shape=crystal.defence + 1)

prob_hit_tb_arma_vasa = np.empty(shape=vasa.defence + 1)

dmg_dist_BGS_vasa = {}
dmg_dist_BGS_crystal = {}
dmg_dist_rap_crystal = {}
dmg_dist_scy_crystal = {}
dmg_dist_tb_arma_vasa = {}
dmg_dist_cb_arma_vasa = {}

dmg_dist_DWH_landed = dwh_damage_distribution(dwh_spec_max)  	# independent of probability to hit because of landed

for dl in range(vasa.defence + 1):  # pre-generate accuracy rolls from 0 to maximum possible defence
	vasa.defence_current = dl

	prob_land_DWH_vasa[dl], _ = gamer_dwh.spec_dwh_npc(vasa, pot_bonus, bandos_attack_bonus, bandos_strength_bonus)
	prob_hit_BGS_vasa[dl], _ = gamer_bgs.spec_bgs(vasa, pot_bonus, bandos_attack_bonus, bandos_strength_bonus)
	prob_hit_tb_arma_vasa[dl], _ = gamer_arma_tb.attack_npc(vasa, 0, 0, pot_bonus, "ranged",
															attack_modifier=arma_tb_attack_bonus,
															strength_modifier=arma_tb_strength_bonus)

	dmg_dist_BGS_vasa[dl] = hit_distribution(bgs_spec_max, prob_hit_BGS_vasa[dl])
	dmg_dist_tb_arma_vasa[dl] = hit_distribution(tb_arma_max, prob_hit_tb_arma_vasa[dl])
	dmg_dist_cb_arma_vasa[dl] = gamer_arma_cb.crossbow_distribution(vasa, 0, 0, pot_bonus, arma_cb_attack_bonus,
																	arma_cb_strength_bonus, kandarin_hard_diary=True)

for dl in range(crystal.defence + 1):
	crystal.defence_current = dl
	prob_land_DWH_crystal[dl], _ = gamer_dwh.spec_dwh_npc(crystal, pot_bonus, bandos_attack_bonus, bandos_strength_bonus)
	prob_hit_BGS_crystal[dl], _ = gamer_bgs.spec_bgs(crystal, pot_bonus, bandos_attack_bonus, bandos_strength_bonus)
	prob_hit_rap_crystal[dl], _ = gamer_rap.attack_npc(crystal, 0, 3, pot_bonus, "stab", bandos_attack_bonus,
													   bandos_strength_bonus)

	dmg_dist_BGS_crystal[dl] = hit_distribution(bgs_spec_max, prob_hit_BGS_crystal[dl])
	dmg_dist_rap_crystal[dl] = hit_distribution(rap_max, prob_hit_rap_crystal[dl])
	dmg_dist_scy_crystal[dl] = gamer_scy.scythe_distribution(other=crystal, pot_bonus=pot_bonus,
															 attack_modifier=bandos_attack_bonus,
															 strength_modifier=bandos_strength_bonus)

	# print(dl, 'rapier wins: ', mean_damage_per_tick(dmg_dist_rap_crystal[dl], 4) > mean_damage_per_tick(dmg_dist_scy_crystal[dl], 5))

toc = time()

print('overhead: ', int(toc - tic), ' seconds')


def main(num_dps: int, num_specs: Union[int, Tuple[int, int]], trials: Union[int, float]):
	trials = int(trials)
	special_distributions = []

	crystal_mean_ticks_to_kill_best_spec_arrangement = {}
	vasa_mean_ticks_to_kill_best_spec_arrangement = {}

	if type(num_specs) == int:
		min_specs = 0
		max_specs = num_specs

	else:
		min_specs, max_specs = num_specs

	num_tb = 25
	num_cb = num_dps - num_tb

	for ns in range(min_specs, max_specs + 1):

		for num_dwh in range(ns + 1):
			tic = time()

			num_bgs = ns - num_dwh
			# num_claw = num_dps - ns

			special_distributions.append((num_dwh, num_bgs))

			crystal_dl_after_specials = np.empty(shape=trials)
			crystal_ticks_to_kill = np.empty(shape=trials)

			vasa_dl_after_specials = np.empty(shape=trials)
			vasa_ticks_to_kill = np.empty(shape=trials)

			for trial in range(trials):
				# Crystal Phase
				trial_crystal = NPC(attack=1, strength=1, defence=267, ranged=1, magic=267, hitpoints=9178,
									defence_bonuses=(-5, 180, 180, 0, 0))
				crystal_ticks = 0

				# DWH
				for i in range(num_dwh):
					p = prob_land_DWH_crystal[trial_crystal.defence_current]
					hit = random.choices([False, True], [1 - p, p])[0]

					if hit:
						trial_crystal.modify_defence_percent(0.70)  	# getter/setter function to handle partial def
						trial_crystal.damage(random_damage(dmg_dist_DWH_landed))

				crystal_ticks += 1

				# BGS
				for i in range(num_bgs):
					damage = random_damage(dmg_dist_BGS_crystal[trial_crystal.defence_current])
					trial_crystal.modify_defence_flat(-1*damage)
					trial_crystal.damage(damage)

				crystal_ticks += 1

				crystal_dl_after_specials[trial] = trial_crystal.defence_current

				# continue  	# defense only

				# # Claw 1
				# for i in range(num_claw):
				# 	damage = random_damage(dmg_dist_claw_crystal[trial_crystal.defence_current])
				# 	trial_crystal.damage(damage)
				#
				# ticks += 4
				#
				# # Claw 2 / DWH scythe
				# for i in range(num_claw):
				# 	trial_crystal.damage(random_damage(dmg_dist_claw_crystal[trial_crystal.defence_current]))
				#
				# for i in range(num_dwh):
				# 	trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))
				#
				# ticks += 1
				#
				# # BGS Scythe
				# for i in range(num_bgs):
				# 	trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))
				#
				# ticks += 3
				#
				# # Now regular scythe attacks on three 1-tick different cycles
				# while trial_crystal.alive():
				#
				# 	for i in range(num_claw):
				# 		trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))
				#
				# 	ticks += 1
				#
				# 	if not trial_crystal.alive():
				# 		break
				#
				# 	for i in range(num_dwh):
				# 		trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))
				#
				# 	ticks += 1
				#
				# 	if not trial_crystal.alive():
				# 		break
				#
				# 	for i in range(num_bgs):
				# 		trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))
				#
				# 	ticks += 3

				# first round of scythes from everyone who didn't spec

				# first round of scythes from those who didn't spec
				for i in range(num_dps - ns):
					trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))

				crystal_ticks += 4

				# regular cycle of (DWH group followed 1 tick later by BGS/Nonspec group)
				while trial_crystal.alive():

					for i in range(num_dwh):
						trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))

					crystal_ticks += 1

					if not trial_crystal.alive():
						break

					for i in range(num_dps - num_dwh):
						trial_crystal.damage(random_damage(dmg_dist_scy_crystal[trial_crystal.defence_current]))

					crystal_ticks += 4

				crystal_ticks_to_kill[trial] = crystal_ticks

				# Vasa phase: assume for now that the specs are on time, implications on crystal kill time of course
				trial_vasa = NPC(attack=1, strength=1, defence=466, ranged=903, magic=903, hitpoints=22950,
								 defence_bonuses=(170, 190, 50, 400, 60))
				vasa_ticks = 0

				# DWH
				for i in range(num_dwh):
					p = prob_land_DWH_vasa[trial_vasa.defence_current]
					hit = random.choices([False, True], [1 - p, p])[0]

					if hit:
						trial_vasa.modify_defence_percent(0.70)  # getter/setter function to handle partial def
						trial_vasa.damage(random_damage(dmg_dist_DWH_landed))

				vasa_ticks += 1

				# BGS
				for i in range(num_bgs):
					damage = random_damage(dmg_dist_BGS_vasa[trial_vasa.defence_current])
					trial_vasa.modify_defence_flat(-1 * damage)
					trial_vasa.damage(damage)

				vasa_ticks += 1

				vasa_dl_after_specials[trial] = trial_vasa.defence_current

				# first round of bows from those who didn't spec
				for i in range(num_tb - ns):
					trial_vasa.damage(random_damage(dmg_dist_tb_arma_vasa[trial_vasa.defence_current]))

				for i in range(num_cb):
					trial_vasa.damage(random_damage(dmg_dist_cb_arma_vasa[trial_vasa.defence_current]))

				vasa_ticks += 4

				# regular cycle of (DWH group followed 1 tick later by BGS/Nonspec group)
				while trial_vasa.alive():

					for i in range(num_dwh):
						trial_vasa.damage(random_damage(dmg_dist_tb_arma_vasa[trial_vasa.defence_current]))

					vasa_ticks += 1

					if not trial_vasa.alive():
						break

					for i in range(num_tb - num_dwh):
						trial_vasa.damage(random_damage(dmg_dist_tb_arma_vasa[trial_vasa.defence_current]))

					for i in range(num_cb):
						trial_vasa.damage(random_damage(dmg_dist_cb_arma_vasa[trial_vasa.defence_current]))

					vasa_ticks += 4

				vasa_ticks_to_kill[trial] = vasa_ticks

			crystal_mean_defence = np.mean(crystal_dl_after_specials)
			crystal_zero_chance = 100 * Counter(crystal_dl_after_specials)[0] / trials

			vasa_mean_defence = np.mean(vasa_dl_after_specials)
			vasa_zero_chance = 100 * Counter(vasa_dl_after_specials)[0] / trials

			x = []
			y = []
			crystal_ticks_to_kill_counter = Counter(crystal_ticks_to_kill)

			for key in sorted(list(crystal_ticks_to_kill_counter.keys())):
				x.append(key)
				y.append(crystal_ticks_to_kill_counter[key] / trials)

			toc = time()

			crystal_mean_kill_ticks = np.mean(crystal_ticks_to_kill)
			crystal_std_kill_ticks = np.std(crystal_ticks_to_kill)

			vasa_mean_kill_ticks = np.mean(vasa_ticks_to_kill)
			vasa_std_kill_ticks = np.std(vasa_ticks_to_kill)

			s = '{:1.0f} DWH, {:1.0f} BGS:\tTicks to kill (Mean/Std Dev):\t{:3.0f}, {:3.0f},\tMean Defense:\t{:3.0f}, ' \
				'Zero Defence % Chance:\t{:5.1f}'

			print(s.format(num_dwh, num_bgs, crystal_mean_kill_ticks, crystal_std_kill_ticks, crystal_mean_defence,
						   crystal_zero_chance))

			print(s.format(num_dwh, num_bgs, vasa_mean_kill_ticks, vasa_std_kill_ticks, vasa_mean_defence, vasa_zero_chance))

			if ns in crystal_mean_ticks_to_kill_best_spec_arrangement:
				crystal_mean_ticks_to_kill_best_spec_arrangement[ns] = min(crystal_mean_ticks_to_kill_best_spec_arrangement[ns],
																		   crystal_mean_kill_ticks)

			else:
				crystal_mean_ticks_to_kill_best_spec_arrangement[ns] = crystal_mean_kill_ticks

			if ns in vasa_mean_ticks_to_kill_best_spec_arrangement:
				vasa_mean_ticks_to_kill_best_spec_arrangement[ns] = min(vasa_mean_ticks_to_kill_best_spec_arrangement[ns],
																		vasa_mean_kill_ticks)

			else:
				vasa_mean_ticks_to_kill_best_spec_arrangement[ns] = vasa_mean_kill_ticks

			# plt.plot(x, y)
			# plt.show()
	x = []
	y = []

	for key, val in crystal_mean_ticks_to_kill_best_spec_arrangement.items():
		x.append(key)
		y.append(val)

	plt.plot(x, y)

	x = []
	y = []

	for key, val in vasa_mean_ticks_to_kill_best_spec_arrangement.items():
		x.append(key)
		y.append(val)

	plt.plot(x, y)

	plt.legend(['crystal', 'vasa'])
	plt.show()


if __name__ == '__main__':
	main(num_dps=50, num_specs=[0, 25], trials=50)
