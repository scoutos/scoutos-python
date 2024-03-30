from scoutos import App


def test_instanitation():
    app = App()
    assert isinstance(app, App)


def test_it_can_be_run():
    app = App()
    result = app.run()
    assert result.ok
