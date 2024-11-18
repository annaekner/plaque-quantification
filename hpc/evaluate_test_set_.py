import json
import logging
import numpy as np

import tools

def evaluate_test_set(config, log, iteration):

    # Configuration settings
    base_dir = config.base_settings.base_dir
    version = config.base_settings.version
    dataset_name = config.dataset_settings.dataset_name
    seed = config.base_settings.seed
    num_samples_test = config.test_settings.num_samples_test

    data_iterations_dir = config.data_iterations.dir
    iterations_evaluations_dir = config.data_iterations.evaluations_dir

    log.info(f'---------------------------- Evaluate test set -----------------------------')

    # Get image indices of all predictions
    predictions_img_indices = tools.list_of_all_predictions(config, log, iteration)

    # Sample random image indices for the test set
    test_img_indices = np.random.default_rng(seed = seed).choice(predictions_img_indices, 
                                                                 size = num_samples_test, 
                                                                 replace = False)
    
    test_img_indices = test_img_indices.tolist()
    test_img_indices = sorted(test_img_indices)
    
    log.info(f"Number of samples in the test set: {num_samples_test}")
    log.info(f"Image indices of samples in the test set: {test_img_indices}")

    # Nested dictionary for storing evaluation metrics of all test predictions
    evaluation_metrics_test = {}

    # Add info to the dictionary
    evaluation_metrics_test["info"] = {
                                       "Number of samples in test set": num_samples_test,
                                       "Image indices of samples in the test set": test_img_indices
                                       }
    
    # Set logging level to WARNING
    log.setLevel(logging.WARNING)

    for i, img_index in enumerate(test_img_indices):

        # 1. Load prediction segmentation (as numpy array and nii.gz)
        prediction_segmentation, prediction_segmentation_nii = tools.load_prediction_segmentation(img_index, config, log, iteration)

        # 2. Load ground truth centerline
        ground_truth_centerline_indices = tools.load_ground_truth_centerline(img_index, prediction_segmentation_nii, config, log)

        # 3. Compute centerline from the predicted LAD segmentation
        prediction_centerline_indices = tools.compute_centerline_from_prediction(prediction_segmentation, prediction_segmentation_nii, img_index, config)
        
        # 4. Evaluate the prediction (w.r.t. the ground truth LAD centerline, which is always available)
        evaluation_metrics_centerline = tools.compute_evaluation_metrics_wrtGTcenterline(ground_truth_centerline_indices, prediction_centerline_indices, prediction_segmentation, img_index, log, config)

        # 5. Store evaluation metrics in nested dictionary
        evaluation_metrics_test[int(img_index)] = evaluation_metrics_centerline

    # ---------------------- #
    # TODO:
    # For each sample in test set:
    # --- Image index
    # --- Number of connected components
    # --- Centerline DICE score
    # --- Normal DICE score
    # --- Houstorf distance

    # For each metric, store a list of the values across all samples, but also store the mean

    # Figure out how to save a dictionary to a .yaml file into iterations/evaluations/evaluation_unlabeled_set.yaml
    # NOTE: Save in a way where it can easily be copy-pasted into a function for plotting

    # Set logging level to INFO
    log.setLevel(logging.INFO)

    # Save dictionary to .json file
    evaluation_filename = f"evaluation_test_set_iteration_{iteration}.json"
    evaluation_path = f"{base_dir}/{version}/{data_iterations_dir}/{dataset_name}/iteration_{iteration}/{iterations_evaluations_dir}/{evaluation_filename}"

    with open(evaluation_path, 'w') as file:
        json.dump(evaluation_metrics_test, file, indent = 4)

    log.info(f'Evaluations on test set saved to: "/iteration_{iteration}/{iterations_evaluations_dir}/{evaluation_filename}"')
    log.info(f'----------------------------------------------------------------------------\n')

    return evaluation_metrics_test
