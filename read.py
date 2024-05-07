from django import setup
setup()

from status.models import Status, Alert, Servers
from csv import reader

if __name__ == '__main__':

    with open('./test.csv', 'r') as f:
        r = reader(f)
        next(r)
        for line in r:
            s = Servers(server=line[0], ip=line[1])
            s.save()