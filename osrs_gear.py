from imports import *
import itertools
import pandas as pd
import os
import pathlib

SETUPS_FILEPATH = 'setups_transpose.csv'

folder = r'gear list'
file_bgs = ('bgs', r'bandos godsword (bandos).txt')
file_dwh_bandos = ('dwh (bandos)', r'dragon warhammer (bandos).txt')
file_dwh_inquisitor = ('dwh (inquisitor)', r'dragon warhammer (inquisitor).txt')
file_scythe_bandos = ('scythe (bandos)', r'scythe of vitur (bandos).txt')
file_scythe_inquisitor = ('scythe (inquisitor)', r'scythe of vitur (inquisitor).txt')
file_dragon_hunter_lance = ('dhl', r'dragon hunter lance (bandos).txt')
file_dwh_bandos_diary = ('dwh (bandos diary)', r'dragon warhammer (bandos diary).txt')

file_abyssal_whip_scuff = ('abyssal whip scuff', r'abyssal whip scuff.txt')
file_ghrazi_rapier_scuff = ('ghrazi rapier scuff', r'ghrazi rapier scuff.txt')
file_staff_of_light_scuff = ('staff of light scuff', r'staff of light scuff.txt')

file_dharok = ('dharok', r'dharok.txt')
file_dharok_dwh = ('dharok_dwh', r'dharok_dwh.txt')
file_dharok_bgs = ('dharok_bgs', r'dharok_bgs.txt')

file_dhl_inq = ('dhl_inq', r'dragon hunter lance (inquisitor).txt')

file_tuples = [
	file_bgs,
	file_dwh_bandos,
	file_dwh_inquisitor,
	file_scythe_bandos,
	file_scythe_inquisitor,
	file_dragon_hunter_lance,
	file_dwh_bandos_diary,
	file_dharok,
	file_dharok_dwh,
	file_dharok_bgs,
	file_dhl_inq,
	file_abyssal_whip_scuff,
	file_ghrazi_rapier_scuff,
	file_staff_of_light_scuff,
]


def load_setups(setup_name: str):
	df = pd.read_csv(SETUPS_FILEPATH, delimiter='\t', dtype=str)
	df.columns = [s.lower() for s in df.columns]
	df_slice = df.loc[df['Name'] == setup_name]
	return df_slice


def load_gear_file(filepath: str) -> List[str]:
	lines = []

	with open(filepath, 'r') as f:
		for line in f:
			lines.append(line.strip().lower())

	return lines


presets = {}


for key, file in file_tuples:
	presets[key] = load_gear_file(os.path.join(folder, file))


def get_gear_from_csv() -> pd.DataFrame:
	"""Reads the gear list from the DPS spreadsheet by bitterkoekje/koekenpann/etc from csv format

	Change "None" that precedes the weapons list to "No Weapon" to preserve uniqueness of that single row"""

	df = pd.read_csv(r'gear.csv')
	df.columns = [s.lower() for s in df.columns]

	string_columns = ['item', 'special defence roll']

	for sc in string_columns:
		df[sc] = df[sc].str.lower().str.strip()

	integer_columns_range = np.append(np.append(np.arange(1, 13), 14), np.arange(19, 23))
	integer_columns = df.columns[integer_columns_range]

	for ic in integer_columns:
		df[ic] = df[ic].fillna(0)
		df[ic] = df[ic].apply(lambda x: int(x))

	float_columns_range = np.append(13, np.arange(15, 18))
	float_columns = df.columns[float_columns_range]

	for fc in float_columns:
		df[fc] = df[fc].fillna(0)

	df = df.set_index('item', drop=False)

	return df


def gear_lookup(df: pd.DataFrame, gear_list: Union[str, List[str]]) -> Tuple[pd.DataFrame, pd.Series]:
	"""Lookup the gear attributes of an item or items in the dataframe: df

	Return a dataframe of items and attributes as well as a series containing the column sums of all items"""

	gear_df = df.loc[gear_list, :]
	stat_total = gear_df.sum(skipna=True)
	return gear_df, stat_total


def main(filepath: str):
	gear_list = load_gear_file(filepath)
	gear_df, stats = gear_lookup(get_gear_from_csv(), gear_list)

	# load_setups()


if __name__ == '__main__':
	folder = r'gear list'
	files = [file for file in os.listdir(os.path.join(os.getcwd(), folder)) if os.path.splitext(file)[1] == '.txt']
	test_filepath = os.path.join(folder, files[1])
	main(test_filepath)
