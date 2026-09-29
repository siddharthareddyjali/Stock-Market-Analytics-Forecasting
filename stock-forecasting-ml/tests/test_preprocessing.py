import pandas as pd

from app.services.preprocessing_service import PreprocessingService


def test_prepare_price_frame_handles_missing_and_duplicates():
    df = pd.DataFrame(
        {
            'Close': [100.0, None, 101.0, 102.0, 102.0],
            'Volume': [10, 11, 12, 13, 14],
        },
        index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-02', '2024-01-04', '2024-01-05'])
    )
    cleaned = PreprocessingService.prepare_price_frame(df)
    assert len(cleaned) >= 4
    assert 'Close' in cleaned.columns
