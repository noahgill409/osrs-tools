from imports import *
import itertools
import pandas as pd
import os

folder = r'gear list'
file_bgs = ('bgs', r'bandos godsword (bandos).txt')
file_dwh_bandos = ('dwh (bandos)', r'dragon warhammer (bandos).txt')
file_dwh_inquisitor = ('dwh (inquisitor)', r'dragon warhammer (inquisitor).txt')
file_scythe_bandos = ('scythe (bandos)', r'scythe of vitur (bandos).txt')
file_scythe_inquisitor = ('scythe (inquisitor)', r'scythe of vitur (inquisitor).txt')
file_dragon_hunter_lance = ('dhl', r'dragon hunter lance (bandos).txt')

file_tuples = [file_bgs, file_dwh_bandos, file_dwh_inquisitor, file_scythe_bandos, file_scythe_inquisitor,
               file_dragon_hunter_lance]


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
	print(gear_df)
	print(stats)


if __name__ == '__main__':
	folder = r'gear list'
	files = [file for file in os.listdir(os.path.join(os.getcwd(), folder)) if os.path.splitext(file)[1] == '.txt']
	test_filepath = os.path.join(folder, files[1])
	main(test_filepath)
