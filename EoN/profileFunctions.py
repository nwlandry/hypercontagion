import pstats
p = pstats.Stats('EoN/test')
p.sort_stats(1).print_stats(.01)
#p.strip_dirs().sort_stats(1).print_stats()
