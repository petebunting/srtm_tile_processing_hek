from pbprocesstools.pbpt_q_process import PBPTGenQProcessToolCmds
import logging
import os
import glob
import rsgislib


logger = logging.getLogger(__name__)

class GenCmds(PBPTGenQProcessToolCmds):

    def gen_command_info(self, **kwargs):
        if not os.path.exists(kwargs['out_asp_dir']):
            os.mkdir(kwargs['out_asp_dir'])
        if not os.path.exists(kwargs['out_slp_dir']):
            os.mkdir(kwargs['out_slp_dir'])
                
        base_tiles = glob.glob(kwargs['tiles_srch'])

        for tile_img in base_tiles:
            basename = self.get_file_basename(tile_img)
            
            base_tile_img = os.path.join(kwargs['nooverlap_base'], '{}.tif'.format(basename))

            slope_img = os.path.join(kwargs['slp_dir'], '{}_slope.tif'.format(basename))
            aspect_img = os.path.join(kwargs['asp_dir'], '{}_aspect.tif'.format(basename))

            out_slope_img = os.path.join(kwargs['out_slp_dir'], '{}_slope.tif'.format(basename))
            out_aspect_img = os.path.join(kwargs['out_asp_dir'], '{}_aspect.tif'.format(basename))

            if (not os.path.exists(out_slope_img)) or (not os.path.exists(out_aspect_img)):
                print('rm {}'.format(slope_img))
                print('rm {}'.format(aspect_img))
                c_dict = dict()
                c_dict['base_img'] = base_tile_img
                c_dict['slope_img'] = slope_img
                c_dict['aspect_img'] = aspect_img
                c_dict['out_slope_img'] = out_slope_img
                c_dict['out_aspect_img'] = out_aspect_img
                self.params.append(c_dict)


    def run_gen_commands(self):
        self.gen_command_info(tiles_srch='/scratch/a.hek4/srtm/srtm_overlap_tiles/*.tif',
                              nooverlap_base='/scratch/a.hek4/srtm/base_nooverlap_tiles',
                              asp_dir='/scratch/a.hek4/srtm/srtm_aspect_overlap_tiles',
                              slp_dir='/scratch/a.hek4/srtm/srtm_slope_overlap_tiles',
                              out_asp_dir='/scratch/a.hek4/srtm/srtm_aspect_nooverlap_tiles',
                              out_slp_dir='/scratch/a.hek4/srtm/srtm_slope_nooverlap_tiles')

        self.pop_params_db()
        self.create_slurm_sub_sh("calc_slp_asp_nooverlap_tiles", 16448, '/scratch/a.hek4/srtm/logs',
                                 run_script='run_exe_analysis.sh', job_dir="job_scripts",
                                 db_info_file='lcl_db_process_info.txt', 
                                 n_cores_per_job=10, n_xtr_cmds=10, n_jobs=10,
                                 job_time_limit='2-23:59',
                                 module_load='module load parallel singularity\n\n')

if __name__ == "__main__":
    py_script = os.path.abspath("create_img_tile.py")
    script_cmd = "singularity exec --bind /scratch/a.hek4:/scratch/a.hek4 --bind /home/a.hek4:/home/a.hek4 /scratch/a.hek4/swimage/au-eoed-dev.sif python {}".format(py_script)

    process_tools_mod = 'create_img_tile'
    process_tools_cls = 'CreateImageTile'

    create_tools = GenCmds(cmd=script_cmd, db_conn_file="/home/a.hek4/pbpt_db_info.txt",
                                         lock_file_path="./srtm_pbpt_lock_file.txt",
                                         process_tools_mod=process_tools_mod, process_tools_cls=process_tools_cls)
    create_tools.parse_cmds()
