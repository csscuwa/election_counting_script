import os
import sys

def read_votes_file(vote_file, numberCandidates):
    lineNumber = 1
    all_votes = []
    for paper in vote_file:
        paper = paper.strip()
        paper = paper.split(',')
        thisPaper = []
        valid_paper = check_vote_valid(paper, numberCandidates)
        if(not valid_paper):
            print("invalid paper on line " + str(lineNumber))
        else:
            for vote in paper:
                try:
                    vote = int(vote.strip())
                except:
                    vote = ''
                thisPaper.append(vote)
        lineNumber += 1
        all_votes.append(thisPaper)
    return all_votes

def check_vote_valid(paper, numberCandidates):
    if(len(paper)!=numberCandidates):
        return False

    missingVotes = False

    paper = list(filter(None, paper))
    try:
        paper = [int(x) for x in paper]
    except:
        missingVotes = True
    else:
        paper = sorted(paper)
        for i in range(len(paper)):
            if(i+1 != paper[i]):
                missingVotes = True

    if(missingVotes):
        return False
    else:
        return True

def count_votes(papers, candidates, winning_cands=[], full_details=False, removal_disp=False):
    winnerFound = False
    papers, candidates = remove_winners(papers, candidates, winning_cands)

    original_papers = copy_papers(papers)
    original_candidates = candidates.copy()

    while(not winnerFound):
        cand_dict = {}
        for cand in candidates:
            cand_dict[cand] = 0
        numberOfPapers = len(papers)
        for paper in papers:
            voteNum = 0
            for vote in paper:
                if(vote == 1):
                    this_cand = candidates[voteNum]
                    cand_dict[this_cand] += 1
                voteNum += 1
        maxVotes = max(cand_dict.values())

        if(maxVotes > (numberOfPapers/2)):
            winnerFound = True
            for cand, primary_vote in cand_dict.items():
                if primary_vote == maxVotes:
                    print("Winner found!")
                    if(full_details):
                        print(cand + " is declared the winner with " + str(maxVotes) + " votes.")
                        print(cand_dict)
                    else:
                        print(cand + " is declared the winner with an absolute majority.")
                    return cand
        else:
            if(calculate_tie(cand_dict, maxVotes, numberOfPapers)):
                print("Optional Preferential Voting with absolute majority has resulted in a tie.")
                print("Using backup election method")
                winnerFound = True
                return count_votes_non_majority(original_papers, original_candidates, full_details, removal_disp)
            else:
                papers, candidates = remove_lowest_candidate(papers, cand_dict, candidates, removal_disp)

def calculate_tie(cand_dict, maxVotes, numberOfPapers):
    #quick way to determine if it's a tie
    if(len(cand_dict) == 2 and maxVotes == (numberOfPapers/2)):
        return True
    else:
        for candidate in cand_dict.values():
            if(candidate != maxVotes):
                return False

    return True

def count_votes_non_majority(papers, candidates, full_details, removal_disp):
    winnerFound = False
    while(not winnerFound):
        cand_dict = {}
        for cand in candidates:
            cand_dict[cand] = 0
        numberOfPapers = len(papers)
        for paper in papers:
            voteNum = 0
            for vote in paper:
                if(vote == 1):
                    this_cand = candidates[voteNum]
                    cand_dict[this_cand] += 1
                voteNum += 1
        maxVotes = max(cand_dict.values())

        candidatesWithMaxVotes = []
        for key, value in cand_dict.items():
            if value == maxVotes:
                candidatesWithMaxVotes.append(key)

        if(len(candidatesWithMaxVotes) == 1):
            cand = candidatesWithMaxVotes[0]
            print("Winner has been found through non-absolute majority selection method")
            if(full_details):
                print(cand + " is declared the winner with " + str(maxVotes) + " votes.")
                print(cand_dict)
            else:
                print(cand + " is declared the winner.")
            winnerFound = True
            return cand
        else:
            if(calculate_tie(cand_dict, maxVotes, numberOfPapers)):
                print("A tie has occured at every single level of the election")
                print("Please refer to documentation on what further action to take")
                winnerFound = True
                return None
            else:
                papers, candidates = remove_lowest_candidate(papers, cand_dict, candidates, removal_disp)

def read_candidates(can_file, orderOfFile):
    positionsDictionary = {}
    lineNumber = 0
    for line in can_file:
        thisLine = []
        for can in line.split(","):
            thisLine.append(can.strip())
        positionsDictionary[orderOfFile[lineNumber]] = thisLine
        lineNumber += 1

    return positionsDictionary

def remove_winners(papers, candidates, winning_cands):
    for cand in winning_cands:
        if(cand in candidates):
            indexOfCand = candidates.index(cand)
            papers = adjust_papers(papers, indexOfCand)
            del candidates[indexOfCand]
    return papers, candidates

def copy_papers(papers):
    original_papers = []
    for paper in papers:
        copy_paper = []
        for vote in paper:
            copy_paper.append(vote)
        original_papers.append(copy_paper)
    return original_papers

