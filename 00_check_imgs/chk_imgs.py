import osgeo.gdal as gdal
import osgeo.osr as osr
import numpy
import os
import argparse
import glob

def check_hdf5_file(input_file):
    """
    A function which checks whether a HDF5 file is valid.
    :param input_file: the file path to the input file.
    :return: a boolean - True file is valid. False file is not valid.

    """
    import h5py

    def _check_h5_var(h5_obj):
        lcl_ok = True
        try:
            if isinstance(h5_obj, h5py.Dataset):
                lcl_ok = True
            elif isinstance(h5_obj, h5py.Group):
                for var in h5_obj.keys():
                    lcl_ok = _check_h5_var(h5_obj[var])
                    if not lcl_ok:
                        break
        except RuntimeError:
            lcl_ok = False
        return lcl_ok
    
    glb_ok = True
    if not os.path.exists(input_file):
        glb_ok = False
    else:
        fH5 = h5py.File(input_file, 'r')
        if fH5 is None:
            glb_ok = False
        else:
            for var in fH5.keys():
                glb_ok = _check_h5_var(fH5[var])
                if not glb_ok:
                    break
    return glb_ok


class RSGISGDALErrorHandler(object):
    """
    A class representing a generic GDAL Error Handler which
    can be used to pick up GDAL warnings rather than just
    failure errors.
    """

    def __init__(self):
        """
        Init for RSGISGDALErrorHandler. Class attributes are err_level, err_no and err_msg

        """
        from osgeo import gdal
        self.err_level = gdal.CE_None
        self.err_no = 0
        self.err_msg = ''

    def handler(self, err_level, err_no, err_msg):
        """
        The handler function which is called with the error information.

        :param err_level: The level of the error
        :param err_no: The error number
        :param err_msg: The message (string) associated with the error.

        """
        self.err_level = err_level
        self.err_no = err_no
        self.err_msg = err_msg


def check_gdal_image_file(gdal_img, check_bands=True, nbands=0, chk_proj=False, epsg_code=0, read_img=False):
    """
    A function which checks a GDAL compatible image file and returns an error message if appropriate.

    :param gdal_img: the file path to the gdal image file.
    :param check_bands: boolean specifying whether individual image bands should be
                        opened and checked (Default: True)
    :param nbands: int specifying the number of expected image bands. Ignored if 0; Default is 0.
    :param chk_proj: boolean specifying whether to check that the projection has been defined.
    :param epsg_code: int for the EPSG code for the projection. Error raised if image is not that projection.
    :param read_img: boolean specifying whether to try reading some image pixel values from the image. 
                     This option will read 10 random image pixel values from a randomly selected band.
    :return: boolean (True: file ok; False: Error found), string (error message if required otherwise empty string)

    """
    file_ok = True
    err_str = ''
    if os.path.exists(gdal_img):
        err = RSGISGDALErrorHandler()
        err_handler = err.handler
        gdal.PushErrorHandler(err_handler)
        gdal.UseExceptions()
        try:
            if os.path.splitext(gdal_img)[1].lower() == '.kea':
                file_ok = check_hdf5_file(gdal_img)
                if not file_ok:
                    err_str = "Error with KEA/HDF5 file."
            if file_ok:
                raster_ds = gdal.Open(gdal_img, gdal.GA_ReadOnly)
                if raster_ds is None:
                    file_ok = False
                    err_str = 'GDAL could not open the dataset, returned None.'

                if file_ok and (nbands > 0):
                    n_img_bands = raster_ds.RasterCount
                    if n_img_bands != nbands:
                        file_ok = False
                        err_str = 'Image should have {} image bands but {} found.'.format(nbands, n_img_bands)
                        
                if file_ok and check_bands:
                    n_img_bands = raster_ds.RasterCount
                    if n_img_bands < 1:
                        file_ok = False
                        err_str = 'Image says it does not have any image bands.'
                    else:
                        for n in range(n_img_bands):
                            band = n + 1
                            img_band = raster_ds.GetRasterBand(band)
                            if img_band is None:
                                file_ok = False
                                err_str = 'GDAL could not open band {} in the dataset, returned None.'.format(band)
                                break
                        
                if file_ok and chk_proj:
                    proj_obj = raster_ds.GetProjection()
                    if proj_obj is None:
                        file_ok = False
                        err_str = 'Image projection is None.'
                    elif proj_obj is '':
                        file_ok = False
                        err_str = 'Image projection is empty.'
                    
                    if file_ok and (epsg_code > 0)                    
                        spat_ref = osr.SpatialReference()
                        spat_ref.ImportFromWkt(proj_obj)            
                        spat_ref.AutoIdentifyEPSG()
                        img_epsg_code = spat_ref.GetAuthorityCode(None)
                        if img_epsg_code is None:
                            file_ok = False
                            err_str = 'Image projection returned a None EPSG code.'
                        elif img_epsg_code != epsg_code
                            file_ok = False
                            err_str = 'Image EPSG ({}) does not match that specified ({})'.format(img_epsg_code, epsg_code)
                            
                if file_ok and read_img:
                    n_img_bands = raster_ds.RasterCount
                    xSize = rasterDS.RasterXSize
                    ySize = rasterDS.RasterYSize
                    
                    if n_img_bands == 1:
                        band = 1
                    else:
                        band = numpy.random.randint(1, high=n_img_bands, size=1)
       
                    img_band = raster_ds.GetRasterBand(band)
                    x_pxls = numpy.random.choice(xSize, 10)
                    y_pxls = numpy.random.choice(ySize, 10)
                    for i in range(10):
                        #print("[{},{}]".format(x_pxls[i], y_pxls[i]))
                        img_data = img_band.ReadRaster(xoff=x_pxls[i], yoff=y_pxls[i], xsize=1, ysize=1, buf_xsize=1, buf_ysize=1, buf_type=gdal.GDT_Float32)
                
                raster_ds = None
        except Exception as e:
            file_ok = False
            err_str = str(e)
        else:
            if err.err_level >= gdal.CE_Warning:
                file_ok = False
                err_str = str(err.err_msg)
        finally:
            gdal.PopErrorHandler()
    else:
        file_ok = False
        err_str = 'File does not exist.'
    return file_ok, err_str

