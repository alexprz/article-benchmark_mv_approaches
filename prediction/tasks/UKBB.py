"""Build prediction tasks for the UKBB database."""
import copy

from .taskMeta import TaskMeta


tasks_meta = list()


# Task 1: Fluid intelligence prediction
def transform_df_fluid_intelligence(df, **kwargs):
    # Drop rows with missing values in the feature to predict
    predict = kwargs['meta'].predict

    return df.dropna(axis=0, subset=[predict])


tasks_meta.append(TaskMeta(
    name='fluid_intelligence',
    db='UKBB',
    df_name='40284',
    predict='20016-0.0',
    drop=[
        '20016-1.0',
        '20016-2.0'
    ],
    drop_contains=[
        '10136-',
        '10137-',
        '10138-',
        '10141-',
        '10144-',
        '10609-',
        '10610-',
        '10612-',
        '10721-',
        '10722-',
        '10740-',
        '10827-',
        '10860-',
        '10895-',  # pilots
        '20128-',
        '4935-',
        '4946-',
        '4957-',
        '4968-',
        '4979-',
        '4990-',
        '5001-',
        '5012-',
        '5556-',
        '5699-',
        '5779-',
        '5790-',
        '5866-',  # response
        '40001-',
        '40002-',
        '41202-',
        '41204',
        '20002-',  # large code
        '40006',
    ],
    transform=transform_df_fluid_intelligence
))

tasks_meta.append(TaskMeta(
    name='fluid_intelligence_light',
    db='UKBB',
    df_name='24440',
    predict='20016-0.0',
    drop=[
        '20016-1.0',
        '20016-2.0'
    ],
    drop_contains=[
        '10136-',
        '10137-',
        '10138-',
        '10141-',
        '10144-',
        '10609-',
        '10610-',
        '10612-',
        '10721-',
        '10722-',
        '10740-',
        '10827-',
        '10860-',
        '10895-',  # pilots
        '20128-',
        '4935-',
        '4946-',
        '4957-',
        '4968-',
        '4979-',
        '4990-',
        '5001-',
        '5012-',
        '5556-',
        '5699-',
        '5779-',
        '5790-',
        '5866-',  # response
        '40001-',
        '40002-',
        '41202-',
        '41204',
        '20002-',  # large code
        '40006',
    ],
    transform=transform_df_fluid_intelligence
))


