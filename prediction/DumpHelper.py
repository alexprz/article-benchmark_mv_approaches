"""Class to dump task info and fit results into csv/yaml files."""
import logging
import os
import shutil
from datetime import datetime

import numpy as np
import pandas as pd
import yaml

results_folder = 'results/'
logger = logging.getLogger(__name__)


def _dump_yaml(data, filepath):
    data = listify(data)
    with open(filepath, 'w') as file:
        file.write(yaml.dump(data, allow_unicode=True))


def _dump_infos(item, filepath):
    """Dump the infos at the given place.

    Parameters
    ----------
    item : object
        Object implementing  a get_infos method returning the infos to dump.
    filepath : string
        Path to the place to store the infos.
    """
    data = item.get_infos()
    _dump_yaml(data, filepath)


def listify(d):
    """Convert all numpy arrays contained in the dict to lists.

    Parameters
    ----------
    d : dict

    Returns
    -------
    dict
        Same dict with numpy arrays converted to lists

    """
    if isinstance(d, list):
        return [listify(v) for v in d]
    elif isinstance(d, np.ndarray):
        return listify(d.tolist())
    elif isinstance(d, dict):
        return {k: listify(v) for k, v in d.items()}
    elif isinstance(d, int):
        return d
    elif isinstance(d, str):
        return d
    elif np.isscalar(d):
        return float(d)
    elif callable(d):
        return d.__name__
    else:
        return d


def get_tag(RS, T):
    RS_tag = '' if RS is None else f'RS{RS}_'
    T_tag = '' if T is None else f'T{T}_'
    return RS_tag + T_tag


