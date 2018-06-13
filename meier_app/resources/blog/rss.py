# -*- coding:utf-8 -*-
from flask import Blueprint
from sqlalchemy import desc

from meier_app.models.post import Post, PostVisibility, PostStatus
from meier_app.models.post_tag import PostTag
from meier_app.models.settings import Settings
from meier_app.models.tag import Tag
from meier_app.models.user import User

rss = Blueprint('rss', __name__, url_prefix='/rss')


@rss.route('', methods=['GET'])
def get_rss():
    from datetime import timezone
    from feedgen.feed import FeedGenerator
    settings = Settings.query.first()
    author = User.query.first()
    fg = FeedGenerator()
    fg.title(settings.blog_title)
    fg.author({'name': author.user_name, 'email': author.email})
    fg.link(href=settings.domain, rel='alternate')
    fg.description(description=settings.blog_desc)
    post_paging_result = Post.query.filter(Post.status == PostStatus.PUBLISH.value) \
        .filter(Post.is_page == False) \
        .filter(Post.visibility == PostVisibility.PUBLIC.value) \
        .order_by(desc(Post.in_date)).limit(15).all()

    post_paging_result = reversed(post_paging_result)
    for post in post_paging_result:
        tag_id_list = [post_tag.tag_id for post_tag in PostTag.query.filter(PostTag.post_id == post.id).all()]
        tag_list = [tag.tag for tag in Tag.query.filter(Tag.id.in_(tag_id_list)).all()]
        fe = fg.add_entry()
        fe.author({'name': author.user_name, 'email': author.email})
        for tag in tag_list:
            fe.category([{'term': tag,
                          'scheme': None,
                          'label': tag,
                          }])
        fe.title(post.title)
        fe.description(description='<![CDATA[ ' + post.html[:200] + ' ]]>')
        fe.content(content=post.html, type='CDATA')
        fe.link(href=settings.domain + "/" + post.post_name, rel='alternate')
        fe.pubdate(str(post.in_date.astimezone(timezone.utc)))
        fe.id(post.post_name)

    rss_feed = fg.rss_str(pretty=True)
    from flask import Response
    return Response(rss_feed, mimetype='text/xml')
