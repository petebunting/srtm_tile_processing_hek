find /scratch/a.hek4/srtm/srtm_aspect_nooverlap_tiles -type f > srtm_aspect_files.txt

singularity exec --bind /scratch/a.hek4:/scratch/a.hek4 --bind /home/a.hek4:/home/a.hek4 /scratch/a.hek4/swimage/au-eoed-dev.sif gdalbuildvrt -input_file_list srtm_aspect_files.txt /scratch/a.hek4/srtm/srtm_aspect_global_mosaic_1arc_v3.vrt 

find /scratch/a.hek4/srtm/srtm_slope_nooverlap_tiles -type f > srtm_slope_files.txt

singularity exec --bind /scratch/a.hek4:/scratch/a.hek4 --bind /home/a.hek4:/home/a.hek4 /scratch/a.hek4/swimage/au-eoed-dev.sif gdalbuildvrt -input_file_list srtm_slope_files.txt /scratch/a.hek4/srtm/srtm_slope_global_mosaic_1arc_v3.vrt 


