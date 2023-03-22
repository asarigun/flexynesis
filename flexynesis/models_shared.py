# Networks that can be reused across different architectures

import torch
from torch import nn


class Encoder(nn.Module):
    """
    Encoder class for a Variational Autoencoder (VAE).
    
    The Encoder class is responsible for taking input data and generating the mean and
    log variance for the latent space representation.
    """
    def __init__(self, input_dim, hidden_dims, latent_dim):
        """
        Initializes the Encoder class with given input dimensions, hidden layer dimensions, and latent dimensions.
        
        Args:
            input_dim (int): The dimensionality of the input data.
            hidden_dims (list): A list of integers representing the dimensions of the hidden layers.
            latent_dim (int): The dimensionality of the latent space.
        """
        super(Encoder, self).__init__()

        self.LeakyReLU = nn.LeakyReLU(0.2)
        
        # Create a list to store the hidden layers
        hidden_layers = []
        
        # Add the input layer to the first hidden layer
        hidden_layers.append(nn.Linear(input_dim, hidden_dims[0]))
        hidden_layers.append(self.LeakyReLU)

        # Create the hidden layers
        for i in range(len(hidden_dims)-1):
            hidden_layers.append(nn.Linear(hidden_dims[i], hidden_dims[i+1]))
            hidden_layers.append(self.LeakyReLU)

        # Add the hidden layers to the model using nn.Sequential
        self.hidden_layers = nn.Sequential(*hidden_layers)
        
        self.FC_mean  = nn.Linear(hidden_dims[-1], latent_dim)
        self.FC_var   = nn.Linear(hidden_dims[-1], latent_dim)
        
    def forward(self, x):
        """
        Performs a forward pass through the Encoder network.
        
        Args:
            x (torch.Tensor): The input data tensor.
            
        Returns:
            mean (torch.Tensor): The mean of the latent space representation.
            log_var (torch.Tensor): The log variance of the latent space representation.
        """
        h_       = self.hidden_layers(x)
        mean     = self.FC_mean(h_)
        log_var  = self.FC_var(h_)
        return mean, log_var
    
    
class Decoder(nn.Module):
    """
    Decoder class for a Variational Autoencoder (VAE).
    
    The Decoder class is responsible for taking the latent space representation and
    generating the reconstructed output data.
    """
    def __init__(self, latent_dim, hidden_dims, output_dim):
        """
        Initializes the Decoder class with given latent dimensions, hidden layer dimensions, and output dimensions.
        
        Args:
            latent_dim (int): The dimensionality of the latent space.
            hidden_dims (list): A list of integers representing the dimensions of the hidden layers.
            output_dim (int): The dimensionality of the output data.
        """
        super(Decoder, self).__init__()

        self.LeakyReLU = nn.LeakyReLU(0.2)

        # Create a list to store the hidden layers
        hidden_layers = []

        # Add the input layer to the first hidden layer
        hidden_layers.append(nn.Linear(latent_dim, hidden_dims[0]))
        hidden_layers.append(self.LeakyReLU)

        # Create the hidden layers
        for i in range(len(hidden_dims) - 1):
            hidden_layers.append(nn.Linear(hidden_dims[i], hidden_dims[i + 1]))
            hidden_layers.append(self.LeakyReLU)

        # Add the hidden layers to the model using nn.Sequential
        self.hidden_layers = nn.Sequential(*hidden_layers)

        self.FC_output = nn.Linear(hidden_dims[-1], output_dim)

    def forward(self, x):
        """
        Performs a forward pass through the Decoder network.
        
        Args:
            x (torch.Tensor): The input tensor representing the latent space.
            
        Returns:
            x_hat (torch.Tensor): The reconstructed output tensor.
        """
        h = self.hidden_layers(x)
        x_hat = torch.sigmoid(self.FC_output(h))
        return x_hat
    

# a MLP model for regression/classification
# set num_class to 1 for regression. num_class > 1 => classification
class MLP(nn.Module):
    def __init__(self, num_feature, num_class, h = 32):
        super(MLP, self).__init__()
        self.layer_1 = nn.Linear(num_feature, h)
        self.layer_out = nn.Linear(h, num_class)
        self.relu = nn.ReLU() 
        self.dropout = nn.Dropout(p=0.4)
        self.batchnorm = nn.BatchNorm1d(h)

    def forward(self, x):
        x = self.layer_1(x)
        x = self.dropout(x)
        x = self.batchnorm(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.layer_out(x)
        return x

# Simple Feed-Forward Network
class EmbeddingNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(EmbeddingNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
    
# Simple feed-forward multi-class classifier
class Classifier(nn.Module):
    def __init__(self, input_size, hidden_dims, num_classes):
        super(Classifier, self).__init__()
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(input_size, hidden_dims[0]))
        
        # Hidden layers
        for i in range(len(hidden_dims) - 1):
            self.layers.append(nn.Linear(hidden_dims[i], hidden_dims[i + 1]))
        
        # Output layer
        self.layers.append(nn.Linear(hidden_dims[-1], num_classes))

    def forward(self, x):
        for layer in self.layers[:-1]:
            x = torch.relu(layer(x))
        x = self.layers[-1](x)
        return x