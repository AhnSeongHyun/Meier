# -*- coding:utf-8 -*-

from sqlalchemy import Column, Integer, String

from meier_app.db.base import MixinBase
from meier_app.extensions import db


class PostTag(db.Model, MixinBase):
    __tablename__ = 'post_tag'
    __table_args__ = {'extend_existing': True, "mysql_engine": "InnoDB"}

    tag_id = Column(Integer, nullable=False, index=True)
    post_id = Column(Integer, nullable=False, index=True)