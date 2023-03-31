from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from functools import reduce
import torch

from .feature_selection import filter_by_laplacian

# given a MultiOmicDataset object, convert to Triplets (anchor,positive,negative)
class TripletMultiOmicDataset(Dataset):
    """
    Train: For each sample (anchor) randomly chooses a positive and negative samples
    Test: Creates fixed triplets for testing
    """

    def __init__(self, mydataset, train = True):
        self.mydataset = mydataset
        self.train = train
        if self.train:
            self.train_data = self.mydataset
            self.labels_set, self.label_to_indices = self.get_label_indices(self.mydataset.y)
        else:
            self.test_data = self.mydataset
            self.test_triplets = self.generate_triplets(labels = self.mydataset.y, 
                                                        N = len(self.test_data))
    def __getitem__(self, index):
        if self.train:
            # get anchor sample and its label
            anchor, label = self.train_data[index][0], self.train_data[index][1].item()
            # choose another sample with same label
            positive_index = index
            while positive_index == index:
                positive_index = np.random.choice(self.label_to_indices[label])
            # choose another sample with a different label 
            negative_label = np.random.choice(list(self.labels_set - set([label])))
            negative_index = np.random.choice(self.label_to_indices[negative_label])
            pos = self.train_data[positive_index][0] # positive example
            neg = self.train_data[negative_index][0] # negative example
        else:
            anchor = self.test_data[self.test_triplets[index][0]][0]
            pos = self.test_data[self.test_triplets[index][1]][0]
            neg = self.test_data[self.test_triplets[index][2]][0]
            label = self.test_data[index][1].item()
        return anchor, pos, neg, label

    def __len__(self):
        return len(self.mydataset)
    
    def get_label_indices(self, labels):
        labels_set = set(labels.numpy())
        label_to_indices = {label: np.where(labels.numpy() == label)[0]
                             for label in labels_set}
        return labels_set, label_to_indices    

    def generate_triplets(self, labels, N, seed = 42):
        labels_set, label_to_indices = self.get_label_indices(labels)
        random_state = np.random.RandomState(seed)
        triplets = [[i,
                     random_state.choice(label_to_indices[labels[i].item()]),
                     random_state.choice(label_to_indices[
                         np.random.choice(
                             list(labels_set - set([labels[i].item()]))
                         )
                     ])
                    ] for i in range(N)]
        return triplets


class MultiomicDataset(Dataset):
    """A PyTorch dataset for multiomic data.

    Args:
        dat (dict): A dictionary with keys corresponding to different types of data and values corresponding to matrices of the same shape. All matrices must have the same number of samples (rows).
        y (list or np.array): A 1D array of labels with length equal to the number of samples.
        features (list or np.array): A 1D array of feature names with length equal to the number of columns in each matrix.
        samples (list or np.array): A 1D array of sample names with length equal to the number of rows in each matrix.

    Returns:
        A PyTorch dataset that can be used for training or evaluation.
    """

    def __init__(self, dat, y, features, samples):
        """Initialize the dataset."""
        self.dat = dat
        self.y = y
        self.features = features
        self.samples = samples 

    def __getitem__(self, index):
        """Get a single data sample from the dataset.

        Args:
            index (int): The index of the sample to retrieve.

        Returns:
            A tuple of two elements: 
                1. A dictionary with keys corresponding to the different types of data in the input dictionary `dat`, and values corresponding to the data for the given sample.
                2. The label for the given sample.
        """
        subset_dat = {x: self.dat[x][index] for x in self.dat.keys()}
        subset_y = self.y[index]
        return subset_dat, subset_y
    
    def __len__ (self):
        """Get the total number of samples in the dataset.

        Returns:
            An integer representing the number of samples in the dataset.
        """
        return len(self.y)
    
    def subset(self, indices):
        """Create a new dataset containing only the specified indices.

        Args:
            indices (list or np.array): A 1D array of indices to include in the subset.

        Returns:
            A new MultiomicDataset containing the specified subset of data.
        """
        indices = np.asarray(indices)
        subset_dat = {key: self.dat[key][indices] for key in self.dat.keys()}
        subset_y = np.asarray(self.y)[indices]
        subset_samples = np.asarray(self.samples)[indices]
        return MultiomicDataset(subset_dat, subset_y, self.features, subset_samples)

