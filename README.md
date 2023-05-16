# Numerical simulations of atmospheric quantum channels: Source code

## Structure

The project consists of 5 stages:
- `01-simulation` - at this stage the main data simulation is performed (the results can be found in the `01-simulation/data` folder);
- `02-analysis` - at this stage the data transformation is performed (obtaining the PDT, the KS functions for all the models; the results will be saved in the `02-analysis/results` folder);
- `03-plots` - the stage of plotting the PDT & KS figures used in the paper;
- `04-details` - the stage of analysing and plotting the figures to the `V. STATISTICAL CHARACTERISTICS OF BEAM PARAMETERS` section;
- `05-application` - the stage of plotting the figures to the `VI. APPLICATION: TRANSMISSION OF SQUEEZED LIGHT` section;


## Running
Make sure you have [Python 3.8+](https://realpython.com/installing-python/#how-to-install-python-on-linux) installed.
Create a [virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments) and [install the required packages](https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing) from the `requirements.txt` file:
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```
Then you can go to the required stage directory, i.e. `cd 03-plots` and execute:
```
python3 main.py
```


<!-- ## Citation -->
