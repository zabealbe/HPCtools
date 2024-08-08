import pytest
from unittest.mock import MagicMock, patch
import ipywidgets as widgets
from threading import Timer
from hpctools.jupyter_utils import DynamicTableWidget, SlurmQueueWidget


@pytest.fixture
def dynamic_table_widget():
    rows_func = MagicMock(return_value=[])
    button_callback = MagicMock()
    widget = DynamicTableWidget(
        "Test Title", rows_func, button_callback, "Click Me", "info", 5
    )
    return widget, rows_func, button_callback


@pytest.fixture
def slurm_queue_widget():
    runner = MagicMock()
    widget = SlurmQueueWidget(runner, "test_job")
    return widget, runner


def test_dynamic_table_widget_initialization(dynamic_table_widget):
    widget, rows_func, button_callback = dynamic_table_widget

    assert widget.title == "Test Title"
    assert widget.refresh_interval == 5
    assert isinstance(widget.container, widgets.VBox)
    assert widget.rows_func == rows_func
    assert widget.button_callback == button_callback
    assert widget.button_text == "Click Me"
    assert widget.button_style == "info"


def test_dynamic_table_widget_new_lines(dynamic_table_widget):
    widget, _, _ = dynamic_table_widget

    widget.new_lines(3)
    assert len(widget.container.children) == 5  # 2 initial + 3 new


def test_dynamic_table_widget_del_lines(dynamic_table_widget):
    widget, _, _ = dynamic_table_widget

    widget.new_lines(3)
    widget.del_lines(2)
    assert len(widget.container.children) == 3  # 2 initial + 1 remaining


def test_dynamic_table_widget_get_row(dynamic_table_widget):
    widget, _, _ = dynamic_table_widget

    widget.new_lines(1)
    button, label, separator = widget.get_row(0)
    assert isinstance(button, widgets.Button)
    assert isinstance(label, widgets.Label)
    assert isinstance(separator, widgets.HTML)


def test_dynamic_table_widget_n_rows(dynamic_table_widget):
    widget, _, _ = dynamic_table_widget

    widget.new_lines(3)
    assert widget.n_rows() == 3


def test_dynamic_table_widget_update(dynamic_table_widget):
    widget, rows_func, _ = dynamic_table_widget
    rows_func.return_value = ["Row 1", "Row 2"]

    widget.update()
    assert widget.n_rows() == 2


def test_dynamic_table_widget_auto_update(dynamic_table_widget):
    widget, _, _ = dynamic_table_widget

    with patch.object(widget, "auto_update") as mock_auto_update:
        widget.auto_update()
        assert mock_auto_update.called


def test_slurm_queue_widget_initialization(slurm_queue_widget):
    widget, runner = slurm_queue_widget

    assert widget.title == "Slurm Queue"
    assert widget.runner == runner
    assert widget.job_name == "test_job"


def test_slurm_queue_widget_get_slurm_queue(slurm_queue_widget):
    widget, runner = slurm_queue_widget
    runner.exec.return_value = (
        MagicMock(readlines=MagicMock(return_value=["", "job1", "job2"])),
        None,
        None,
    )

    lines = widget.get_slurm_queue()
    assert lines == ["job1", "job2"]


def test_slurm_queue_widget_kill_job(slurm_queue_widget):
    widget, runner = slurm_queue_widget
    runner.exec.return_value = (
        MagicMock(readlines=MagicMock(return_value=["killed"])),
        None,
        None,
    )

    result = widget.kill_job("12345")
    assert result == ["killed"]


def test_slurm_queue_widget_on_click(slurm_queue_widget):
    widget, runner = slurm_queue_widget
    runner.exec.return_value = (
        MagicMock(readlines=MagicMock(return_value=["killed"])),
        None,
        None,
    )

    button = MagicMock()
    row = "12345 some_job"
    widget.on_click(button, row)
    runner.exec.assert_called_with("scancel 12345")
