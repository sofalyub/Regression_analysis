"""
Модуль с пользовательским интерфейсом
"""

from ui.app import RegressionApp, run_app
from ui.widgets import (FileSelectionWidget, SheetSelectionWidget, ColumnSelectionWidget, 
                       MultipleColumnSelectionWidget, ResultsWidget)
from ui.data_preview import DataPreviewWidget

__all__ = [
    'RegressionApp', 'run_app',
    'FileSelectionWidget', 'SheetSelectionWidget', 'ColumnSelectionWidget',
    'MultipleColumnSelectionWidget', 'ResultsWidget',
    'DataPreviewWidget'
]