import pytest
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def test_dummy_data_generation():
    """
    Test that we can generate dummy data for model testing
    without needing Spark or Delta Lake connections.
    """
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame({
        'trip_distance': np.random.uniform(0.5, 20.0, n_samples),
        'pickup_hour': np.random.randint(0, 24, n_samples),
    })
    
    assert len(df) == 100
    assert 'trip_distance' in df.columns
    assert 'pickup_hour' in df.columns

def test_linear_regression_model():
    """
    Test that a basic Scikit-Learn model can be instantiated and fitted.
    """
    # Create simple data
    X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5], 'feature2': [2, 4, 6, 8, 10]})
    y = pd.Series([10, 20, 30, 40, 50])
    
    model = LinearRegression()
    model.fit(X, y)
    
    predictions = model.predict(X)
    
    # Model predictions should roughly match for a perfect linear relationship
    assert len(predictions) == 5
    assert abs(predictions[0] - 10) < 1e-5
