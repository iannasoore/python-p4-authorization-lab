#!/usr/bin/env python3

import pytest
from sqlalchemy.pool import StaticPool

from app import app
from models import db, Article, User


@pytest.fixture(autouse=True)
def _db_setup_and_seed():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite://',
        SQLALCHEMY_ENGINE_OPTIONS={
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(username='tester')
        db.session.add(user)
        db.session.flush()

        # Ensure the first article is member-only for the tests.
        member_article = Article(
            author='Test Author',
            title='Member Only',
            content='Full content',
            preview='Preview...',
            minutes_to_read=1,
            is_member_only=True,
            user_id=user.id,
        )
        public_article = Article(
            author='Test Author',
            title='Public',
            content='Public content',
            preview='Public preview...',
            minutes_to_read=1,
            is_member_only=False,
            user_id=user.id,
        )

        db.session.add_all([member_article, public_article])
        db.session.commit()

    yield

def pytest_itemcollected(item):
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))