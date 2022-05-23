from pathlib import Path
from gwdc_python.utils import remove_path_anchor


def test_remove_path_anchor():
    assert remove_path_anchor(Path('/a/test/absolute/path')) == Path('a/test/absolute/path')
    assert remove_path_anchor(Path('//another/test/absolute/path')) == Path('another/test/absolute/path')
    assert remove_path_anchor(Path('a/test/relative/path')) == Path('a/test/relative/path')
    assert remove_path_anchor(Path('./another/test/relative/path')) == Path('another/test/relative/path')