def _run_img_chk(img_params):
    img = img_params[0]
    nbands = img_params[1]
    rmerr = img_params[2]
    printnames = img_params[3]
    chk_proj = img_params[4]
    epsg_code = img_params[5]
    read_img = img_params[6]
    
    if printnames:
        print(img)
    try:
        file_ok, err_str = check_gdal_image_file(img, check_bands=True, nbands=nbands, chk_proj=chk_proj, epsg_code=epsg_code, read_img=read_img)
        if not file_ok:
            if rmerr:
                os.remove(img)
                print("Removed {}".format(img))
            else:
                print("rm {}".format(img))
    except:
        if rmerr:
            os.remove(img)
            print("Removed {}".format(img))
        else:
            print("rm {}".format(img))


if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="A utility which can be used to check whether a GDAL "
                                                  "compatible file is valid and if there are any errors or warnings.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file path")
    parser.add_argument("--rmerr", action='store_true', default=False, help="Delete error files from system.")
    parser.add_argument("--printnames", action='store_true', default=False, help="Print file names as checking")
    parser.add_argument("--nbands", type=int, default=0, help="Check the number of bands is correct. Ignored if 0; Default.")
    parser.add_argument("--epsg", type=int, default=0, help="The EPSG code for the projection of the images.")
    parser.add_argument("--chkproj", action='store_true', default=False, help="Check that a projection is defined")
    parser.add_argument("--readimg", action='store_true', default=False, help="Check the image by reading part of it.")
    

    args = parser.parse_args()
    print(args.input)
    
    chk_projection = args.chkproj
    if (not args.chkproj) and (args.epsg > 0):
        chk_projection = True
    
    
    imgs = glob.glob(args.input)

    print("File Checks ({} Files Found):".format(len(imgs)))

    from multiprocessing import Pool
    processes_pool = Pool(1)
    try:
        for img in imgs:
            try:
                params = [img, args.nbands, args.rmerr, args.printnames, chk_projection, args.epsg, args.readimg]
                result = processes_pool.apply_async(_run_img_chk, args=[params])
                result.get(timeout=2)
            except Exception as e:
                if args.rmerr:
                    os.remove(img)
                    print("Removed {}".format(img))
                else:
                    print("rm {}".format(img))
                continue
        processes_pool.join()
    except Exception as inst:
        print("Finished with pool")

    print("Finish Checks")
