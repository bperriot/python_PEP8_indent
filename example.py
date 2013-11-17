
numbers = ['1', '2', '3',
           '4', '5', '6']

alpha = (
    'a', 'b', 'c',
    'd', 'e', 'f')


def foo(arg1, arg2,
        arg3, arg4):
    return "a"


def barbaz(
        arg1, arg2,
        arg3, arg4):
    pass


if letter == 'a':
    print "A"
elif letter == 'b':
    print "B"
else:
    print "other"
    pass


try:
    print alpha[7]
except IndexError:
    pass


if n % 2 == 0:
    if n % 3 == 0:
        print "fizzbuz"
    else:
        print "fizz"
else:
    print "nope"
    pass


for i in range(10):
    if i % 5 == 0:
        break
    elif i % 3 == 0:
        raise ValueError("i % 3")
    continue





