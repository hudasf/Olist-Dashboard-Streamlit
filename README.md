# Olist-Dashboard-Streamlit
my simple project creating simple yet powerful dashboard for monitoring operational condition. with advanced filtering in showing data

## Setup environment
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install numpy pandas matplotlib seaborn streamlit babel folum
```

## Setup dataframe
```
change main_dir string to real path of desired data to load in pandas dataframe.
```

## Run steamlit app
```
streamlit run olist_dataAnalyst.py
```

## Operating app
```
1. use date filter in sidebar for desired date range.
2. data and graph will show accordingly.
3. pick data to show in multi select.
4. app will show only desired data.
5. download data if needed.
```

## Streamlit App Deploy Demo
```
demo of running app can be found in :
https://hudasf-olist.streamlit.app/
```
