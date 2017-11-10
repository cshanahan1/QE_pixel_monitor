from download_new_anneal_file import *
from paths_and_params import paths
from make_median_filter_flats import *
from make_mean_visit_flats import *
from sort_new_data import *
from group_files_by_date import *

def main_run_QE_pixels(paths):

    #unpack paths
    data_dir, new_data_dir = paths['data_dir'],paths['new_data_dir']
    
    #download most recent anneal date file, update anneal_dates.txt
    main_update_anneal_file()
    
    #sort files in new_data dir into subdirectories by filter
    main_sort_new_data(data_dir,new_data_dir)
    
    #group new files in filter subdirectories by nearest anneal date
    main_group_files_by_date(data_dir)
    
    #make ideal median flats for each filter, median combining all observations
    main_make_median_flats(data_dir)
    
    #make mean flat for each filter/epoch of data
    main_make_mean_visit_flats(data_dir)
    
    #mask pixels in median / mean flats with DQ array 
    
    

if __name__ == '__main__':
    pathss = paths()
    main_run_QE_pixels(pathss)
    