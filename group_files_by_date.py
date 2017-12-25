from astropy.io import fits
from astropy.time import Time 
import glob
import os
from paths_and_params import paths
import shutil

def open_anneal_mjd_list(anneal_info_dir):
	
	lines = []
	with open(anneal_info_dir+'/anneal_mjds.txt','r') as f:
		lines = f.readlines()
		
	return lines
	
def make_anneal_date_directories(proposal_subdir,anneal_mjds):

	"""For a filter/proposal ID subdirectory, creates a directory for each anneal date if 
		it doesn't exist already."""
		
	for anneal_mjd in anneal_mjds:
		if float(anneal_mjd) >= 56000: #roughly when earliest images were taken
			date_subdir = proposal_subdir+'/'+anneal_mjd
			if not os.path.isdir(date_subdir):
				print 'Making directory ' + date_subdir
				os.mkdir(date_subdir)

def get_mjd_from_files(proposal_subdir):

    files = glob.glob(proposal_subdir+'/*.fits')
    mjds = [] 

    for f in files:
        date_obs = fits.open(f)[0].header['DATE-OBS']
        t = Time(date_obs,format = 'iso')
        mjds.append(t.mjd)
    
    return (files,mjds)
    
def remove_empty_dirs():
	pass
	
def sort_files(file_paths,mjds,anneal_mjds):

	anneal_mjds = ['0'] + anneal_mjds
	
	for i in range(len(anneal_mjds)-1):
		for j, mjd in enumerate(mjds):
			file_path =file_paths[j]
			if (mjd > float(anneal_mjds[i]))  & (mjd <= float(anneal_mjds[i+1])):
				fname = os.path.basename(file_path)
				date_obs = fits.open(file_path)[0].header['date-obs']
				dest = file_path.replace(fname,'') +str(anneal_mjds[i+1])+'/{}/'.format(date_obs)+fname
				if not os.path.isdir(dest.replace(os.path.basename(dest),'')):
					print 'making directory',dest.replace(os.path.basename(dest),'')
					os.mkdir(dest.replace(os.path.basename(dest),''))
				print 'Moving ' + os.path.basename(file_path) + ' with an MJD of ' + str(mjd) + ' to ' + dest
				shutil.move(file_path,dest)
				
def main_group_files_by_date(data_dir,anneal_info_dir,prop_ids):

    anneal_mjds = open_anneal_mjd_list(anneal_info_dir)
    anneal_mjds = [item.replace('\n','') for item in anneal_mjds]
    

    filter_directories = glob.glob(data_dir+'/*')

    
    print 'Sorting files by anneal date...'
    for filter_directory in filter_directories:
    	proposal_subdirs = glob.glob(filter_directory+'/*')
    	for proposal_subdir in proposal_subdirs:

			#make new date subdirectories 
			make_anneal_date_directories(proposal_subdir,anneal_mjds)

			file_paths,mjds = get_mjd_from_files(proposal_subdir)
			#print mjds
	
			sort_files(file_paths,mjds,anneal_mjds)
	
			#remove empty dirs
	
			anneal_dirs = glob.glob(filter_directory+'/*')
	
			for dir in anneal_dirs:
				files_list = glob.glob(dir+'/*')
				print files_list
				if len(files_list) == 0:
					print 'removing',dir
					os.rmdir(dir)
				
        	
          
if __name__ == '__main__':

    paths = paths()
    data_dir = paths['data_dir']
    anneal_info_dir = paths['anneal_info_dir']
    prop_ids = paths['prop_ids']
    main_group_files_by_date(data_dir,anneal_info_dir,prop_ids)
    

