# this file defines tests which are run after successful flashing
# it is a tuple of tests, each of which contains description for
# a person executing the tests and second is a shell script

TESTS = (
{
    "desc":
        u"První test, instrukce.",
    "cmd":
        "/bin/true",
},
{
    "desc":
        u"Druhý test, instrukce.",
    "cmd":
        "/bin/false",
},
)
