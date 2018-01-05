import requests
from paths_and_params import paths

def download_updated_anneal_file(:
	url = 'http://www.stsci.edu/hst/wfc3/ins_performance/monitoring/UVIS/anneal_dates-tab.txt'
	r = requests.get(url, allow_redirects = True)
	open('anneal_dates.txt','w').write(r.content)
	print 'Downloaded updated anneal dates file.'

def parse_updated_anneal_file():

	anneal_file = 'anneal_dates.txt'
	
	anneal_mjds = []
	with open(anneal_file,'r') as f:
		lines = f.readlines()
		for line in lines:
			line_split = line.split()
			if len(line_split) > 0:
				if 'anneal' in line_split[-1]:
					anneal_mjds.append(line_split[0])
	return anneal_mjds
	
def write_mjd_to_file(anneal_mjds):

	with open('anneal_mjds.txt','w') as f:
		for mjd in anneal_mjds:
			f.write(mjd+'\n')
			
def main_update_anneal_file(anneal_info_dir):
	download_updated_anneal_file()
	anneal_mjds = parse_updated_anneal_file()
	write_mjd_to_file(anneal_mjds)
	
			
if __name__ == '__main__':

	main_update_anneal_file()	
