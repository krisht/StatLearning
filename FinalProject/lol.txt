def evaluator(kagglesongs, recedsongs, hiddenset):
    usongs = []

    with open(kagglesongs, "r") as file:
        songsubset = dict(map(lambda line: list((line.strip().split(' ')[1],line.strip().split(' ')[0])), file.readlines()))

    with open(recedsongs) as file:
        for line in file:
            songset = line.strip().split(" ")
            for i in range(len(songset)):
                songset[i] = songsubset[songset[i]]
            usongs.append(songset)

    userindex = -1
    hiddenusers = []

    file = open(hiddenset)
    listusers = []

    for line in file:
        user, song,_, = line.split("\t")
        if user not in listusers:
            listusers.append(user)
            hiddenusers.append([])
            userindex += 1

        hiddenusers[userindex].append(song)

    cumulativemap = 0.0

    for i in range(0, len(hiddenusers)):
        value = 0.0
        for hsong in range(0, len(hiddenusers[i])):
            for rrsongs in range(0, len(usongs[i])):
                if hiddenusers[i][hsong] == usongs[i][rrsongs]:
                    value +=  (hsong + 1.0) / (rrsongs + 1.0)

        value /= len(hiddenusers[i])
        cumulativemap += value

    cumulativemap /= len(hiddenusers)
    return cumulativemap

recedsongs = "MSD_result.txt"
hiddenset = "Result_hidden.txt"
kagglesongs = "kaggle_songs.txt" 

print evaluator(kagglesongs, recedsongs, hiddenset)

