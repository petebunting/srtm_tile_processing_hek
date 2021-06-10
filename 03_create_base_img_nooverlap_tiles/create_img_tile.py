from pbprocesstools.pbpt_q_process import PBPTQProcessTool
import logging
import os
import shutil
import rsgislib
import rsgislib.imageutils

logger = logging.getLogger(__name__)

class CreateImageTile(PBPTQProcessTool):

    def __init__(self):
        super().__init__(cmd_name='create_img_tile.py', descript=None)

    def do_processing(self, **kwargs):
        rsgis_utils = rsgislib.RSGISPyUtils()
        wkt_str = rsgis_utils.getWKTFromEPSGCode(4326)
        os.environ["RSGISLIB_IMG_CRT_OPTS_GTIFF"] = "TILED=YES:COMPRESS=LZW"
        pxl_res = 0.000277777777778
        width = int((self.params['xmax'] - self.params['xmin']) / pxl_res) + 1
        height = int((self.params['ymax'] - self.params['ymin']) / pxl_res) + 1
        rsgislib.imageutils.createBlankImage(self.params['out_img'], 1, width, height, self.params['xmin'], self.params['ymax'], pxl_res, 0, "", wkt_str, 'GTIFF', rsgislib.TYPE_8UINT)
        rsgislib.imageutils.popImageStats(self.params['out_img'], usenodataval=False, nodataval=0, calcpyramids=False)

    def required_fields(self, **kwargs):
        return ["xmin", "xmax", "ymin", "ymax", "out_img"]

    def outputs_present(self, **kwargs):
        files_dict = dict()
        files_dict[self.params['out_img']] = 'gdal_image'
        return self.check_files(files_dict)

    def remove_outputs(self, **kwargs):
        # Remove the output files.
        if os.path.exists(self.params['out_img']):
            os.remove(self.params['out_img'])

if __name__ == "__main__":
    CreateImageTile().std_run()


