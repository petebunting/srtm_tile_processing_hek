from pbprocesstools.pbpt_q_process import PBPTQProcessTool
import logging
import os
import shutil
import pathlib
import rsgislib
import rsgislib.imageutils
import rsgislib.imagecalc

logger = logging.getLogger(__name__)

class CreateImageTile(PBPTQProcessTool):

    def __init__(self):
        super().__init__(cmd_name='create_img_tile.py', descript=None)

    def do_processing(self, **kwargs):
        if not os.path.exists(self.params['tmp_dir']):
            os.mkdir(self.params['tmp_dir'])
            
        os.environ["RSGISLIB_IMG_CRT_OPTS_GTIFF"] = "TILED=YES:COMPRESS=LZW"
    
        print("Creating SRTM tile")
        rsgislib.imageutils.resampleImage2Match(self.params['base_img'], self.params['srtm_img'], self.params['out_img'], 'GTIFF', 'cubicspline', datatype=rsgislib.TYPE_16INT, noDataVal=-32768, multicore=False)
        
        print("Check if there is valid data within the SRTM tile")     
        tmp_valid_data_img = os.path.join(self.params['tmp_dir'], "{}_vld_data.tif".format(self.params['basename']))
        band_defns = [rsgislib.imagecalc.BandDefn('srtm', self.params['out_img'], 1)]
        rsgislib.imagecalc.bandMath(tmp_valid_data_img, '(srtm>-500)&&(srtm<9000)?1:0', 'GTIFF', rsgislib.TYPE_8UINT, band_defns)
        vld_count = rsgislib.imagecalc.countPxlsOfVal(tmp_valid_data_img, vals=[1])
        
        if vld_count[0] > 0:
            print("There is valid data - calc stats")
            rsgislib.imageutils.popImageStats(self.params['out_img'], usenodataval=True, nodataval=-32768, calcpyramids=False)
        else:
            print("There is not any valid data - remove image")
            os.remove(self.params['out_img'])
        
        print("Finished")
        pathlib.Path(self.params['out_cmp_file']).touch()
        
        if os.path.exists(self.params['tmp_dir']):
            shutil.rmtree(self.params['tmp_dir'])
        

    def required_fields(self, **kwargs):
        return ["basename", "base_img", "srtm_img", "out_img", "out_cmp_file", "tmp_dir"]

    def outputs_present(self, **kwargs):
        files_dict = dict()
        files_dict[self.params['out_img']] = 'gdal_image'
        files_dict[self.params['out_cmp_file']] = 'file'
        return self.check_files(files_dict)

    def remove_outputs(self, **kwargs):
        # Remove the output files.
        if os.path.exists(self.params['out_img']):
            os.remove(self.params['out_img'])
            
        if os.path.exists(self.params['out_cmp_file']):
            os.remove(self.params['out_cmp_file'])
            
        # Reset the tmp dir
        if os.path.exists(self.params['tmp_dir']):
            shutil.rmtree(self.params['tmp_dir'])
        os.mkdir(self.params['tmp_dir'])

if __name__ == "__main__":
    CreateImageTile().std_run()