class DataImporter:
    def __init__(self, path, outcome_var, data_types, min_features=None, top_percentile=None):
        self.path = path
        self.outcome_var = outcome_var
        self.data_types = data_types
        self.min_features = min_features
        self.top_percentile = top_percentile
        
    def read_data(self, folder_path, file_ext='.csv'):
        data = {}
        for file in os.listdir(folder_path):
            if file.endswith(file_ext):
                file_path = os.path.join(folder_path, file)
                file_name = os.path.splitext(file)[0]
                data[file_name] = pd.read_csv(file_path, index_col=0)
        return data

    def import_data(self):
        training_path = os.path.join(self.path, 'train')
        testing_path = os.path.join(self.path, 'test') if 'test' in os.listdir(self.path) else None

        if testing_path:
            self.validate_data_folders(training_path, testing_path)
        else:
            self.validate_data_folder(training_path)

        training_data = self.read_data(training_path)

        if testing_path:
            testing_data = self.read_data(testing_path)

        train_dat, train_y, train_samples = self.process_data(training_data)
        training_dataset = self.get_torch_dataset(train_dat, train_y, train_samples)

        testing_dataset = None
        if testing_data:
            test_dat, test_y, test_samples = self.process_data(testing_data, split = 'test', 
                                                harmonize_with=train_dat)
            testing_dataset = self.get_torch_dataset(test_dat, test_y, test_samples)
            
        return training_dataset, testing_dataset
    
    def validate_data_folders(self, training_path, testing_path):
        training_files = set(os.listdir(training_path))
        testing_files = set(os.listdir(testing_path))

        required_files = {'clin.csv'} | {f"{dt}.csv" for dt in self.data_types}

        if not required_files.issubset(training_files):
            missing_files = required_files - training_files
            raise ValueError(f"Missing files in training folder: {', '.join(missing_files)}")

        if not required_files.issubset(testing_files):
            missing_files = required_files - testing_files
            raise ValueError(f"Missing files in testing folder: {', '.join(missing_files)}")


    def process_data(self, data, split = 'train', harmonize_with=None):
        dat = {k: v for k, v in data.items() if k != 'clin'}
        ann = data['clin']
        dat, y, samples = self.get_labels(dat, ann)
        
        # no filtering is applied to test data, 
        # feature selection is only applied to training data
        if split == 'train': 
            if self.min_features or self.top_percentile:
                dat = self.filter(dat, self.min_features, self.top_percentile)
        # test data is harmonized with training data based 
        # on whatever features are left in training data
        if harmonize_with:
            dat = self.harmonize(harmonize_with, dat)
         
        return dat, y, samples

    def get_labels(self, dat, ann):
        y = ann[self.outcome_var]
        y = y[~y.isna()]

        samples = list(reduce(set.intersection, [set(item) for item in [dat[x].columns for x in dat.keys()]]))
        samples = list(set(y.index).intersection(samples))
        dat = {x: dat[x][samples] for x in dat.keys()}
        y = y[samples]
        return dat, y, samples

    def get_torch_dataset(self, dat, labels, samples):
        features = {x: dat[x].index for x in dat.keys()}
        dat = {x: torch.from_numpy(np.array(dat[x].T)).float() for x in dat.keys()}
        y =  torch.from_numpy(np.array(labels)).float()
        return MultiomicDataset(dat, y, features, samples)

    def filter(self, dat, min_features, top_percentile):
        counts = {x: max(int(dat[x].shape[0] * top_percentile), min_features) for x in dat.keys()}
        dat = {x: filter_by_laplacian(dat[x].T, topN=counts[x]).T for x in dat.keys()}
        return dat

    def harmonize(self, dat1, dat2):
        features = {x: dat1[x].index for x in self.data_types}
        return {x: dat2[x].loc[features[x]] for x in dat2.keys()}
