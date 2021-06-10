from pbprocesstools.pbpt_q_process import PBPTQProcessTool
import logging
import os
import shutil
import pathlib
import rsgislib
import rsgislib.imageutils
import rsgislib.elevation
import subprocess

logger = logging.getLogger(__name__)

class CreateImageTile(PBPTQProcessTool):

    def __init__(self):
        super().__init__(cmd_name='create_img_tile.py', descript=None)

    def do_processing(self, **kwargs):
        os.environ["RSGISLIB_IMG_CRT_OPTS_GTIFF"] = "TILED=YES:COMPRESS=LZW"
    
        print("Calculate SRTM Slope")
        #rsgislib.elevation.slope(self.params['srtm_img'], self.params['out_slope_img'], 'degrees', 'GTIFF')
        cmd = 'gdaldem slope -of GTIFF -co "TILED=YES" -co "COMPRESS=LZW" -s 111120 -compute_edges {} {}'.format(self.params['srtm_img'], self.params['out_slope_img'])
        subprocess.call(cmd, shell=True)
        rsgislib.imageutils.popImageStats(self.params['out_slope_img'], usenodataval=True, nodataval=-9999, calcpyramids=True)
        
        print("Calculate SRTM Aspect")
        rsgislib.elevation.aspect(self.params['srtm_img'], self.params['out_aspect_img'], 'GTIFF')
        rsgislib.imageutils.popImageStats(self.params['out_aspect_img'], usenodataval=False, nodataval=-32768, calcpyramids=True)
        

        

    def required_fields(self, **kwargs):
        return ["srtm_img", "out_slope_img", "out_aspect_img"]

    def outputs_present(self, **kwargs):
        files_dict = dict()
        files_dict[self.params['out_slope_img']] = 'gdal_image'
        files_dict[self.params['out_aspect_img']] = 'gdal_image'
        return self.check_files(files_dict)

    def remove_outputs(self, **kwargs):
        # Remove the output files.
        if os.path.exists(self.params['out_slope_img']):
            os.remove(self.params['out_slope_img'])
            
        if os.path.exists(self.params['out_aspect_img']):
            os.remove(self.params['out_aspect_img'])


if __name__ == "__main__":
    CreateImageTile().std_run()


