from astropy.io import fits
import glob
import os 
from paths_and_params import paths
from QE_pixel_tools import *

            
def main_make_mean_visit_flats(data_dir):

    visit_dirs = glob.glob(data_dir+'/*/*/*/*')
    
    for visit_dir in visit_dirs:    
        visit_date = os.path.basename(visit_dir)
        mjd = visit_dir.split('/')[-2]
        filt = visit_dir.split('/')[-4]
        ifiles = glob.glob(visit_dir+'/*flt.fits')
        if len(ifiles) > 0:
            print('Making mean epoch flat for ' + filt+ ', visit date', visit_date)
            sci_arrays,dq_arrays = make_avg_flat_array(ifiles,'mean',[1,2],
                                                       combine_dq_arrays = True,
                                                       mask_dq_each = False)
            mean_array_1, mean_array_2= sci_arrays[0],sci_arrays[1]
            dq_array_1,dq_array_2 = dq_arrays[0],dq_arrays[1]
            
            outfile_path = visit_dir+'/mean_flat_'+filt+'_'+mjd+'_'+visit_date+'.fits'
            print('Writing out', outfile_path)
            write_full_frame_uvis_image(mean_array_1,mean_array_2,dq_array_1,dq_array_2,
            							outfile_path)
            
        
if __name__ == '__main__':

    data_dir = paths()['data_dir']
    main_make_mean_visit_flats(data_dir)