class DumpHelper:
    """Class used to dump prediction results."""

    def __init__(self, task, strat, RS=None, T=None, n_bagging=None):
        self.task = task
        self.strat = strat
        self.RS = RS
        self.T = T
        self.n_bagging = n_bagging

        self.db_folder = f'{results_folder}{self.task.meta.db}/'

        tag = get_tag(RS, T)

        self.task_folder = f'{self.db_folder}{self.task.meta.name}/'
        logger.info(f'Task folder: {self.task_folder}')

        self.backup_folder = f'{self.task_folder}backup/'

        if strat is not None:
            name = strat.name if n_bagging is None else f'{strat.name}_Bagged{self.n_bagging}'
            self.strat_folder = f'{self.task_folder}{tag}{name}/'
            logger.info(f'Strat folder: {self.strat_folder}')

        self._dump_infos()
        self._dump_features()

    def _dump_infos(self):
        """Dump the infos of the task and strategy used."""
        if self.strat is not None:
            # Check if task directory already exists
            if os.path.isdir(self.strat_folder):
                # Move it in the backup folder
                os.makedirs(self.backup_folder, exist_ok=True)
                time_tag = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
                dest = f'{self.backup_folder}{self.strat.name}_{time_tag}'

                # Move lead to error on next dumping so copy + delete
                shutil.copytree(self.strat_folder, dest)
                shutil.rmtree(self.strat_folder)

            # Create all necessary folders and ignore if already exist
            os.makedirs(self.strat_folder, exist_ok=True)

            # Update infos of the task if using bagging
            strat_infos = self.strat.get_infos()
            strat_infos['n_bagging'] = self.n_bagging
            # if self.n_bagging is not None:
            #     strat_infos['name'] = f"Bagged_{self.n_bagging}_{strat_infos['name']}"

            _dump_yaml(self.task.get_infos(), f'{self.strat_folder}task_infos.yml')
            _dump_yaml(strat_infos, f'{self.strat_folder}strat_infos.yml')

        else:
            # Create all necessary folders and ignore if already exist
            os.makedirs(self.task_folder, exist_ok=True)

            _dump_yaml(self.task.get_infos(), f'{self.task_folder}task_infos.yml')

    def _dump_features(self):
        filepath = self.strat_folder+'features.yml'
        _dump_yaml(list(self.task.X.columns), filepath)

    def _filepath(self, filename):
        return f'{self.strat_folder}{filename}'

    @staticmethod
    def _load_content(filepath):
        """Used to load a yaml or csv file as dict or df respectively.

        Parameters
        ----------
        filepath : str
            Path of the file to load

        Returns
        -------
        dict or df
            Depends on the extension present in the path:
            If csv: returns df. If file doesn't exist, returns empty df.
            If yml: returns dict. If file doesn't exist, returns empty dict.

        """
        _, ext = os.path.splitext(filepath)

        if ext == '.yml':
            if not os.path.exists(filepath):
                return dict()
            # If exists
            with open(filepath, 'r') as file:
                return yaml.safe_load(file)

        elif ext == '.csv':
            if not os.path.exists(filepath):
                return pd.DataFrame()
            # If exists
            return pd.read_csv(filepath, index_col=0, dtype=str)

        else:
            raise ValueError(f'Extension {ext} not supported.')

    @staticmethod
    def _append_fold(filepath, data, fold=None):
        """Dump data (df or dict) in a file while keeping track of the fold #.

        Open or create a file and dump the data in it. If previous data has
        been dumped for the same fold number, the newer one will replace it.
        To keep track of the fold number, the data is stored in a dict with
        fold number as key (if data is dict). If data is dataframe, an extra
        fold columns is added and the dataframe is concatenated to the existing
        after removing the existing data having the same fold number.

        Parameters
        ----------
        filepath : str
            Path of the file to dump the data in.
        data : dict or pandas.DatFrame
            The data to dump.
        fold : int or None
            The fold number of the data.

        """
        content = DumpHelper._load_content(filepath)

        if isinstance(content, dict):
            content[fold] = data
            _dump_yaml(content, filepath)

        elif isinstance(content, pd.DataFrame):
            if not isinstance(data, pd.DataFrame):
                raise ValueError('Dumping to csv require pandas df as data.')

            # Remove previous results of same fold number
            if not content.empty:
                # Df is supposed to have fold column if not empty
                content = content[content.fold != fold]

            # Add new results
            data = data.copy()
            data['fold'] = fold
            content = pd.concat([content, data])

            content.to_csv(filepath)

    def _dump(self, data, filename, fold=None):
        """Wraper to dump data (dict or df) in a file."""
        filepath = self._filepath(filename)
        DumpHelper._append_fold(filepath, data, fold=fold)

    def dump_prediction(self, y_pred, y_true, fold=None, tag=None):
        df = pd.DataFrame({
            'y_pred': y_pred,
            'y_true': y_true,
        })

        if tag is None:
            tag = ''

        self._dump(df, f'{tag}_prediction.csv', fold=fold)

    def dump_best_params(self, best_params, fold=None):
        self._dump(best_params, 'best_params.yml', fold=fold)

    def dump_cv_results(self, cv_results, fold=None):
        self._dump(cv_results, 'cv_results.yml', fold=fold)

    def dump_roc(self, y_score, y_true, fold=None):
        df = pd.DataFrame({
            'y_score': y_score,
            'y_true': y_true
        })

        self._dump(df, 'roc.csv', fold=fold)

    def dump_probas(self, y_true, probas, classes=None, fold=None, tag=None):
        y_true = np.array(y_true)
        probas = np.array(probas)
        n_classes = probas.shape[1]

        if classes is None:
            classes = range(n_classes)

        cols = ['y_true'] + [f'proba_{c}' for c in classes]

        data = np.concatenate([y_true.reshape(-1, 1), probas], axis=1)

        df = pd.DataFrame(data, columns=cols)

        if tag is None:
            tag = ''

        self._dump(df, f'{tag}_probas.csv', fold=fold)

    def dump_importance(self, importance, fold=None):
        data = {
            'importances_mean': importance.importances_mean,
            'importances_std': importance.importances_std,
            'importances': importance.importances
        }
        self._dump(data, 'importance.yml', fold=fold)

    def dump_learning_curve(self, learning_curve, fold=None):
        self._dump(learning_curve, 'learning_curve.yml', fold=fold)

    def dump_pvals(self, pvals):
        pvals.to_csv(self.task_folder+'pvals.csv', header=False)

    def dump_times(self, imputation_time, tuning_time, imputation_pt,
                   tuning_pt, fold=None, tag=None):
        df = pd.DataFrame({
            'imputation_WCT': [imputation_time],
            'tuning_WCT': [tuning_time],
            'imputation_PT': [imputation_pt],
            'tuning_PT': [tuning_pt],
        })

        if tag is None:
            tag = ''

        self._dump(df, f'{tag}_times.csv', fold=fold)
