import os


def test_readme_exists_not_empty():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    readme_path = os.path.join(repo_root, 'README.md')
    assert os.path.isfile(readme_path), 'README.md file not found'
    assert os.path.getsize(readme_path) > 0, 'README.md is empty'
