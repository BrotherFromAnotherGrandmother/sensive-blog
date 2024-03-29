from django.db.models import Count, Prefetch
from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag


def serialize_post_updated(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_updated(tag) for tag in post.tags.all().annotate(posts_by_tag=Count('posts'))],
        'first_tag_title': post.tags.first().title,
    }


def serialize_tag_updated(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_by_tag,
    }


def index(request):
    posts = Post.objects.all().prefetch_tags()

    fresh_posts = posts.order_by('published_at') \
        .annotate(comments_count=Count('comments')) \
        .prefetch_related('author')

    most_fresh_posts = list(fresh_posts)[-5:]
    most_popular_posts = posts.popular().prefetch_related('author')[:5].fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular().annotate(posts_by_tag=Count('posts'))[:5]

    context = {
        'most_popular_posts': [
            serialize_post_updated(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_updated(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_updated(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.all(). \
        prefetch_related(Prefetch('tags', queryset=Tag.objects.all()
                                  .annotate(posts_by_tag=Count('posts'))))
    posts = posts.annotate(likes_count=Count('likes'))
    most_popular_posts = Post.objects.popular().prefetch_related('author')[:5].fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular()[:5].annotate(posts_by_tag=Count('posts'))

    post = get_object_or_404(posts.prefetch_related('likes'), slug=slug)
    comments = post.comments.select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all().annotate(posts_by_tag=Count('posts'))

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_updated(tag) for tag in related_tags],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_updated(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_updated(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5].annotate(posts_by_tag=Count('posts'))

    most_popular_posts = Post.objects.popular().prefetch_related('author')[:5].fetch_with_comments_count()

    related_posts = tag.posts.all().prefetch_related('author')[:20].fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_updated(tag) for tag in most_popular_tags],
        'posts': [serialize_post_updated(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_updated(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
