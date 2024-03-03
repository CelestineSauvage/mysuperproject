# How to develop on this project

**First you need PYTHON3!**

This instructions are for linux based systems (Linux, MacOS, BSD, etc.)

## Setting up your own fork of this repo.

- Clone the repo :
```shell script
git clone git@github.com:YOUR_GIT_USERNAME/FEV24-BDE-JOBMARKET.git
```

- Enter the directory :
```shell script
cd FEV24-BDE-JOBMARKET
```

## Setting up your own virtual environment

Create a virtual environment :
```shell script
python3 -m venv FEV24-BDE-JOBMARKET 
```

Activate the virtual environment :
```shell script
source .venv/bin/activate
```

## Install packages with pip and requirements.txt

Install automatically all the required packages according to the configuration file 'requirements.txt' :
```shell script
pip3 install -r requirements.txt
```

## Create a new branch to work on your contribution

```shell script
git checkout -b my_contribution
```
