from astropy.io import fits
import numpy as np
import os
import glob
from paths_and_params import *
from QE_pixel_tools import *
import pandas as pd
from astropy.time import Time


def find_anom_pixels(epoch_mean_flat, ideal_median_flat, threshold, lower_bound, 
                     mask_DQ = False, mask_border = True):
                     
    """
    Identifies low QE pixels by comparing mean flat fields from each visit to a 
    median 'ideal' flat field for each filter. 
    
    Updates file that lists x,y pixel positions of identified low QE pixels,
        their % deviation from the ideal flat, and counts on that pixel
    """

    #get data from fits files 
    epoch_sci_arrays, epoch_dq_arrays = open_fits(epoch_mean_flat, [1,2], DQ = True)
    median_sci_arrays, median_dq_arrays = open_fits(ideal_median_flat, [1,2], DQ = True)
    
    sci_1_epoch, sci_2_epoch = epoch_sci_arrays[0],epoch_sci_arrays[1]
    dq_1_epoch, dq_2_epoch = epoch_dq_arrays[0],epoch_dq_arrays[1]
    
    sci_1_median,sci_2_median = median_sci_arrays[0],median_sci_arrays[1]
    dq_1_median,dq_2_median = median_dq_arrays[0],median_dq_arrays[1]

    #optional, mask top and bottom 10 pixels in each chip
    if mask_border:
        sci_1_epoch[0:10], sci_1_epoch[-10:] = np.nan, np.nan
        sci_2_epoch[0:10], sci_2_epoch[-10:] = np.nan, np.nan
        sci_1_median[0:10], sci_1_median[-10:] = np.nan, np.nan
        sci_2_median[0:10], sci_2_median[-10:] = np.nan, np.nan
        if mask_DQ:
            dq_1_epoch[0:10], dq_1_epoch[-10:] = np.nan, np.nan
            dq_2_epoch[0:10], dq_2_epoch[-10:] = np.nan, np.nan
            dq_1_median[0:10], dq_1_median[-10:] = np.nan, np.nan
            dq_2_median[0:10], dq_2_median[-10:] = np.nan, np.nan
            
    #optional, mask science arrays with DQ arrays 
    if mask_DQ:
        sci_1_epoch[dq_1_epoch != 0] = np.nan
        sci_2_epoch[dq_2_epoch != 0] = np.nan
        sci_1_median[dq_1_median != 0] = np.nan
        sci_2_epoch[dq_2_epoch != 0] = np.nan
        
    #find percent difference from median flat 
    dif_sci_1 = ((sci_1_epoch-sci_1_median)/sci_1_median)*100
    dif_sci_2 = ((sci_2_epoch-sci_2_median)/sci_2_median)*100
    
    #find locations and values of anom. pixels
    locs_lowQE_sci1 = np.where((dif_sci_1<threshold) & (dif_sci_1>lower_bound))
    locs_lowQE_sci2 = np.where((dif_sci_2<threshold) & (dif_sci_2>lower_bound))
    #zip coords together
    coords_sci1 = np.column_stack(locs_lowQE_sci1)
    coords_sci2 = np.column_stack(locs_lowQE_sci2)
        
    percent_dev_lowQE_sci1 = dif_sci_1[locs_lowQE_sci1]
    flux_lowQE_sci1=sci_1_epoch[locs_lowQE_sci1]
    percent_dev_lowQE_sci2 = dif_sci_2[locs_lowQE_sci2]
    flux_lowQE_sci2=sci_2_epoch[locs_lowQE_sci2]
    
    #get date info from file path       
    split_path = epoch_mean_flat.split('/')[-1]
    split_path = split_path.replace('.fits','')
    split_path = split_path.split('_')
    
    anneal_date = split_path[-2]
    date_obs = split_path[-1]
        
    output_dir = ideal_median_flat.replace(os.path.basename(ideal_median_flat),'results/')
    filt = output_dir.split('/')[-3]
    output_path = output_dir+'combined_masked_{}_{}_{}_{}_{}.dat'.format(filt,str(anneal_date),str(date_obs),str(threshold),str(lower_bound))
    
    #write out data file
    with open(output_path,'w') as f:
        print 'writing out',output_path
        f.write('#chip,xc,yc,percent_dev,counts\n')
        for i,coords in enumerate(coords_sci1):
            f.write('{},{},{},{},{}\n'.format('1',coords[0],coords[1],\
            percent_dev_lowQE_sci1[i],flux_lowQE_sci1[i]))
        for i,coords in enumerate(coords_sci2):
            f.write('{},{},{},{},{}\n'.format('2',coords[0],coords[1],\
            percent_dev_lowQE_sci2[i],flux_lowQE_sci2[i]))


    """#write out mask
    chip_1_mask = np.zeros(sci_1_epoch.shape)
    chip_1_mask[locs_lowQE_sci1] = 1
    chip_2_mask = np.zeros(sci_2_epoch.shape)
    chip_2_mask[locs_lowQE_sci2] = 1
    outfile_path = output_dir + 'combined_masked_{}_{}_{}_{}_{}_QE_pixel_mask.fits'.format(filt,anneal_date,date_obs,str(threshold),str(lower_bound))
    
    print 'writing out',outfile_path
    write_full_frame_uvis_image(chip_1_mask, chip_2_mask, dq_1_epoch,
                                dq_2_epoch, outfile_path, overwrite=True)"""
                                
            
def main_find_anom_pixels(data_dir,mask_DQ = False, mask_border = True):

    filter_dirs = glob.glob(data_dir+'/*')
    filters = [os.path.basename(item) for item in filter_dirs]
    
    anneal_date_dirs = glob.glob(data_dir+'/*/*')
    anneal_dates = [os.path.basename(item) for item in anneal_date_dirs]
    
    visit_date_dirs = glob.glob(data_dir+'/*/*') 
    
    for i,filter_dir in enumerate(filter_dirs):
    
        ideal_median_flat = glob.glob(filter_dir+'/*combined*median*')[0]

        epoch_mean_flats=glob.glob(data_dir+'/{}/*/*/*combined*mean*'.format(filters[i]))
        
        thresholds = [-1.0,-2.0,-3.0,-4.0,-5.0]
        lower_bounds = [-10.0,-7.0,-6.0]
        for epoch_mean_flat in epoch_mean_flats:
            for threshold in thresholds:
                for lower_bound in lower_bounds:
                    print 'threshold:',threshold
                    print 'lower bound:',lower_bound
        
                    find_anom_pixels(epoch_mean_flat, ideal_median_flat, threshold, lower_bound, \
                    mask_DQ = True, mask_border = mask_border)

if __name__ == '__main__':

    data_dir = paths()['data_dir']
    
    main_find_anom_pixels(data_dir,mask_DQ = False, mask_border = True)
    

    
    
    
    
        
    
    


