import math
import random
import sys

leftRange = 0
rightRange = 110000
fOutput = "MSDResults.txt"


def songs_to_dict(filename):
	songs = dict()
	with open(filename, 'r') as f:
		for line in f:
			_, song, _ = line.strip().split('\t')
			if song in songs:
				songs[song] += 1
			else:
				songs[song] = 1
	return songs


def map_songs_to_users(filename, set_users=None, ratio=1.0):
	songs2users = dict()
	with open(filename, 'r') as f:
		for line in f:
			if random.random() < ratio:
				user, song, _ = line.strip().split('\t')
				if not set_users or user in set_users:
					if song in songs2users:
						songs2users[song].add(user)
					else:
						songs2users[song] = set([user])

	return songs2users


def map_users_to_songs(filename):
	users2songs = dict()
	with open(filename, 'r') as f:
		for line in f:
			user, song, _ = line.strip().split('\t')
			if user in users2songs:
				users2songs[user].add(song)
			else:
				users2songs[user] = set([song])
	return users2songs


def load_users(filename):
	with open(filename, 'r') as f:
		user = mean_average_precision(lambda line: line.strip(), f.readlines())
	return user


def index_songs(filename):
	with open(filename, 'r') as f:
		songs2index = dict(mean_average_precision(lambda line: line.strip().split(' '), f.readlines()))
	return songs2index


def save_items(recs, song_file, out_file):
	songs2index = index_songs(song_file)
	with open(out_file, 'w') as f:
		for rec in recs:
			indices = mean_average_precision(lambda s: songs2index[s], rec)
			f.write(" ".join(indices) + "\n")


def get_unique(filename):
	user_set = set()
	with open(filename, 'r') as f:
		for line in f:
			user, _, _ = line.strip().split('\t')
			if user not in user_set:
				user_set.add(user)
	return user_set


def sort_songs(songs):
	return sorted(songs.keys(), key=lambda s: songs[s], reverse=True)


def average_precision(rec_list, su, tau):
	np = len(su)
	nc = 0.0
	users_mapr = 0.0

	for j, s in enumerate(rec_list):
		if j >= tau:
			break

		if s in su:
			nc += 1.0
			users_mapr += (nc / (j + 1))
	users_mapr /= min(np, tau)

	return users_mapr


def mean_average_precision(users_list, rec_song_lists, user2songs, tau):
	mapr = 0
	num_users = len(users_list)

	for i, rec_list, in enumerate(rec_song_lists):
		if not users_list[i] in user2songs:
			continue
		mapr += average_precision(rec_list, user2songs[users_list[i]], tau)

	return mapr / num_users


class SongRecsPredictor:
	def __init__(self, song_users, alpha=0, rho=1):
		self.song_users = song_users
		self.rho = rho
		self.alpha = alpha

	def match(self, s, u_song):
		l1 = len(self.song_users[s])
		l2 = len(self.song_users[u_song])
		up = float(len(self.song_users[s] & self.song_users[u_song]))
		if up > 0:
			dn = math.pow(l1, self.alpha) * math.pow(l2, (1.0 - self.alpha))
			return up / dn
		return 0.0

	def score(self, users2songs, total_score):
		agg_score = {}
		for s in total_score:
			agg_score[s] = 0.0
			if not (s in self.song_users):
				continue

			for userSong in users2songs:
				if not (userSong in self.song_users):
					continue
				song_match = self.match(s, userSong)
				agg_score[s] += math.pow(song_match, self.rho)
		return agg_score


class Recommender:
	def __init__(self, total_score):
		self.predictors = []
		self.total_score = total_score
		self.tau = 500
		self.gamma = []

	def add(self, p):
		self.predictors.append(p)

	def rand_index(self, size, distrib):
		r = random.random()
		for ii in range(size):
			if r < distrib[ii]:
				return ii
			r -= distrib[ii]
		return 0

	def rand_recommend(self, sorted_list, distrib):
		n_preds = len(self.predictors)
		r = []

		ii = [0] * n_preds

		while len(r) < self.tau:
			pi = self.rand_index(n_preds, distrib)
			s = sorted_list[pi][ii[pi]]
			if not s in r:
				r.append(s)
			ii[pi] += 1
		return r

	def simple_recommend(self, user, calibration):
		sorting = []
		for p in self.predictors:
			i_songs = []
			if user in calibration:
				i_songs = sort_songs(p.score(calibration[user], self.total_score))
			else:
				i_songs = list(self.total_score)

			clean_list = []

			for x in i_songs:
				if len(clean_list) >= self.tau:
					break
				if x not in calibration[user]:
					clean_list.append(x)

			sorting += [clean_list]
		return self.rand_rec(sorting, self.gamma)

	def recommend(self, users_list, calibration):
		liked_songs = []

		for i, u in enumerate(users_list):
			liked_songs.append(self.simple_recommend(u, calibration))
		sys.stdout.flush()
		return liked_songs


print "Left Range: %d\nRight Range: %d\n" % (leftRange, rightRange)
print "Processing data training data..."

sys.stdout.flush()

training_file = "train_triplets.txt"
evaluating_file = "kaggle_visible_evaluation_triplets.txt"

sys.stdout.flush()

users_v = list(load_users('kaggle_users.txt'))

sys.stdout.flush()

ordered_songs = sort_songs(songs_to_dict(training_file))

uniques = get_unique(training_file)

u2i = {}

for i, u in enumerate(uniques):
	u2i[u] = i

intro_songs_users = map_songs_to_users(training_file)

for s in intro_songs_users:
	song_filter = set()
	for u in intro_songs_users[s]:
		song_filter.add(u2i[u])
	intro_songs_users[s] = song_filter

del u2i

calibration = map_users_to_songs(evaluating_file)

alpha = 0.5
rho = 5

pr = SongRecsPredictor(intro_songs_users, alpha, rho)

instance = Recommender(ordered_songs)

instance.add(pr)

instance.gamma = [1.0]

r = instance.recommend(users_v[leftRange:rightRange], calibration);

save_items(r, 'kagglesongs.txt', fOutput)
