from imports import *
from bedevere.markov import *



def dwh_effectiveness_estimate(level_defence: int) -> int:
	"""Returns an estimate of the amount of warhammer specs that need to land before it gets silly"""
	margin = 0.25
	dwh_modifier = 0.7
	return math.ceil(np.log(margin / (1 - dwh_modifier) / level_defence) / np.log(dwh_modifier))


def dwh_intermediate_values_to_absorption(level_defence: int) -> List[int]:
	"""Returns a list of the defence values traversed by purely dragon warhammer hits to absorption"""
	dwh_modifier = 0.7
	intermediate_values = [math.ceil(level_defence * dwh_modifier ** k) for k in
	                       range(dwh_effectiveness_estimate(level_defence))]

	duplicate_occurrence = None

	for i, e in enumerate(intermediate_values):
		if e == intermediate_values[i + 1]:
			duplicate_occurrence = i + 1
			break

	assert duplicate_occurrence
	intermediate_values = intermediate_values[:duplicate_occurrence]

	return intermediate_values


def dwh_transition_matrix_generator(level_defence: int, dwh_defence_range_chance_to_land: Union[dict, np.array]) \
		-> Tuple[np.ndarray, np.ndarray]:
	"""Generates an absorbing transition matrix pair Q, R for solely DWH specs"""
	intermediate_values = dwh_intermediate_values_to_absorption(level_defence)
	transition_probabilities = [dwh_defence_range_chance_to_land[iv] for iv in intermediate_values][:-1]
	r = intermediate_values[-2]
	t = level_defence - r + 1

	Q = np.zeros(shape=(t, t))
	R = np.zeros(shape=(t, r))

	for index, e in enumerate(intermediate_values):
		i = level_defence - e
		j = level_defence - intermediate_values[index + 1]
		Q[i, i] = 1 - transition_probabilities[index]

		try:
			Q[i, j] = transition_probabilities[index]

		except IndexError as E:
			R[i, 0] = transition_probabilities[index]
			break

	return Q, R


def dwh_transition_matrix_generator_compact(level_defence: int,
                                            dwh_defence_range_chance_to_land: Union[dict, np.array]) \
		-> Tuple[np.ndarray, np.ndarray, np.array]:
	"""Generates an absorbing transition matrix pair Q, R for solely DWH specs, compacted to only important levels"""
	intermediate_values = dwh_intermediate_values_to_absorption(level_defence)
	transition_probabilities = [dwh_defence_range_chance_to_land[iv] for iv in intermediate_values][:-1]

	t = len(transition_probabilities)
	r = 1

	Q = np.zeros(shape=(t, t))
	R = np.zeros(shape=(t, r))

	for index, e in enumerate(intermediate_values):
		i = index
		j = index + 1
		Q[i, i] = 1 - transition_probabilities[index]

		try:
			Q[i, j] = transition_probabilities[index]

		except IndexError as E:
			R[i, 0] = transition_probabilities[index]
			break

	return Q, R, np.asarray(intermediate_values)


def bgs_transition_matrix_generator(level_defence: int, bgs_max: int,
                                    bgs_defence_range_accuracy: Union[dict, np.array]) -> Tuple[np.ndarray, np.ndarray]:
	"""Generates an absorbing transition matrix pair Q, R for solely bgs specs of a single weapon"""
	t = level_defence
	r = 1

	Q = np.zeros(shape=(t, t))
	R = np.zeros(shape=(t, r))

	for i in range(t):
		row_accuracy = bgs_defence_range_accuracy[t - i]   # def lvl = defence - row

		for j in range(i, t):
			Q[i, j] = (j - i <= bgs_max) * (1 / (bgs_max + 1)) * row_accuracy + (i == j) * (1 - row_accuracy)

		if bgs_max >= t - i:
			R[i, 0] = 1 - sum(Q[i, :])

	# for i in range(t):
	# 	Q[i, i] = bgs_acc / (bgs_max + 1) + (1 - bgs_acc)
	#
	# 	try:
	# 		Q[i, i+1:i+2+bgs_max] = bgs_acc / (bgs_max + 1) * np.ones(shape=bgs_max)
	#
	# 	except IndexError as E:
	# 		if i < t - 1:
	# 			Q[i, i+1:] = bgs_acc / (bgs_max + 1) * np.ones(shape=t-i-1)
	#
	# 		R[i, 0] = 1 - sum(Q[i, :])
	# 	# fix that

	return Q, R


def crop_transition_matrix_generator(crop_lives: int, chance_to_preserve_life: float) -> Tuple[np.ndarray, np.ndarray]:
	"""Generates a transition matrix pair Q, R for a crop with N lives and p chance to preserve a life per harvest"""
	p = chance_to_preserve_life
	q = 1 - p

	Q = np.diag(p*np.ones(crop_lives))
	Q[:-1, 1:] += np.diag(q*np.ones(crop_lives-1))
	R = np.zeros(shape=(crop_lives, 1))
	R[-1] = q

	return Q, R


def main():
	Q, R = dwh_transition_matrix_generator(182, np.interp(np.arange(183), (182, 0), (0.64, 0.99)))
	Q2, R2 = bgs_transition_matrix_generator(182, 73, np.interp(np.arange(183), (182, 0), (0.80, 0.99)))

	print(Q2, R2)


if __name__ == '__main__':
	main()
