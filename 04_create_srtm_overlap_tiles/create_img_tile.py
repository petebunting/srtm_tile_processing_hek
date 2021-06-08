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
        rsgislib.imageutils.resampleImage2Match(self.params['base_img'], self.params['srtm_img'], self.params['out_img'], 'GTIFF', 'cubicspline', datatype=rsgislib.TYPE_16INT, noDataVal=-32768, multicore=False)
        
        band_defns = [rsgislib.imagecalc.BandDefn('srtm', self.params['out_img'], 1)]
        prop_valid = rsgislib.imagecalc.calcPropTrueExp('(srtm>-500)&&(srtm<10000?1:0', band_defns)
        if prop_valid > 0:
            rsgislib.imageutils.popImageStats(self.params['out_img'], usenodataval=True, nodataval=-32768, calcpyramids=False)
        else:
            os.remove(self.params['out_img'])
            
        pathlib.Path(self.params['out_cmp_file']).touch()
        

    def required_fields(self, **kwargs):
        return ["base_img", "srtm_img", "out_img", "out_cmp_file"]

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

if __name__ == "__main__":
    CreateImageTile().std_run()


