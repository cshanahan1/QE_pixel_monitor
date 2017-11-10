from astropy.io import fits
import glob
import os 
from paths_and_params import paths
from QE_pixel_tools import *

            
def main_make_mean_visit_flats(data_dir):

    dirs = glob.glob(data_dir+'/*')
    filters = [os.path.basename(item) for item in dirs]

    for i, filt in enumerate(filters):
        mjd_dirs = glob.glob(dirs[i]+'/*')
        mjds = [os.path.basename(item) for item in mjd_dirs]
        for i, mjd in enumerate(mjds):
            visit_dirs = glob.glob(mjd_dirs[i] + '/*')
            #print visit_dirs
            for visit_dir in visit_dirs:
                ifiles = glob.glob(visit_dir + '/*flt.fits')
                visit_date = os.path.basename(visit_dir)
                if len(ifiles) > 0:
                    print 'Making mean epoch flat for ' + filt + ', before anneal date ',str(mjd), ' visit date', visit_date
                    sci_arrays,dq_arrays = make_avg_flat_array(ifiles,'mean',[1,2],combine_dq_arrays = True,mask_dq_each = False)
                    mean_array_1, mean_array_2= sci_arrays[0],sci_arrays[1]
                    dq_array_1,dq_array_2 = dq_arrays[0],dq_arrays[1]
                    outfile_path = visit_dir+'/combined_mean_flat_'+filt+'_'+mjd+'_'+visit_date+'.fits'
                    print 'Writing out', outfile_path
                    write_full_frame_uvis_image(mean_array_1,mean_array_2,dq_array_1,dq_array_2,outfile_path)

if __name__ == '__main__':

    data_dir = paths()['data_dir']
    main_make_mean_visit_flats(data_dir)
    

