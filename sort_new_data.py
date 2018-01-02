from astropy.io import fits
from astropy.time import Time
import glob
import os
from paths_and_params import *
import shutil
    
def open_anneal_mjd_list():

    """Opens anneal_mjds.txt and returns a list of anneal dates (in MJD)."""
    
    anneal_mjds = []
    with open('anneal_mjds.txt','r') as f:
        anneal_mjds = f.readlines()
     
    anneal_mjds = [item.replace('\n','') for item in anneal_mjds]
        
    return anneal_mjds
    
def get_nearest_anneal_date(mjd,anneal_mjds):
    
    """ For a given MJD, finds the closest anneal date that it falls before.
    
        Parameters
        ----------
        mjd: float
            MJD to compare list of anneal dates to
        anneal_mjds: list of floats
            list of UVIS anneal dates
        
        Returns
        -------
        nearest_anneal_mjd : float
            For input MJD, the date of the nearest UVIS anneal that it falls before.
        
        """

    anneal_mjds = ['0'] + anneal_mjds

    for i in range(len(anneal_mjds)-1):
        if (mjd > float(anneal_mjds[i]))  & (mjd <= float(anneal_mjds[i+1])):
            nearest_anneal_mjd = anneal_mjds[i+1]
            return nearest_anneal_mjd
                
def get_info_new_files(new_files):

    """Opens up each new files and retrieves header information needed for sorting.
    
        Parameters
        ----------
            new_files : list of strings 
                List of paths of all _flt.fits files in the new_data directory.
                
        Returns
        -------
            new_files_info : list of tuples
                For each file path, a tuple containing 
                (file_path, filter, proposal_id, nearest_anneal_mjd, date_obs(iso)).
        
        """
    anneal_mjds = open_anneal_mjd_list()
    new_files_info = []
    
    for f in new_files:
        hdr = fits.open(f)[0].header 
        filter_name = hdr['FILTER']
        prop_id = hdr['PROPOSID']
        date_obs = fits.open(f)[0].header['DATE-OBS']
        t = Time(date_obs,format = 'iso')
        #find nearest anneal date
        nearest_anneal_mjd = get_nearest_anneal_date(t.mjd,anneal_mjds)
        new_files_info.append((f,filter_name,str(prop_id),nearest_anneal_mjd,date_obs))
            
    return new_files_info
    
                
def make_dirs_move_files(new_files_info,data_dir):

    """Opens up each new files and retrieves header information needed for sorting.
    
        Parameters
        ----------
            new_files : list of strings 
                List of paths of all _flt.fits files in the new_data directory.
                
        Returns
        -------
            new_files_info : list of tuples
                For each file path, a tuple containing 
                (file_path, filter, proposal_id, nearest_anneal_mjd, date_obs(iso)).
        
        """
    
    for item in new_files_info:
        file_path, filt, prop_id, nearest_anneal_mjd, date_obs = item
        dest=data_dir+'/{0}/{1}/{2}/{3}'.format(filt,prop_id,nearest_anneal_mjd,date_obs)
        
        if not os.path.isdir(dest):
            os.makedirs(dest)
        
        print('moving',os.path.basename(file_path),'to',dest)
        shutil.move(file_path,dest)

def main_sort_new_data(paths):

    
    new_data_dir,data_dir = paths['new_data_dir'],paths['data_dir']
    new_files = glob.glob(new_data_dir+'/*flt.fits')
    new_files_info = get_info_new_files(new_files)
    make_dirs_move_files(new_files_info,data_dir)
    
if __name__ == '__main__':

    paths = paths()
    main_sort_new_data(paths)   

