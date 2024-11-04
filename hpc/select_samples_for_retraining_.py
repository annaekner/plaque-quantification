import numpy as np

def select_samples_for_retraining(evaluation_metrics_all, config, log):
    """
    Select n samples for retraining based on the evaluation metrics of all predictions.

    Args
        evaluation_metrics_all: Nested dictionary of evaluation metrics for all predictions.
    """

    # Configuration settings
    num_samples_per_retraining = config.retraining.num_samples_per_retraining
    selection_method = config.retraining.selection_method  # 'worst', 'best', or 'random'

    # List of samples considered for retraining
    samples_considered_for_retraining = []

    # All samples sorted by number of connected components (in ascending and descending order)
    num_samples = len(evaluation_metrics_all)
    all_samples = list(evaluation_metrics_all.keys())
    all_samples_DICE_ascending = sorted(all_samples, key=lambda x: evaluation_metrics_all[x]['combined_centerline_dice_score'], reverse=False)
    all_samples_DICE_descending = sorted(all_samples, key=lambda x: evaluation_metrics_all[x]['combined_centerline_dice_score'], reverse=True)

    if selection_method == 'worst':
        # Find all predictions with > 1 connected component (if any)
        for img_index in evaluation_metrics_all:
            if evaluation_metrics_all[img_index]['num_connected_components'] > 1:
                samples_considered_for_retraining.append(img_index)

        # If not enough samples have > 1 connected components, add more
        if len(samples_considered_for_retraining) < num_samples_per_retraining:
            extra_samples = num_samples_per_retraining - len(samples_considered_for_retraining)
            
            for img_index in all_samples_DICE_ascending:

                # Add sample to list of samples considered for retraining if it has not already been added
                if img_index not in samples_considered_for_retraining:
                    samples_considered_for_retraining.append(img_index)
                    extra_samples -= 1

                if extra_samples == 0:
                    break

        if len(samples_considered_for_retraining) == num_samples_per_retraining:
            samples_for_retraining = samples_considered_for_retraining
        
        else:
            # Select sample with the lowest combined centerline "DICE" score
            samples_for_retraining = sorted(samples_considered_for_retraining, 
                                        key=lambda x: evaluation_metrics_all[x]['combined_centerline_dice_score'],
                                        reverse=False)[:num_samples_per_retraining]

    elif selection_method == 'best':
        # Find all predictions with exactly 1 connected component (if any)
        for img_index in evaluation_metrics_all:
            if evaluation_metrics_all[img_index]['num_connected_components'] == 1:
                samples_considered_for_retraining.append(img_index)

        # If not enough samples have exactly 1 connected components, add more
        if len(samples_considered_for_retraining) < num_samples_per_retraining:
            extra_samples = num_samples_per_retraining - len(samples_considered_for_retraining)

            for img_index in all_samples_DICE_descending:

                # Add sample to list of samples considered for retraining if it has not already been added
                if img_index not in samples_considered_for_retraining:
                    samples_considered_for_retraining.append(img_index)
                    extra_samples -= 1

                if extra_samples == 0:
                    break

        if len(samples_considered_for_retraining) == num_samples_per_retraining:
            samples_for_retraining = samples_considered_for_retraining

        else:
            # Select sample with the highest combined centerline "DICE" score
            samples_for_retraining = sorted(samples_considered_for_retraining, 
                                        key=lambda x: evaluation_metrics_all[x]['combined_centerline_dice_score'], 
                                        reverse=True)[:num_samples_per_retraining]

    elif selection_method == 'random':
        # Select random sample
        samples_for_retraining = np.random.default_rng(seed = 0).choice(all_samples, num_samples_per_retraining, replace=False)

    retraining = {
                  'samples_for_retraining': samples_for_retraining,
                  'selection_method': selection_method,
                  'num_connected_components': [evaluation_metrics_all[sample]["num_connected_components"] for sample in samples_for_retraining],
                  'predicted_centerline_coverage_of_ground_truth_centerline': [round(evaluation_metrics_all[sample]["predicted_centerline_coverage_of_ground_truth_centerline"], 4) for sample in samples_for_retraining],
                  'ground_truth_centerline_coverage_of_predicted_centerline': [round(evaluation_metrics_all[sample]["ground_truth_centerline_coverage_of_predicted_centerline"], 4) for sample in samples_for_retraining],
                  'combined_centerline_dice_score': [round(evaluation_metrics_all[sample]["combined_centerline_dice_score"], 4) for sample in samples_for_retraining],
                 }
    
    log.info(f'-------------------------------- Re-training -------------------------------')
    log.info(f'Number of samples evaluated: {num_samples}')
    log.info(f'Number of samples selected for re-training: {num_samples_per_retraining}')
    log.info(f'Selection method: {retraining["selection_method"]}')
    log.info(f'Image indices of samples selected for re-training: {retraining["samples_for_retraining"]}')
    log.info(f'Number of connected components: {retraining["num_connected_components"]}')
    log.info(f'Predicted centerline coverage of the ground truth centerline: {retraining["predicted_centerline_coverage_of_ground_truth_centerline"]}')
    log.info(f'Ground truth centerline coverage of the predicted centerline: {retraining["ground_truth_centerline_coverage_of_predicted_centerline"]}')
    log.info(f'Combined centerline "DICE" score: {retraining["combined_centerline_dice_score"]}')
    log.info(f'----------------------------------------------------------------------------\n')

    return retraining