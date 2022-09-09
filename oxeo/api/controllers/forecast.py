import os

import gcsfs
import pandas as pd
import xarray as xr
import xgboost as xgb
from sqlalchemy.orm import Session

from oxeo.api.controllers import geom
from oxeo.api.models import database, schemas


def get_tp_cumsum(data, window=1):
    cum_tp = (
        data.mean(dim=["latitude", "longitude"]).isel(step=30).mean(dim="member").values
    )
    return (
        pd.Series(cum_tp, index=data.time.values)
        .rolling(min_periods=1, window=window)
        .sum()
    )


def get_keyed_values(results, keyed_value, new_col):
    df = pd.DataFrame(results)
    df.labels = df.labels.map(lambda x: x[0])
    df[new_col] = df.keyed_values.apply(lambda x: x.get(keyed_value))
    df = df.drop_duplicates(subset=["aoi_id", "datetime"]).dropna()
    df.datetime = pd.to_datetime(df.datetime)
    return df


def get_forecast(
    db: Session,
    user: database.User,
    event_query: schemas.EventQuery,
    forecast_query: schemas.ForecastQuery,
):

    bbox = forecast_query
    events = geom.get_events(event_query=event_query, db=db, user=user)
    events = [
        {
            "labels": e.labels,
            "aoi_id": e.aoi_id,
            "datetime": e.datetime,
            "keyed_values": e.keyed_values,
            "id": e.id,
        }
        for e in events.events
    ]
    aga_df = get_keyed_values(events, "mean_value", "ndvi_mean")
    ndvi = aga_df.groupby(["datetime"]).mean()["ndvi_mean"]
    ndvi_monthly = ndvi.resample("M").mean()

    # Shift ndvi. I'm using last month ndvi mean, and tp_monthly forecast

    url = "gs://oxeo-seasonal/tp"
    zx = xr.open_zarr(gcsfs.GCSMap(url))

    min_x, min_y, max_x, max_y = bbox.bbox
    min_x += 180
    max_x += 180

    data = zx["tp"].sel(
        {
            "time": slice(
                ndvi_monthly.index.min(),
                ndvi_monthly.index.max(),
            ),
            "latitude": slice(round(max_y), round(min_y)),
            "longitude": slice(round(min_x), round(max_x)),
        }
    )

    tp_monthly = get_tp_cumsum(data, window=1)
    tp_monthly_2_cumsum = get_tp_cumsum(data, window=2)
    tp_monthly_3_cumsum = get_tp_cumsum(data, window=3)

    ndvi_monthly = ndvi_monthly[:-1]

    ndvi_monthly.index = tp_monthly.index

    tp_monthly = tp_monthly[2:]
    tp_monthly_2_cumsum = tp_monthly_2_cumsum[2:]
    tp_monthly_3_cumsum = tp_monthly_3_cumsum[2:]
    ndvi_monthly = ndvi_monthly[2:]

    df = pd.concat(
        [ndvi_monthly, tp_monthly, tp_monthly_2_cumsum, tp_monthly_3_cumsum], axis=1
    )

    # load XGB models
    models = []
    for i in range(7):
        model = xgb.XGBRegressor()
        model.load_model(f"{os.environ['MODELS_PATH']}/model_{i+1}.json")
        models.append(model)

    value_to_predict = df.values[-1].reshape(1, -1)
    preds = []
    for i in range(7):
        preds.append(models[i].predict(value_to_predict)[0])

    return schemas.ForecastQueryReturn(forecast=list(preds))
