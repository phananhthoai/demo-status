from django import setup
setup()

from status.models import State, Alert, Server
from csv import reader

if __name__ == '__main__':

    with open('./test.csv', 'r') as f:
        r = reader(f)
        next(r)
        for line in r:
            s = Server(server=line[0], ip=line[1])
            s.save()