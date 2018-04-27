# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import abort, render_template

from meier_app.models.post import Post, PostStatus, PostVisibility
from meier_app.models.post_tag import PostTag
from meier_app.models.settings import Settings
from meier_app.models.tag import Tag
from meier_app.models.user import User
from meier_app.resources.blog.opengraph_generator import OpenGraphGenerator

post_detail_view = Blueprint('post_detail_view', __name__, url_prefix='/posts')


@post_detail_view.route('/<string:post_name>', methods=['GET'])
def get_post_detail_view(post_name: str):
    settings = Settings.query.first()
    author = User.query.first()
    post = Post.query \
        .filter(Post.post_name == post_name) \
        .filter(Post.visibility == int(PostVisibility.PUBLIC.value)) \
        .filter(Post.status == int(PostStatus.PUBLISH.value)).scalar()

    if post:
        prev_post = Post.query.filter(Post.id < post.id) \
            .filter(Post.visibility == int(PostVisibility.PUBLIC.value)) \
            .filter(Post.status == int(PostStatus.PUBLISH.value)) \
            .order_by(Post.id.desc()).first()
        next_post = Post.query.filter(Post.id > post.id)\
            .filter(Post.visibility == int(PostVisibility.PUBLIC.value)) \
            .filter(Post.status == int(PostStatus.PUBLISH.value))\
            .order_by(Post.id).first()
        tag_id_list = [post_tag.tag_id for post_tag in PostTag.query.filter(PostTag.post_id == post.id).all()]
        tag_list = [tag.tag for tag in Tag.query.filter(Tag.id.in_(tag_id_list)).all()]

        ogp_meta_tag = OpenGraphGenerator(site_name=settings.blog_title,
                                          title=post.title,
                                          description=post.content[:300],
                                          url=post.link,
                                          image=post.featured_image
                                          )

        return render_template("/themes/"+settings.theme+"/post_detail.html",
                               author=author,
                               ogp_meta_tag=ogp_meta_tag(),
                               settings=settings,
                               prev_post=prev_post.for_detail if prev_post else None,
                               next_post=next_post.for_detail if next_post else None,
                               post=post.for_detail,
                               tag_list=tag_list
                               )
    else:
        abort(404)

