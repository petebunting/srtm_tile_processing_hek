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
        os.environ["RSGISLIB_IMG_CRT_OPTS_GTIFF"] = "TILED=YES:COMPRESS=LZW"
    
        print("Cutout SRTM Slope")
        band_defns = [rsgislib.imagecalc.BandDefn('base', self.params['base_img'], 1),
                      rsgislib.imagecalc.BandDefn('slope', self.params['slope_img'], 1)]
        rsgislib.imagecalc.bandMath(self.params['out_slope_img'], 'slope', 'GTIFF', rsgislib.TYPE_32FLOAT, band_defns)
        rsgislib.imageutils.popImageStats(self.params['out_slope_img'], usenodataval=False, nodataval=0, calcpyramids=True)
        
        print("Catout SRTM Aspect")
        band_defns = [rsgislib.imagecalc.BandDefn('base', self.params['base_img'], 1),
                      rsgislib.imagecalc.BandDefn('aspect', self.params['aspect_img'], 1)]
        rsgislib.imagecalc.bandMath(self.params['out_aspect_img'], 'aspect', 'GTIFF', rsgislib.TYPE_32FLOAT, band_defns)
        rsgislib.imageutils.popImageStats(self.params['out_aspect_img'], usenodataval=False, nodataval=0, calcpyramids=True)
        

        

    def required_fields(self, **kwargs):
        return ["base_img", "slope_img", "aspect_img", "out_slope_img", "out_aspect_img"]

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


