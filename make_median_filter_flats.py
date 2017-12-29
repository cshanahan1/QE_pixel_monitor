from astropy.io import fits
import glob
import os 
from paths_and_params import paths
from QE_pixel_tools import *
#5 files from 13585
#2 files from 13169

def write_temp_split_files(ifiles):
    """To avoid running out of memory, when trying to combine more than ~150 images,
        create temporary files that split the full frame into pieces, combine them 
        piecewise. This functionality assumes disk space is not limited so that temp
        files can be all created at once, then deleted. 
        
        Full frame UVIS images are split into 8 pieces, each chip into quarters."""
        
    for fnumber, ifile in enumerate(ifiles):
    
        print fnumber,'of',len(ifiles)
        
        sci_arrays, dq_arrays = open_fits(ifile,[1,2],DQ = True)
        ch1, ch2 = sci_arrays[0],sci_arrays[1]
        dq1,dq2 = dq_arrays[0],dq_arrays[1]
        
        #split each chip in 2 pieces
        
        sci_arrays = (ch1[0:1025,0:2048],ch1[0:1025,2048:],ch1[1025:,0:2048],ch1[1025:,2048:],
                  ch2[0:1025,0:2048],ch2[0:1025,2048:],ch2[1025:,0:2048],ch2[1025:,2048:])
                  
        dq_arrays = (dq1[0:1025,0:2048],dq1[0:1025,2048:],dq1[1025:,0:2048],dq1[1025:,2048:],
                  dq2[0:1025,0:2048],dq2[0:1025,2048:],dq2[1025:,0:2048],dq2[1025:,2048:])
                  
        
        #write out temporary files
        
        sections = [('_chip{0}_{1}'.format(i,j),i) for i in ('1','2') \
                    for j in ('A','B','C','D')]
        
        for i, ar in enumerate(sci_arrays):
            temp_path = ifile.replace('_flt.fits','') + sections[i][0]+'.temp'
            chip = int(sections[i][1])
            
            dq_ar = dq_arrays[i]
            
            #if not os.path.isfile(temp_path):
            if True:
                pri = fits.PrimaryHDU() #dummy primary extension
                
                hdu1 = fits.ImageHDU(ar)
                hdu1.header['EXTNAME'] = 'SCI'
                hdu1.header['EXTVER'] = int(chip)
                
                hdu2 = fits.ImageHDU(dq_ar)
                hdu2.header['EXTNAME'] = 'DQ'
                hdu2.header['EXTVER'] = int(chip)
    
                #print 'writing out file to', temp_path
                hdulist = fits.HDUList([pri,hdu1,hdu2])
                hdulist.writeto(temp_path,overwrite=True) 
            else:
                pass
                #print 'temp file already exists'

def log_file_names(ifile_paths,log_file_outfile_path):
    """Creates a log file of the rootnames of files that went in to making the meadian
        flat for each filter."""
        
    rootnames = [os.path.basename(f) for f in ifile_paths]
        
    print 'Logging files used to create median flat.'
    with open(log_file_outfile_path,'a') as f:
        for rootname in rootnames:
            f.write(rootname+'\n')
                   
def remove_temp_files():
    pass
            
