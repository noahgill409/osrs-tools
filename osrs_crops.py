from imports import *
import markov
import osrs_markov


def chance_to_not_consume_life(lvl: int, attas: bool):
	lower_bound, upper_bound = (23, 99)
	lvl_bounded = np.clip(lvl, lower_bound, upper_bound)
	raw = np.interp(lvl_bounded, (23, 99), (0.641, 0.82))
	return raw + 0.05*attas


def seaweed():
	"""Hello world for seaweed expected yield through absorbing markov chain mathematics + simulation"""

	LIVES = {
		'compost':	4,
		'supercompost':	5,
		"ultracompost":	6
	}

	lives = LIVES['ultracompost']

	Q, R = osrs_markov.crop_transition_matrix_generator(lives, chance_to_not_consume_life(99, True))
	states = np.arange(lives, -1, -1)

	SeaweedMC = markov.AbsorbingMarkovChain(Q, R, states)

	print(SeaweedMC.expected_steps[0])

	start_state = np.zeros(states.shape)
	start_state[0] = 1

	hundred_step = SeaweedMC.probability_distribution(start_state, 7)
	print(1 - hundred_step[-1])

	step_range = np.arange(1, 101)
	distributions = SeaweedMC.probability_distribution(start_state, step_range)

	death_probability = 0
	death_distribution = {}

	for i, step in enumerate(step_range):

		if i == 0:
			death_distribution[step] = distributions[-1][i]

		else:
			death_distribution[step] = distributions[-1][i] - distributions[-1][i-1]

	x = list(death_distribution.keys())
	y = list(death_distribution.values())

	plt.plot(x, y)
	plt.xlabel('Seaweed harvested')
	plt.ylabel('Cumulative probability frequency P(X <= x)')
	plt.show()

	trials = 1e6
	trials = int(trials)
	data = np.ndarray(shape=(trials,1))

	for i in range(trials):
		data[i] = SeaweedMC.monte_carlo_absorbing(0)

	print(np.mean(data))


if __name__ == '__main__':
	seaweed()
