from tagmaster.hello_jy import hello_tagmaster


def test_hello_tagmaster():
    """Mise en place environnement de test"""
    assert hello_tagmaster() == "Hello Jean-Yves!"
