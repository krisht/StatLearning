
mydict = {}; 

songid2name = {};
sondid2artist = {}

with open('unique_tracks.txt') as f: 
	for line in f:
		s = line.rstrip('\n').split('<SEP>');
		songid2name[s[1]] = s[3];
		sondid2artist[s[1]] = s[2]; 



with open ('kaggle_songs.txt') as f:
	for line in f: 
		s = line.rstrip('\n').split(' ');  
		mydict[s[0]] = s[1][0]; 
		mydict[s[1]] = s[0]; 



with open('MSD_result.txt', 'r') as f:
	ii = 1;
	for line in f: 
		s = line.rstrip('\n').split(' '); 
		print("User", ii);
		for x in s:
			if x in mydict.keys():
				print(x, ',' ,songid2name[mydict[x]], ', ', sondid2artist[mydict[x]]);
		ii+=1;