def main_make_median_flats(data_dir,prop_ids = 'all'):
    
    if prop_ids == 'all':
        print 'Making median filter flat from all proposals.'
        dirs = glob.glob(data_dir+'/*/*/*/*')
    
    else:
        print 'Making median filter flat from proposals ', prop_ids
        dirs = []
        for id in prop_ids:
            dirs += glob.glob(data_dir+'/'+(str(id))+'/*/*/*')

    
    filters = [os.path.basename(item) for item in dirs]

    for i, filt in enumerate(filters):
    
        print 'filt',filt
    
        print dirs[i]
        
        ifiles = []
        for dir in dirs:
            if filt in dir:
                ifiles += glob.glob(dir+'/*/*/*')
        print ifiles
        
        
        """if len(ifiles) > 0:
            if len(ifiles) < 150:
                print 'Making median filter flat for ' + filt +'. Using {} files'.format(len(ifiles))
                sci_arrays,dq_arrays = make_avg_flat_array(ifiles,'median',[1,2],combine_dq_arrays = True,mask_dq_each = False)
                median_array_1, median_array_2= sci_arrays[0],sci_arrays[1]
                dq_array_1,dq_array_2 = dq_arrays[0],dq_arrays[1]

            else:
                print 'Making median filter flat for ' + filt +'. Using {} files. Creating temporary spliced files before combining.'.format(len(ifiles))
                write_temp_split_files(ifiles)
                print 'All temp files created.'
                
                ifiles_chip1A = glob.glob(dirs[i]+'/*/*/*chip1_A*.temp')
                ifiles_chip1B = glob.glob(dirs[i]+'/*/*/*chip1_B*.temp')
                ifiles_chip1C = glob.glob(dirs[i]+'/*/*/*chip1_C*.temp')
                ifiles_chip1D = glob.glob(dirs[i]+'/*/*/*chip1_D*.temp')
                
                ifiles_chip2A = glob.glob(dirs[i]+'/*/*/*chip2_A*.temp')
                ifiles_chip2B = glob.glob(dirs[i]+'/*/*/*chip2_B*.temp')
                ifiles_chip2C = glob.glob(dirs[i]+'/*/*/*chip2_C*.temp')
                ifiles_chip2D = glob.glob(dirs[i]+'/*/*/*chip2_D*.temp')
                
                m1A,dq1A = make_avg_flat_array(ifiles_chip1A,'median',[1],
                           combine_dq_arrays = True,mask_dq_each = False)
                m1B,dq1B= make_avg_flat_array(ifiles_chip1B,'median',[1],
                          combine_dq_arrays = True,mask_dq_each = False)
                m1C,dq1C= make_avg_flat_array(ifiles_chip1C,'median',[1],
                          combine_dq_arrays = True,mask_dq_each = False)
                m1D,dq1D= make_avg_flat_array(ifiles_chip1D,'median',[1],
                          combine_dq_arrays = True,mask_dq_each = False)
                
                m2A,dq2A = make_avg_flat_array(ifiles_chip2A,'median',[2],
                           combine_dq_arrays = True,mask_dq_each = False)
                m2B,dq2B = make_avg_flat_array(ifiles_chip2B,'median',[2],
                           combine_dq_arrays = True,mask_dq_each = False)
                m2C,dq2C = make_avg_flat_array(ifiles_chip2C,'median',[2],
                           combine_dq_arrays = True,mask_dq_each = False)
                m2D,dq2D = make_avg_flat_array(ifiles_chip2D,'median',[2],
                           combine_dq_arrays = True,mask_dq_each = False)

                #recombine to full frame to write out 
                median_array_1 = np.hstack((np.vstack((m1A[0],m1C[0])),np.vstack((m1B[0],m1D[0]))))
                median_array_2 = np.hstack((np.vstack((m2A[0],m2C[0])),np.vstack((m2B[0],m2D[0]))))
                
                dq_array_1 = np.hstack((np.vstack((dq1A[0],dq1C[0])),np.vstack((dq1B[0],dq1D[0]))))
                dq_array_2 = np.hstack((np.vstack((dq2A[0],dq2C[0])),np.vstack((dq2B[0],dq2D[0]))))
                
                #remove temporary files 
                print 'Removing temporary spliced files'
                all_temp =ifiles_chip1A+ifiles_chip1B+ifiles_chip2A+ifiles_chip2B
                print all_temp
                
                for item in all_temp:
                    os.remove(item)           
                
            outfile_path = dirs[i]+'/combined_maskedDQ_flat_{}_median_flat.fits'.format(filt)
            print 'Writing out', outfile_path
            
            #make log of files that went into making median flat
            log_file_outfile_path = dirs[i]+'median_flat_log_file.txt'
            with open(log_file_outfile_path,'w') as f:
                f.write('List of files used to create {}.'.format(log_file_outfile_path))
            log_file_names(ifiles,log_file_outfile_path)

            write_full_frame_uvis_image(median_array_1,median_array_2,dq_array_1,dq_array_2,outfile_path)"""
                

if __name__ == '__main__':

    data_dir = paths()['data_dir']
    main_make_median_flats(data_dir,prop_ids='all')
    

