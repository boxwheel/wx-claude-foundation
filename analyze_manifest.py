"""Dataset manifest and quality analysis for wx-claude-foundation."""
import pandas as pd
import numpy as np
import json
import os

DATA_DIR = '/home/user/research/data'
OUT_DIR = '/home/user/research/wx-claude-foundation/artifacts'

def analyze_global():
    df = pd.read_csv(f'{DATA_DIR}/GlobalTemperatures.csv', parse_dates=['dt'])
    df['year'] = df['dt'].dt.year
    result = {
        'file': 'GlobalTemperatures.csv',
        'rows': len(df),
        'cols': list(df.columns),
        'date_range': [str(df['dt'].min().date()), str(df['dt'].max().date())],
        'nan_pct_land_avg': df['LandAverageTemperature'].isna().mean(),
        'nan_pct_land_ocean': df['LandAndOceanAverageTemperature'].isna().mean(),
        'uncertainty_by_period': {}
    }
    for start in range(1750, 2020, 50):
        sub = df[(df['year'] >= start) & (df['year'] < start+50)].dropna(subset=['LandAverageTemperature'])
        result['uncertainty_by_period'][f'{start}-{start+50}'] = {
            'n_months': len(sub),
            'mean_uncertainty_C': round(sub['LandAverageTemperatureUncertainty'].mean(), 3)
        }
    return result

def analyze_country():
    df = pd.read_csv(f'{DATA_DIR}/GlobalLandTemperaturesByCountry.csv', parse_dates=['dt'])
    return {
        'file': 'GlobalLandTemperaturesByCountry.csv',
        'rows': len(df),
        'countries': df['Country'].nunique(),
        'date_range': [str(df['dt'].min().date()), str(df['dt'].max().date())],
        'nan_pct': df['AverageTemperature'].isna().mean()
    }

def analyze_major_city():
    df = pd.read_csv(f'{DATA_DIR}/GlobalLandTemperaturesByMajorCity.csv', parse_dates=['dt'])
    return {
        'file': 'GlobalLandTemperaturesByMajorCity.csv',
        'rows': len(df),
        'cities': df['City'].nunique(),
        'countries': df['Country'].nunique(),
        'date_range': [str(df['dt'].min().date()), str(df['dt'].max().date())],
        'nan_pct': df['AverageTemperature'].isna().mean()
    }

def analyze_city_be():
    df = pd.read_csv(f'{DATA_DIR}/GlobalLandTemperaturesByCity.csv', low_memory=False, parse_dates=['dt'])
    return {
        'file': 'GlobalLandTemperaturesByCity.csv',
        'rows': len(df),
        'cities': df['City'].nunique(),
        'countries': df['Country'].nunique(),
        'date_range': [str(df['dt'].min().date()), str(df['dt'].max().date())],
        'nan_pct': df['AverageTemperature'].isna().mean()
    }

def analyze_daily():
    df = pd.read_csv(f'{DATA_DIR}/city_temperature.csv', low_memory=False)
    df_clean = df[df['AvgTemperature'] != -99]
    return {
        'file': 'city_temperature.csv',
        'rows_total': len(df),
        'rows_after_sentinel_removal': len(df_clean),
        'sentinel_pct': (df['AvgTemperature'] == -99).mean(),
        'year_anomalies': {'year_200_rows': int((df['Year'] == 200).sum()),
                           'year_201_rows': int((df['Year'] == 201).sum())},
        'year_range_clean': [int(df_clean[df_clean['Year'] > 500]['Year'].min()),
                             int(df_clean['Year'].max())],
        'cities': df['City'].nunique(),
        'countries': df['Country'].nunique(),
        'note': 'Temperatures in FAHRENHEIT. -99 is missing sentinel. Year values 200 and 201 are data entry errors (440 rows, discard).'
    }

manifest = {
    'datasets': [
        analyze_global(),
        analyze_country(),
        analyze_major_city(),
        analyze_city_be(),
        analyze_daily()
    ],
    'quality_warnings': [
        'Berkeley Earth: uncertainty pre-1850 is 23x higher than post-1960 (2.05 vs 0.09 C). Claims about the earliest period must account for this.',
        'Daily city dataset: temperatures in Fahrenheit (not Celsius). Convert: C = (F - 32) * 5/9.',
        'Daily city dataset: -99 sentinel for missing values must be removed before analysis.',
        'Daily city dataset: Year values 200 and 201 (440 rows total) are data entry errors; discard.',
        'Berkeley Earth by-country/city: sparse and high-uncertainty before 1850.',
        'Station composition changes over time can introduce apparent trends.'
    ]
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(f'{OUT_DIR}/dataset_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print('Manifest saved.')
print(json.dumps(manifest, indent=2))
