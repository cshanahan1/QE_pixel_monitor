from astropy.io import fits
import numpy as np
import os
import copy

def open_fits(ifile, chips, DQ = False):

    """Opens fits file, returns science arrays (and DQ arrays, if DQ = True,
        from specified UVIS chips.
        
        Parameters
        ----------
        
        ifile: string
            Path to input file.
            
        chips: list of ints
            List of UVIS chips.
            
        Returns
        -------
        if DQ = True:
        
            sci_arrays: Tuple of array(s).
                List containing science arrays from desired UVIS chips, in the order
                they were provided. 
                
        if DQ = False
        
            sci_arrays: Tuple of array(s).
                List containing science arrays from desired UVIS chips, in the order
                they were provided. 
                
        
        """
    
    hdu_list = fits.open(ifile)
    
    #print 'opening ' + os.path.basename(ifile)
    
    sci_arrays = []
    DQ_arrays = []
        
    for chip in chips:
        sci_array_chip = hdu_list['SCI',chip].data
        sci_arrays.append(sci_array_chip)
        if DQ:
            DQ_array_chip = hdu_list['DQ',chip].data
            DQ_arrays.append(DQ_array_chip)
        
    hdu_list.close()
        
    if DQ:
        return (sci_arrays,DQ_arrays)
    else:
        return sci_arrays
    
    
def make_avg_flat_array(ifiles,avg_type,chips,combine_dq_arrays = False, mask_dq_each = False):

    """Makes a median or mean image for input files. Assumes images are full frame 
    UVIS images, and returns a median or mean image for each chip. 
    
    If desired, DQ array is generated from all the DQ arrays of the 
    combined files - a flag is set for a pixel if that pixel was flagged in ANY of the 
    input images.
              
        Parameters
        ----------
        filt: string
            Filter.
            
        mjd: string
            Closest anneal date that files were taken before.
        
        ifiles: list of string
            Paths to input files.
            
        Returns
        -------
        
        median_flat_arrays: tuple of arrays
            Tuple containing the median image for (chip 1, chip 2) 
        
        """
    
    #sort order of chips so they are ascending...
    chips = sorted(chips)

    #initialize an empty array for each chip
    test_hdu = fits.open(ifiles[0])
    test_sci_ar = test_hdu['SCI',chips[0]].data
    dims = test_sci_ar.shape
    test_hdu.close()
    
    avg_array_chips = np.zeros((len(chips),len(ifiles),dims[0],dims[1]))
    DQ_array_chips = np.zeros((len(chips),dims[0],dims[1]),dtype=np.int16)

    #fill up empty data cube 
    for i, filee in enumerate(ifiles):
        sci_arrays,dq_arrays = open_fits(filee,chips,DQ=True)  
        for j in range(len(sci_arrays)):
            tmp = np.copy(sci_arrays[j])
            if mask_dq_each:
                tmp[DQ_array_chips[j] != 0] = np.nan
            avg_array_chips[j][i] = tmp
            if combine_dq_arrays:

                DQ_array_chips[j] = DQ_array_chips[j] | dq_arrays[j]

  #make average image (median or mean)
    if avg_type == 'median':
        print('computing median of {} images...'.format(str(len(ifiles))))
        median_arrs = [np.median(arr, axis=0) for arr in avg_array_chips]
        return (median_arrs,DQ_array_chips)

    if avg_type == 'mean':
        print('computing mean of {} images'.format(str(len(ifiles))))

        mean_arrs = [np.mean(arr, axis=0) for arr in avg_array_chips]

        return (mean_arrs,DQ_array_chips)

            
    else:
        print("Please specify method of average ('mean' or 'median').")
    
    
def write_full_frame_uvis_image(sci_array_chip1, sci_array_chip2, dq_array_chip1,
                                dq_array_chip2, outfile_path, overwrite=True):
                                
    pri=fits.PrimaryHDU() # dummy primary extension
    
    hdu = fits.ImageHDU(sci_array_chip1)
    hdu.header['EXTNAME'] = 'SCI'
    hdu.header['EXTVER'] = 1
    
    hdu2 = fits.ImageHDU(dq_array_chip1)
    hdu2.header['EXTNAME'] = 'DQ'
    hdu2.header['EXTVER'] = 1
    
    hdu3 = fits.ImageHDU(sci_array_chip2)
    hdu3.header['EXTNAME'] = 'SCI'
    hdu3.header['EXTVER'] = 2
    
    hdu4 = fits.ImageHDU(dq_array_chip2)
    hdu4.header['EXTNAME'] = 'DQ'
    hdu4.header['EXTVER'] = 2
    
    #DQ arrays
    
    hdulist = fits.HDUList([pri,hdu,hdu2,hdu3,hdu4])
    hdulist.writeto(outfile_path,overwrite=overwrite) 