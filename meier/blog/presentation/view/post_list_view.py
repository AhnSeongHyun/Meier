import random

from flask import Blueprint, render_template, request
from sqlalchemy import desc

from meier.blog.presentation.view.sort import PostListSort
from meier.models.notification import Notification
from meier.models.post import Post, PostStatus, PostVisibility
from meier.models.settings import Settings
from meier.models.user import User
from meier.blog.services.opengraph import OpenGraphMetaTagGenerator

post_list_view = Blueprint("post_list_view", __name__, url_prefix="/")
post_list_sort_map = {
    PostListSort.UPDATE_DATE_DESC: desc(Post.mo_date),
    PostListSort.CREATE_DATE_DESC: desc(Post.in_date),
    PostListSort.RANDOM: desc(Post.in_date),
}


@post_list_view.route("", methods=["GET"])
def get_post_list_view():
    author = User.query.first()
    page = int(request.args.get("page", 1))
    sort = PostListSort(
        request.args.get("sort", PostListSort.CREATE_DATE_DESC.value)
    )

    order_by = post_list_sort_map[sort]

    settings = Settings.query.first()
    post_paging_result = (
        Post.query.filter(Post.status == PostStatus.PUBLISH.value)
        .filter(Post.is_page.is_(False))
        .filter(Post.visibility == PostVisibility.PUBLIC.value)
        .order_by(order_by)
        .paginate(page, settings.post_per_page, error_out=False)
    )
    post_list = [post.for_detail for post in post_paging_result.items]
    if sort == PostListSort.RANDOM:
        random.shuffle(post_list)
    first_post = post_list[0]
    ogp_meta_tag = OpenGraphMetaTagGenerator(
        site_name=settings.blog_title,
        title=first_post.get("title", None),
        description=first_post.get("content", None)[:300],
        url=first_post.get("link", None),
        image=first_post.get("featured_image", None),
    )

    notifications = Notification.query.all()

    return render_template(
        f"themes/{settings.theme}/post_list.html",
        author=author,
        ogp_meta_tag=ogp_meta_tag(),
        settings=settings,
        total_pages=post_paging_result.pages,
        notifications=notifications,
        post_list=post_list,
        has_next=post_paging_result.has_next,
        next=f"?page={page+1}",
        has_prev=post_paging_result.has_prev,
        prev=f"?page={page-1}",
    )
