from pyDatalog import pyDatalog

variables = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

for var in variables:
    pyDatalog.create_terms(var)

source = 'X'
target = 'Y'

pyDatalog.create_terms(source, target)

