from parse import *

str = 'NILAI,REZZA,PELAJARAN';
rest = parse('{CMD},{NAMA},{PEL}', str)
PELAJARAN = rest['PEL']
print(PELAJARAN)


