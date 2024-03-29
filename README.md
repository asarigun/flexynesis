
<p align="center">
  <img alt="logo" src="img/logo.png" width="50%" height="50%">
</p>

[![Tests](https://github.com/BIMSBbioinfo/flexynesis/actions/workflows/tests.yml/badge.svg)](https://github.com/BIMSBbioinfo/flexynesis/actions/workflows/tests.yml)
![benchmarks](https://github.com/BIMSBbioinfo/flexynesis/actions/workflows/benchmarks.yml/badge.svg)

# flexynesis
A deep-learning based multi-omics bulk sequencing data integration suite with a focus on (pre-)clinical 
endpoint prediction. The package includes multiple types of deep learning architectures such as simple 
fully connected networks, supervised variational autoencoders; different options of data layer fusion, 
and automates feature selection and hyperparameter optimisation. The tools are continuosly benchmarked 
on publicly available datasets mostly related to the study of cancer. Some of the applications of the methods 
we develop are drug response modeling in cancer patients or preclinical models (such as cell lines and 
patient-derived xenografts), cancer subtype prediction, or any other clinically relevant outcome prediction
that can be formulated as a regression or classification problem. 

<p align="center">
  <img alt="workflow" src="img/workflow.jpg">
</p>

# Documentation

A detailed documentation of classes and functions in this repository can be found [here](https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis/docs/flexynesis/index.html).

# Benchmarks

For the latest benchmark results see: 
https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis-benchmark-datasets/dashboard.html

The code for the benchmarking pipeline is at: https://github.com/BIMSBbioinfo/flexynesis-benchmarks

# Quick Start

```
# install 
git clone https://github.com/BIMSBbioinfo/flexynesis.git
cd flexynesis
conda create --name flexynesis --file spec-file.txt
conda activate flexynesis
pip install -e .

# test the installation
curl -L -o dataset1.tgz https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis-benchmark-datasets/dataset1.tgz
tar -xzvf dataset1.tgz

flexynesis --data_path dataset1 --model_class DirectPred --target_variables Erlotinib --fusion_type early --hpo_iter 1 --features_min 50 --features_top_percentile 5 --log_transform False --data_types gex,cnv --outdir . --prefix erlotinib_direct --early_stop_patience 3 --use_loss_weighting False --evaluate_baseline_performance False
```

To export existing spec-file.txt:
```
conda list --explicit > spec-file.txt
```

# Guix

You can also create a reproducible development environment with [GNU Guix](https://guix.gnu.org).  You will need at least the Guix channels listed in `channels.scm`.

```
guix shell
```

or

```
guix shell -m manifest.scm
```

You can build a Guix package from the current committed state of your git checkout like this:

```
guix pack -f guix.scm
```

Do this to build a Docker image containing this package together with a matching Python installation:

```
guix pack -C none \
  -e '(load "guix.scm")' \
  -f docker \
  -S /bin=bin -S /lib=lib -S /share=share \
  glibc-locales coreutils bash python
```

# Defining Kernel for Jupyter Notebook

For interactively using flexynesis on Jupyter notebooks, one can define the kernel to make
flexynesis and its dependencies available on the jupyter session. 

Assuming you have already defined an environment and installed the package: 
```
conda activate flexynesis
python -m ipykernel install --user --name "flexynesis" --display-name "flexynesis"
```

# Testing

Run unit tests
```python
pytest -vvv tests/unit
```

This will run all the unit tests in the tests directory.

# Contributing
If you would like to contribute to the project, please open an issue or a pull request on the GitHub repository.

# Branches

When working on a feature on a new branch, don't forget to write a branch description:
```
git branch --edit-description
```


You can view branch descriptions: 
```
git config branch.<branch name>.description 
```




# Documentation

```
pdoc --html --output-dir docs --force flexynesis 
```



