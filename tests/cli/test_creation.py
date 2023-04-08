from propan.cli.startproject import create


def test_create_propject(move_dir, version):
    path = create(move_dir, version)
    assert path.exists()