def remove_lowest_candidate(papers, cand_dict, candidates, removal_disp):
    minVotes = min(cand_dict.values())

    number_of_min_cands = list(cand_dict.values()).count(minVotes)

    removal_list = []
    for cand, primary_vote in cand_dict.items():
        if primary_vote == minVotes:
            indexOfCand = candidates.index(cand)
            removal_list.append(indexOfCand)

    if(len(removal_list) == 1):
        for indexOfCand in removal_list:
            if(removal_disp):
                print('Removing candidate ' + cand + ' who had ' + str(minVotes) + ' vote(s)')
            else:
                print('Removing the candidate with the fewest votes.')
            papers = adjust_papers(papers, indexOfCand)
            del candidates[indexOfCand]
    else:
        print("Multiple candidates, need to run mini election to determine who to remove")
        papers, candidates = mini_election(removal_list, candidates, papers)
    return papers, candidates

def mini_election(candidates_to_remove=[], candidates=[], papers=[[]]):
    #not going to lie, this section needs some serious work.
    mini_election_papers = copy_papers(papers)
    candidate_copy = candidates.copy()

    candidate_not_involved = []
    for i in range(len(candidates)):
        if(i not in candidates_to_remove):
            candidate_not_involved.append(i)

    candidates_not_involved = [candidates[i] for i in candidate_not_involved]

    mini_election_papers, me_candidates = remove_winners(mini_election_papers, candidates, candidates_not_involved)


    new_papers = []
    for paper in mini_election_papers:
        new_paper = []
        for vote in paper:
            if vote == '':
                vote = len(paper)
            new_paper.append(vote)
        new_papers.append(new_paper)

    mini_election_papers = new_papers

    cand_dict = {}

    for cand in me_candidates:
        cand_dict[cand] = 0

    for paper in mini_election_papers:
        i = 0
        for vote in paper:
            cand_dict[me_candidates[i]] += vote
            i += 1

    #The person(s) with the highest number is the least preferred person
    max_votes = max(cand_dict.values())

    for cand in cand_dict.keys():
        #doing it this way handles if there's a tie - removes both at the same time
        if(cand_dict[cand] == max_votes):
            cand_index = candidate_copy.index(cand)
            papers = adjust_papers(papers, cand_index)
            del candidate_copy[cand_index]


    return papers, candidate_copy

def adjust_papers(papers, indexToRemove):
    fixed_papers = []
    for paper in papers:
        valueOfVote = paper[indexToRemove]
        if(valueOfVote == ''):
            pass
        else:
            paper = [-1 if vote=='' else vote for vote in paper]
            paper = [ (vote - 1) if vote > valueOfVote else vote for vote in paper ]
            paper = ['' if vote==-1 else vote for vote in paper]
        del paper[indexToRemove]
        if(paper_not_empty(paper)):
            fixed_papers.append(paper)
    return fixed_papers

def paper_not_empty(paper):
    for vote in paper:
        if vote != '':
            return True
    return False

def string_to_bool(input_value):
    if(input_value.lower()=='y'):
        return True
    else:
        return False


def main():
    year = input("Year you are calculating the results for: ")
    more_deets = string_to_bool(input("Show full details? [Y/n]: ") or 'y')
    display_removal_name = string_to_bool(input("Display Who's Removed? [y/N]: ") or 'n')

    orderOfCanFile = ['President', 'Vice President', 'Secretary', 'Treasurer']

    candidatesFile = open(year + "/candidates", 'r')

    votesFilePresident = open("./" + year + "/01. president", 'r')
    votesFileVP = open("./" + year + "/02. vp", 'r')
    votesFileSecretary = open("./" + year + "/03. secretary", 'r')
    votesFileTreasurer = open("./" + year + "/04. treasurer", 'r')

    cand_dict = read_candidates(candidatesFile, orderOfCanFile)

    president_candidates = cand_dict[orderOfCanFile[0]]
    vp_candidates = cand_dict[orderOfCanFile[1]]
    sec_candidates = cand_dict[orderOfCanFile[2]]
    tres_candidates = cand_dict[orderOfCanFile[3]]

    winner_list = []

    print("=======President File=======")
    presidentVotes = read_votes_file(votesFilePresident, len(president_candidates))

    pres_results = count_votes(papers=presidentVotes, candidates=president_candidates, winning_cands=winner_list, full_details=more_deets, removal_disp=display_removal_name)
    winner_list.append(pres_results)

    print("=======Vice President File=======")
    vicepresidentVotes = read_votes_file(votesFileVP, len(vp_candidates))

    vpres_results = count_votes(papers=vicepresidentVotes, candidates=vp_candidates, winning_cands=winner_list, full_details=more_deets, removal_disp=display_removal_name)
    winner_list.append(vpres_results)

    print("=======Secretary File=======")
    secVotes = read_votes_file(votesFileSecretary, len(sec_candidates))

    sec_results = count_votes(papers=secVotes, candidates=sec_candidates, winning_cands=winner_list, full_details=more_deets, removal_disp=display_removal_name)
    winner_list.append(sec_results)

    print("=======Treasurer File=======")
    tresVotes = read_votes_file(votesFileTreasurer, len(tres_candidates))

    tres_results = count_votes(papers=tresVotes, candidates=tres_candidates, winning_cands=winner_list, full_details=more_deets, removal_disp=display_removal_name)
    winner_list.append(tres_results)


if __name__ == '__main__':
    main()
