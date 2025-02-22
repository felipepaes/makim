"""Tests for `makim` package."""
from pathlib import Path

import pytest

import makim


@pytest.mark.parametrize(
    'target,args',
    [
        ('tests.test-1', {}),
        ('tests.test-1', {'--all': False}),
        ('tests.test-2', {'--all': True}),
        ('tests.test-3-a', {}),
        ('tests.test-3-b', {}),
        ('tests.test-4', {}),
        ('tests.test-4', {'--trigger-dep': True}),
        ('tests.test-5', {}),
        ('tests.test-6', {}),
    ],
)
def test_success(target, args):
    """Test makim when expects success."""
    makim_file = Path(__file__).parent / '.makim-unittest.yaml'

    m = makim.Makim()
    m.load(makim_file)

    args.update(
        {
            'target': target,
            'makim_file': makim_file,
        }
    )

    m.run(args)
