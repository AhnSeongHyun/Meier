# -*- coding:utf-8 -*-
from datetime import datetime

from attrdict import AttrDict
from flask import Blueprint, request

from meier_app.commons.logger import logger
from meier_app.commons.response_data import ResponseData, HttpStatusCode
from meier_app.extensions import db
from meier_app.models.post import Post
from meier_app.models.post_tag import PostTag
from meier_app.models.tag import Tag
from meier_app.resources.admin import base
from meier_app.resources.admin.base import login_required_api

admin_writer_api = Blueprint(
    "admin_writer_api", __name__, url_prefix="/admin/writer/api"
)


@admin_writer_api.route("/post/<int:post_id>", methods=["DELETE"])
@login_required_api
@base.api_exception_handler
def delete_post(post_id):
    Post.query(Post.id == post_id).delete()
    db.session.commit()
    return ResponseData(code=HttpStatusCode.SUCCESS).json


@admin_writer_api.route("/post/<int:post_id>", methods=["PUT"])
@login_required_api
@base.api_exception_handler
def update_post(post_id):
    req_data = AttrDict(request.get_json())
    post = Post.query.filter(Post.id == post_id).scalar()
    if post:
        for k, v in req_data.items():
            setattr(post, k, v)
        post.mo_date = datetime.now()

        tags_id = []
        tags = req_data.tags.strip().split(",")

        for tag in tags:
            tag = str(tag).strip()
            tag_instance = Tag.query.filter(Tag.tag == tag).scalar()
            if tag_instance is None:
                tag_instance = Tag(tag=tag)
                db.session.add(tag_instance)
                db.session.flush()
                tags_id.append(tag_instance.id)
            else:
                tags_id.append(tag_instance.id)

        for tag_id in tags_id:
            post_tag = (
                PostTag.query.filter(PostTag.post_id == post.id)
                .filter(PostTag.tag_id == tag_id)
                .all()
            )
            if not post_tag:
                post_tag = PostTag(post_id=post.id, tag_id=tag_id)
                db.session.add(post_tag)
                logger.debug(post_tag.id)
        db.session.commit()
    return ResponseData(code=HttpStatusCode.SUCCESS).json


@admin_writer_api.route("/post", methods=["POST"])
@login_required_api
@base.api_exception_handler
def save_post():
    from sqlalchemy import func

    req_data = AttrDict(request.get_json())

    post_name_dup_count = (
        db.session.query(func.count(Post.id))
        .filter_by(post_name=req_data.post_name.strip())
        .scalar()
    )
    if post_name_dup_count:
        return ResponseData(code=HttpStatusCode.DUP_POST_NAME).json

    post = Post()
    post.title = req_data.title.strip()
    post.content = req_data.content.strip()
    post.post_name = req_data.post_name.strip()
    post.html = req_data.html
    post.status = req_data.status
    post.visibility = req_data.visibility
    post.in_date = datetime.now()
    post.mo_date = datetime.now()
    db.session.add(post)
    db.session.commit()

    tags_id = []
    tags = req_data.tags.strip().split(",")
    for tag in tags:
        tag = str(tag).strip()
        tag_instance = Tag.query.filter(Tag.tag == tag).scalar()
        if tag_instance is None:
            tag_instance = Tag(tag=tag)
            db.session.add(tag_instance)
            db.session.flush()
            tags_id.append(tag_instance.id)
        else:
            tags_id.append(tag_instance.id)

    db.session.commit()
    logger.debug(tags_id)

    for tag_id in tags_id:
        post_tag = (
            PostTag.query.filter(PostTag.post_id == post.id)
            .filter(PostTag.tag_id == tag_id)
            .all()
        )
        if not post_tag:
            post_tag = PostTag(post_id=post.id, tag_id=tag_id)
            db.session.add(post_tag)
            db.session.commit()
            logger.debug(post_tag.id)
    return ResponseData(code=HttpStatusCode.SUCCESS, data={"id": post.id}).json
