"""Constants related to the management of databases and missing values."""

# Missing values type
NOT_APPLICABLE = 1
NOT_AVAILABLE = 2
NOT_MISSING = 0

# Features type
CATEGORICAL = 0
ORDINAL = 1
CONTINUE_R = 2
CONTINUE_I = 3
DATE_TIMESTAMP = 4
DATE_EXPLODED = 5
BINARY = 6
NOT_A_FEATURE = -1

# Paths
METADATA_PATH = 'database/metadata/'

MV_PLACEHOLDER = 'MISSING_VALUE'


def is_categorical(x):
    return x in [CATEGORICAL, BINARY]

def is_ordinal(x):
    return x in [ORDINAL]

def is_continuous(x):
    return x in [CONTINUE_I, CONTINUE_R, DATE_TIMESTAMP]
