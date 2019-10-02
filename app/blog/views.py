from flask import render_template, flash, current_app, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import blog
from .. import db, uploads
from ..models import Post, User, Follow, Comment, Permission
from .forms import PostForm, CommentForm
from ..decorators import permission_required_in, permission_required_eq
from os import remove


@blog.route('/', methods=['GET', 'POST'])
def index_posts():
    page = request.args.get('page', 1, type=int)
    paginator = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    return render_template('blog/posts-page.html', posts=paginator.items, paginator=paginator)


@blog.route('/<string:username>/posts', methods=['GET'])
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    paginator = Post.query.filter_by(author_id=user.id).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    return render_template('blog/user-posts-page.html', user=user, posts=paginator.items, paginator=paginator)


@blog.route('/show/post/<int:identifier>', methods=['GET', 'POST'])
def show_post(identifier):
    post = Post.query.filter_by(id=identifier).first_or_404()
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit() and current_user.can(Permission.COMMENT):
        comment = Comment(author=current_user, body=form.body.data, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment is created')
        return redirect(url_for('.show_post', identifier=post.id))

    paginator = db.session.query(Comment).filter_by(post=post, disabled=False).paginate(page, per_page=current_app.config['FLASKY_COMMENT_PER_PAGE'], error_out=False)

    return render_template('blog/show-post-page.html', form=form, post=post, comments=paginator.items, paginator=paginator)


@blog.route('/delete/post/<int:identifier>', methods=['POST'])
@login_required
def delete_post(identifier):
    post = Post.query.filter_by(id=identifier).first_or_404()
    if post.is_author(current_user) or current_user.is_administrator():

        db.session.delete(post)
        db.session.commit()
        if post.image_filename is not None:
            remove(uploads.path(post.image_filename))

        flash('The post has been deleted')
        return redirect(url_for('.index_posts'))

    abort(401)


@blog.route('/edit/post/<int:identifier>', methods=['POST', 'GET'])
@login_required
def edit_post(identifier):
    post = Post.query.filter_by(id=identifier).first_or_404()
    if not post.is_author(current_user) and not current_user.is_administrator():
        abort(401)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.image_filename = uploads.save(form.file.data)
        flash('The post has been updated')
        db.session.commit()
        return redirect(url_for('.show_post', identifier=post.id))

    form.title.data = post.title
    form.body.data = post.body
    form.file.data = post.image_filename

    return render_template('blog/edit-post-page.html', form=form)


@blog.route('/new/post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        filename = uploads.save(form.file.data)
        post = Post(title=form.title.data, body=form.body.data, image_filename=filename, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('Your Post is created')
        return redirect(url_for('.index_posts'))

    return render_template('blog/new-post-page.html', form=form)


@blog.route('/followers/<string:username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    paginator = db.session.query(User). \
        filter(Follow.follower_id == user.id). \
        join(Follow, Follow.followed_id == User.id). \
        order_by(Follow.timestamp.desc()). \
        paginate(page, per_page=current_app.config['FLASKY_FOLLOWER_PER_PAGE'], error_out=True)
    return render_template('blog/user-followers-page.html', user=user, followers=paginator.items, paginator=paginator)


@blog.route('/following/<string:username>')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    paginator = db.session.query(User). \
        filter(Follow.followed_id == user.id). \
        join(Follow, Follow.follower_id == User.id). \
        order_by(Follow.timestamp.desc()). \
        paginate(page, per_page=current_app.config['FLASKY_FOLLOWED_PER_PAGE'], error_out=True)
    return render_template('blog/user-following-page.html', user=user, following=paginator.items, paginator=paginator)


@blog.route('/follow/<string:username>')
@login_required
@permission_required_eq(Permission.FOLLOW)
def follow_user(username):
    user_to_follow = User.query.filter_by(username=username).first_or_404()

    if not current_user.is_following(user_to_follow):
        follow_object = Follow(follower_id=user_to_follow.id, followed_id=current_user.id)
        db.session.add(follow_object)
        db.session.commit()
        flash('You are now following %s.' % username)
    else:
        flash('You are already following this user.')

    return redirect(url_for('.following', username=current_user.username))


@blog.route('/un-follow/<string:username>')
@login_required
@permission_required_eq(Permission.FOLLOW)
def un_follow_user(username):
    user_to_un_follow = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user_to_un_follow):
        follow_object = Follow.query.filter_by(follower_id=user_to_un_follow.id, followed_id=current_user.id).first()
        db.session.delete(follow_object)
        db.session.commit()
        flash('You are now not following %s.' % username)
    else:
        flash('You are already not following this user.')

    return redirect(url_for('.following', username=current_user.username))


@blog.route('/comment/edit/<int:identifier>', methods=['GET', 'POST'])
@login_required
@permission_required_in(Permission.ADMIN, Permission.MODERATE)
def edit_comment(identifier):
    comment = Comment.query.filter_by(id=identifier).first_or_404()
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit() and current_user.can(Permission.COMMENT):
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('Your comment is updated')
        return redirect(url_for('.show_post', identifier=comment.post_id))

    form.body.data = comment.body

    paginator = db.session.query(Comment).filter_by(post=comment.post, disabled=False).\
        paginate(page, per_page=current_app.config['FLASKY_COMMENT_PER_PAGE'], error_out=False)

    return render_template('blog/show-post-page.html', scroll='js-comment-section', form=form, post=comment.post, comments=paginator.items,
                           paginator=paginator)


@blog.route('/comment/disable/<int:identifier>', methods=['POST'])
@login_required
@permission_required_in(Permission.ADMIN, Permission.MODERATE)
def disable_comment(identifier):
    comment = Comment.query.get_or_404(identifier)
    if not comment.disabled:
        comment.disabled = True
        db.session.commit()
        flash('This comment is disabled')
    else:
        flash('This comment is already disabled')

    return redirect(url_for('.show_post', identifier=comment.post_id))


@blog.route('/comment/enable/<int:identifier>', methods=['POST'])
@login_required
@permission_required_in(Permission.ADMIN, Permission.MODERATE)
def enable_comment(identifier):
    comment = Comment.query.get_or_404(identifier)
    if comment.disabled:
        comment.disabled = False
        db.session.commit()
        flash('This comment is enabled')
    else:
        flash('This comment is already enabled')

    return redirect(url_for('.show_post', identifier=comment.post_id))