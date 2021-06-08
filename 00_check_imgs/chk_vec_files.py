import osgeo.gdal as gdal
import os
import argparse
import glob


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


def check_gdal_vector_file(gdal_vec):
    """
    A function which checks a GDAL compatible vector file and returns an error message if appropriate.

    :param gdal_vec: the file path to the gdal vector file.
    :return: boolean (True: file OK; False: Error found), string (error message if required otherwise empty string)

    """
    file_ok = True
    err_str = ''
    if os.path.exists(gdal_vec):
        err = RSGISGDALErrorHandler()
        err_handler = err.handler
        gdal.PushErrorHandler(err_handler)
        gdal.UseExceptions()

        try:
            vec_ds = gdal.OpenEx(gdal_vec, gdal.OF_VECTOR)
            if vec_ds is None:
                file_ok = False
                err_str = 'GDAL could not open the data source, returned None.'
            else:
                for lyr_idx in range(vec_ds.GetLayerCount()):
                    vec_lyr = vec_ds.GetLayerByIndex(lyr_idx)
                    if vec_lyr is None:
                        file_ok = False
                        err_str = 'GDAL could not open all the vector layers.'
                        break
            vec_ds = None
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

def deleteFilesWithBasename(filePath):
    """
    Function to delete all the files which have a path
    and base name defined in the filePath attribute.

    """
    import glob
    baseName = os.path.splitext(filePath)[0]
    fileList = glob.glob(baseName+str('.*'))
    for file in fileList:
        print("Removed: {}".format(file))
        os.remove(file)

def _run_vecfile_chk(img_params):
    vec_file = img_params[0]
    rmerr = img_params[1]
    printnames = img_params[2]
    multi_file = img_params[3]

    if printnames:
        print(vec_file)
    try:
        file_ok, err_str = check_gdal_vector_file(vec_file)
        if not file_ok:
            if rmerr:
                if multi_file:
                    deleteFilesWithBasename(vec_file)
                else:
                    os.remove(vec_file)
                    print("Removed {}".format(vec_file))
            else:
                print("rm {}".format(vec_file))
    except:
        if rmerr:
            if multi_file:
                deleteFilesWithBasename(vec_file)
            else:
                os.remove(vec_file)
                print("Removed {}".format(vec_file))
        else:
            print("rm {}".format(vec_file))




if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="A utility which can be used to check whether a GDAL "
                                                  "compatible file is valid and if there are any errors or warnings.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file path")
    parser.add_argument("--rmerr", action='store_true', default=False, help="Delete error files from system.")
    parser.add_argument("--printnames", action='store_true', default=False, help="Print file names as checking")
    parser.add_argument("--multi", action='store_true', default=False, help="For formats which have multiple files "
                                                                            "where all files with the same basename"
                                                                            "will be deleted.")

    args = parser.parse_args()
    print(args.input)

    vec_files = glob.glob(args.input)

    print("File Checks ({} Files Found):".format(len(vec_files)))

    from multiprocessing import Pool
    processes_pool = Pool(1)
    try:
        for vec_file in vec_files:
            try:
                params = [vec_file, args.rmerr, args.printnames, args.multi]
                result = processes_pool.apply_async(_run_vecfile_chk, args=[params])
                result.get(timeout=1)
            except Exception as e:
                if args.rmerr:
                    if args.multi:
                        deleteFilesWithBasename(vec_file)
                    else:
                        os.remove(vec_file)
                        print("Removed {}".format(vec_file))
                else:
                    print("rm {}".format(vec_file))
                continue
        processes_pool.join()
    except Exception as inst:
        print("Finished with pool")

    print("Finish Checks")
