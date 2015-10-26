import time
import pytest
from mock import Mock, patch


@pytest.fixture
def refresher():
    from vcli.completion_refresher import CompletionRefresher
    return CompletionRefresher()


def test_ctor(refresher):
    """
    Refresher object should contain a few handlers
    :param refresher:
    :return:
    """
    assert len(refresher.refreshers) > 0
    actual_handlers = list(refresher.refreshers.keys())
    expected_handlers = ['schemata', 'tables', 'views', 'functions',
                         'types', 'databases']
    assert expected_handlers == actual_handlers


def test_refresh_called_once(refresher):
    """

    :param refresher:
    :return:
    """
    callbacks = Mock()
    vexecute = Mock()
    special = Mock()

    with patch.object(refresher, '_bg_refresh') as bg_refresh:
        actual = refresher.refresh(vexecute, special, callbacks)
        time.sleep(1)  # Wait for the thread to work.
        assert len(actual) == 1
        assert len(actual[0]) == 5
        assert actual[0][3] == 'Auto-completion refresh started in the background.'
        bg_refresh.assert_called_with(vexecute, special, callbacks)


def test_refresh_called_twice(refresher):
    """
    If refresh is called a second time, it should be restarted
    :param refresher:
    :return:
    """
    callbacks = Mock()

    vexecute = Mock()
    special = Mock()

    def dummy_bg_refresh(*args):
        time.sleep(3)  # seconds

    refresher._bg_refresh = dummy_bg_refresh

    actual1 = refresher.refresh(vexecute, special, callbacks)
    time.sleep(1)  # Wait for the thread to work.
    assert len(actual1) == 1
    assert len(actual1[0]) == 5
    assert actual1[0][3] == 'Auto-completion refresh started in the background.'

    actual2 = refresher.refresh(vexecute, special, callbacks)
    time.sleep(1)  # Wait for the thread to work.
    assert len(actual2) == 1
    assert len(actual2[0]) == 5
    assert actual2[0][3] == 'Auto-completion refresh restarted.'


def test_refresh_with_callbacks(refresher):
    """
    Callbacks must be called
    :param refresher:
    """
    callbacks = [Mock()]
    vexecute_class = Mock()
    vexecute = Mock()
    special = Mock()

    with patch('vcli.completion_refresher.VExecute', vexecute_class):
        # Set refreshers to 0: we're not testing refresh logic here
        refresher.refreshers = {}
        refresher.refresh(vexecute, special, callbacks)
        time.sleep(1)  # Wait for the thread to work.
        assert (callbacks[0].call_count == 1)
