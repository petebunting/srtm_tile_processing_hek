from pbprocesstools.pbpt_q_process import PBPTGenQProcessToolCmds
import logging
import os
import glob
import rsgislib


logger = logging.getLogger(__name__)

class GenCmds(PBPTGenQProcessToolCmds):

    def gen_command_info(self, **kwargs):
        if not os.path.exists(kwargs['out_dir']):
            os.mkdir(kwargs['out_dir'])
                
        base_tiles = glob.glob(kwargs['tiles_srch'])

        for tile_img in base_tiles:
            basename = self.get_file_basename(tile_img)
            out_img = os.path.join(kwargs['out_dir'], '{}.tif'.format(basename))
            out_cmp_file = os.path.join(kwargs['out_dir'], '{}.txt'.format(basename))

            if not os.path.exists(out_cmp_file):

                c_dict = dict()
                c_dict['base_img'] = kwargs['tile_img']
                c_dict['srtm_img'] = kwargs['srtm_img']
                c_dict['out_img'] = out_img
                c_dict['out_cmp_file'] = out_cmp_file
                self.params.append(c_dict)


    def run_gen_commands(self):
        self.gen_command_info(tiles_srch='/scratch/a.hek4/srtm/base_overlap_tiles/*.tif',
                              srtm_img='/scratch/a.hek4/srtm/srtm_global_mosaic_1arc_v3.kea',
                              out_dir='/scratch/a.hek4/srtm/srtm_overlap_tiles')

        self.pop_params_db()
        self.create_slurm_sub_sh("create_base_tiles", 16448, '/scratch/a.hek4/srtm/logs',
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
