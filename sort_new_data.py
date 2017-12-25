from astropy.io import fits 
import glob
from paths_and_params import *
import os
import shutil

def get_new_files(new_data_dir):
    """Obtains the full paths to all new _flt.fits files in the new_data directory.
    
        Parameters:
            new_data_dir: string
                Location of the directory where new data is placed.
        Returns:
            new_files : list of strings
                List of paths of all _flt.fits files in the new_data directory.
    """
    
    new_files = glob.glob(new_data_dir+'/*flt.fits')
    
    return new_files

def info_new_files(new_files):
    """Opens up each new files and retrieves header information needed for sorting.
    
        Parameters:
            new_files : list of strings 
                List of paths of all _flt.fits files in the new_data directory.
                
        Returns:
            new_files_info : list of tuples
                For each new file path, a tuple containint (file path, filter).
        
        """
    new_files_info = []
    for f in new_files:
        hdr = fits.open(f)[0].header 
        filter_name = hdr['FILTER']
        prop_id = hdr['PROPOSID']
        #print f, filter_name
        new_files_info.append((f,filter_name,str(prop_id)))
            
    return new_files_info

def sort_files(new_files_info,data_dir):

    """Sorts new files into subdirectories by filter. Creates filter subdirectory
        if it does not exsit alread in the data directory (i.e first time running this).
    
        Parameters:
            new_files_info : list of tuples
                For each new file path, a tuple containint (file path, filter).
        
    """
    
    for f in new_files_info:
        fname, filter_name, proposid = f[0], f[1], f[2]
        dest = data_dir + '/{}/{}'.format(proposid,filter_name)
        if not os.path.isdir(dest):
            print 'Making directory ' + dest
            os.makedirs(dest)
        shutil.move(fname, dest)
        print 'Moving ' + os.path.basename(fname) + ' to ' + dest
    

def main_sort_new_data(data_dir,new_data_dir):

    new_files = get_new_files(new_data_dir)
    print len(new_files), ' new files'
    new_files_info = info_new_files(new_files)
    sort_files(new_files_info,data_dir)
    
    

if __name__ == "__main__":
    
    paths = paths()
    data_dir, new_data_dir = paths['data_dir'],paths['new_data_dir']
    main_sort_new_data(data_dir,new_data_dir)
    
        
    
    
    
    
                
            
        
            
            
                
    
    
    
    
    
        