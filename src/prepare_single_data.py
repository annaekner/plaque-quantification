import hydra
import logging
import shutil

from segment_lad import extract_lad_from_full_tree
from load_save_utilities import load_sample, save_resampled_img, save_segmentation, save_distance_map, copy_centerline_vtk_file
from tools import compute_centerline_distance_map

# Set up logging
log = logging.getLogger(__name__)

@hydra.main(config_path="../conf", config_name="config.yaml", version_base="1.3.2")
def main(config):
    
    # TODO: These two variables need to be set!
    index = 64          # Set the index (in file_list.txt) of the sample to load
    subset = 'train'    # Set subset to either 'train' or 'test'

    # Load the sample
    sample = load_sample(index, config, subset)
    img_index = sample['image_index']

    # 1. Save the resampled image
    save_resampled_img(img_index, config, subset)

    # # 2. Save LAD segmentation from full coronary tree
    lad_segmentation = extract_lad_from_full_tree(sample, config)
    save_segmentation(lad_segmentation, sample, config, subset)

    # # 3. Save the centerline distance map
    distance_map = compute_centerline_distance_map(sample)
    save_distance_map(distance_map, sample, config, subset)

    # 4. Copy centerline VTK file to centerlines directory
    copy_centerline_vtk_file(img_index, config)
    
if __name__ == "__main__":
    main()