#!/usr/bin/python

from bs4 import BeautifulSoup
import urllib2
import sys
import pickle
import string

favourite_team = "Belarusian SU Air Penguins: Poliyevits, Sheftelevich, Sokol"
upsolving_url = "http://karelia.snarknews.info/index.cgi?data=macros/doresh&head=index&menu=index&sbname=2014s&class=2014s"
year = 2014


class Problem:

    def __init__(self, title, code, ac):
        self.title = title
        self.date = code[2:4] + '/' + code[:2] + '/' + str(year)
        self.letter = code[-1]
        self.ac = ac

    def __str__(self):
        return 'Date: %s, Task %s - "%s", AC: %d' % (
            self.date, self.letter, self.title, self.ac)


class Team:

    def __init__(self, name, solved):
        name = name.strip()
        while len(name) > 0 and name[0] not in string.letters:
            name = name[1:]
        self.name = name
        self.solved = solved

    def __str__(self):
        return '%s, Solved %d/%d' % (self.name,
                                     sum(self.solved),
                                     len(self.solved))


def get_problems(standings, teams):
    unparsed = standings.find_all("th")[3:-4]
    problems = []
    for id, record in enumerate(unparsed):
        title = record.attrs["title"]
        code = record.text[:5]
        ac = len(filter(lambda team: team.solved[id] == 1, teams))
        problems.append(Problem(title, code, ac))
    return problems


def get_teams(standings):
    unparsed = standings.find_all("tr")[1:-3]
    teams = []
    for record in unparsed:
        columns = record.find_all("td")[:-4]
        name = columns[1].text
        solved = []
        columns = columns[3:]
        for column in columns:
            if '+' in column.text:
                solved.append(1)
            else:
                solved.append(0)
        teams.append(Team(name, solved))
    return teams


def backup(datafile, *arrays):
    to_backup = []
    for array in arrays:
        to_backup.append(len(array))
        to_backup = to_backup + array
    pickle.dump(to_backup, open(datafile, "wb"))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print >> sys.stderr, "Too few arguments!"
        sys.exit(0)

    if len(sys.argv) > 3:
        print >> sys.stderr, "Too much arguments!"
        sys.exit(0)

    if len(sys.argv) == 3:
        if sys.argv[1] == '--get':
            datafile = sys.argv[2]
            try:
                data = pickle.load(open(datafile, "rb"))
                no_problems = data[0]
                no_teams = data[no_problems + 1]
                problems = []
                teams = []
                for i in range(1, no_problems + 1):
                    problems.append(data[i])
                for i in range(no_problems + 2, len(data)):
                    teams.append(data[i])
                print >> sys.stderr, "The data has been imported!"
            except:
                print >> sys.stderr, "Some problems were occurred while importing data!"
                sys.exit(0)
            the_team = None
            for team in teams:
                if team.name == favourite_team:
                    the_team = team
            print "The Team: %s" % the_team.name
            print "*" * 80
            problem_ids = filter(
                lambda id: the_team.solved[id] == 0,
                range(len(problems)))
            problems = sorted(
                    map(lambda id: problems[id], problem_ids), 
                    key=lambda problem: problem.ac, 
                    reverse=True)
            for problem in problems:
                print problem
        elif sys.argv[1] == '--pull':
            datafile = sys.argv[2]
            soup = BeautifulSoup(urllib2.urlopen(upsolving_url))
            print >> sys.stderr, "The page has been downloaded!"
            standings = soup.find("table", class_="standings")
            teams = get_teams(standings)
            problems = get_problems(standings, teams)
            try:
                backup(datafile, problems, teams)
                print >> sys.stderr, "The data has been exported!"
            except:
                print >> sys.stderr, "Some problems were occurred while exporting data!"
                sys.exit(0)
        else:
            print >> sys.stderr, "Wrong parameter!"
