singularity exec --bind /scratch/a.hek4:/scratch/a.hek4 --bind /home/a.hek4:/home/a.hek4 /scratch/a.hek4/swimage/au-eoed-dev.sif python chk_imgs.py --nbands 1 --rmerr -i "/scratch/a.hek4/srtm/srtm_overlap_tiles/*.tif"



