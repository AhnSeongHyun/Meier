from datetime import datetime

from flask import Blueprint, request
from sqlalchemy import func

from meier.commons.response_data import HttpStatusCode, ResponseData
from meier.extensions import db
from meier.models.post import Post
from meier.models.post_tag import PostTag
from meier.models.tag import Tag
from meier.admin import base
from meier.admin.base import login_required_api

admin_writer_api = Blueprint(
    "admin_writer_api", __name__, url_prefix="/admin/writer/api"
)


@admin_writer_api.route("/post/<int:post_id>", methods=["DELETE"])
@login_required_api
@base.exc_handler
def delete_post(post_id):
    Post.query(Post.id == post_id).delete()
    db.session.commit()
    return ResponseData(code=HttpStatusCode.SUCCESS).json


@admin_writer_api.route("/post/<int:post_id>", methods=["PUT"])
@login_required_api
@base.exc_handler
def update_post(post_id):
    req_data = request.get_json()
    if post := Post.query.filter(Post.id == post_id).scalar():
        for k, v in req_data.items():
            setattr(post, k, v)
        post.mo_date = datetime.now()

        tags_id = []
        tags = req_data["tags"].strip().split(",")

        for tag in tags:
            tag = str(tag).strip()
            tag_instance = Tag.query.filter(Tag.tag == tag).scalar()
            if tag_instance is None:
                tag_instance = Tag(tag=tag)
                db.session.add(tag_instance)
                db.session.flush()
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
        db.session.commit()
    return ResponseData(code=HttpStatusCode.SUCCESS).json


@admin_writer_api.route("/post", methods=["POST"])
@login_required_api
@base.exc_handler
def save_post():
    req_data = request.get_json()
    if post_name_duplicated_count := (
        db.session.query(func.count(Post.id))
        .filter_by(post_name=req_data["post_name"].strip())
        .scalar()
    ):
        return ResponseData(code=HttpStatusCode.DUP_POST_NAME).json

    post = Post()
    post.title = req_data["title"].strip()
    post.content = req_data["content"].strip()
    post.post_name = req_data["post_name"].strip()
    post.html = req_data["html"]
    post.status = req_data["status"]
    post.visibility = req_data["visibility"]
    post.in_date = datetime.now()
    post.mo_date = datetime.now()
    db.session.add(post)
    db.session.commit()

    tags_id = []
    tags = req_data["tags"].strip().split(",")
    for tag in tags:
        tag = str(tag).strip()
        tag_instance = Tag.query.filter(Tag.tag == tag).scalar()
        if tag_instance is None:
            tag_instance = Tag(tag=tag)
            db.session.add(tag_instance)
            db.session.flush()
        tags_id.append(tag_instance.id)
    db.session.commit()

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
    return ResponseData(code=HttpStatusCode.SUCCESS, data={"id": post.id}).json
