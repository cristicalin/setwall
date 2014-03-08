import copy
from wpm.filelist import *
f = filelist()
f.load("/home/kman/bin/wpm")
f.get_list()
p = copy.copy(f)
p.sort()
f.randomize()
p.get_list()
f.get_list()
p.close()
f.close()