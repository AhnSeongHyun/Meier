from mixer.backend.flask import mixer

from meier.models.settings import Settings


def test_insert(session):
    mixer.blend(Settings)
    spec_setting = mixer.blend(
        Settings,
        blog_title="test1",
        blog_desc="test1",
        theme="test1",
        domain="test1",
    )

    assert spec_setting.blog_title == "test1"
    assert spec_setting.blog_desc == "test1"
    assert spec_setting.theme == "test1"
    assert spec_setting.domain == "test1"
    assert spec_setting.post_per_page == 10
    assert Settings.query.count() == 2


def test_update(session):
    mixer.blend(Settings)

    s = Settings.query.scalar()
    s.blog_title = "blog"
    s.blog_desc = "blog"
    s.post_per_page = 0

    session.commit()
    assert s.blog_title == "blog"
    assert s.blog_desc == "blog"
    assert s.post_per_page == 0


def test_delete(session):
    mixer.blend(Settings)
    s = Settings.query.scalar()
    session.delete(s)
    session.commit()
    assert Settings.query.count() == 0


def test_for_dict(session):
    spec_setting = mixer.blend(
        Settings,
        blog_title="test2",
        blog_desc="test2",
        theme="test2",
        domain="test2",
    )

    test_dict = {
        "blog_title": "test2",
        "blog_desc": "test2",
        "theme": "test2",
        "post_per_page": 10,
        "domain": "test2",
    }
    assert spec_setting.for_dict == test_dict
