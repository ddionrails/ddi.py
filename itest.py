from ddi import statareader

test1 = statareader.read_stata("test/data/test1.dta")
test1.add_statistics()
