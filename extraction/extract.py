"""Extract a sub df from a big df."""
import os
import pandas as pd
import logging
import csv

from prediction.tasks import tasks
from database.base import Database
from database import dbs

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())  # Print also in console.

dump_folder = 'extracted/'


def run(args):
    task_name = args.task_name
    task = tasks[task_name]
    db = dbs[task.meta.db]
    df_name = task.meta.df_name
    path = db.frame_paths[df_name]

    features = pd.read_csv(path, sep=db._sep, encoding=db._encoding,
                           nrows=0)

    to_keep, _ = Database.get_drop_and_keep_meta(features, task.meta)

    if db.acronym == 'UKBB':
        index_col = 'eid'
        to_keep.add('eid')
        quoting = csv.QUOTE_ALL
    else:
        index_col = None
        quoting = csv.QUOTE_MINIMAL

    df = pd.read_csv(path, sep=db._sep, encoding=db._encoding,
                     usecols=to_keep, index_col=index_col)

    dump_path = dump_folder + db.acronym
    os.makedirs(dump_path, exist_ok=True)
    df.to_csv(f'{dump_folder}{task_name}_{df_name}.csv', quoting=quoting)
