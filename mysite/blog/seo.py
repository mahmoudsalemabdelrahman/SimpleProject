# blog/seo.py
"""Utility functions to generate JSON‑LD schema markup for SEO.
Used in templates via the ``seo_context`` context processor.
"""
import json
from django.urls import reverse
from .models import Course, Post, Review


def course_schema(course):
    """Return JSON‑LD dict for a Course object."""
    return {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": course.title,
        "description": course.description,
        "url": reverse('course_detail', args=[course.id]),
        "provider": {
            "@type": "Organization",
            "name": "Your Platform Name",
            "sameAs": "https://yourdomain.com",
        },
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "online",
            "offers": {
                "@type": "Offer",
                "price": float(course.price) if course.price else 0,
                "priceCurrency": "USD",
            },
        },
    }


def article_schema(post):
    """Return JSON‑LD dict for a BlogPosting (article) object."""
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "image": post.image.url if getattr(post, 'image', None) else None,
        "author": {
            "@type": "Person",
            "name": post.author.get_full_name() if hasattr(post, 'author') else "",
        },
        "datePublished": post.created_at.isoformat() if hasattr(post, 'created_at') else None,
        "dateModified": post.updated_at.isoformat() if hasattr(post, 'updated_at') else None,
        "articleBody": post.content if hasattr(post, 'content') else "",
        "url": reverse('post_detail', args=[post.slug]),
    }


def review_schema(review):
    """Return JSON‑LD dict for a Review object."""
    return {
        "@context": "https://schema.org",
        "@type": "Review",
        "author": {
            "@type": "Person",
            "name": review.user.get_full_name() if hasattr(review, 'user') else "",
        },
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": review.rating,
            "bestRating": 5,
        },
        "reviewBody": review.comment,
        "datePublished": review.created_at.isoformat() if hasattr(review, 'created_at') else None,
        "itemReviewed": {
            "@type": "Course",
            "name": review.course.title if hasattr(review, 'course') else "",
        },
    }


def breadcrumb_schema(request, crumbs):
    """Generate BreadcrumbList schema.
    ``crumbs`` should be a list of tuples (name, url).
    """
    item_list = []
    for idx, (name, url) in enumerate(crumbs, start=1):
        item = {
            "@type": "ListItem",
            "position": idx,
            "name": name,
            "item": request.build_absolute_uri(url),
        }
        item_list.append(item)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list,
    }


def render_schema(schema_dict):
    """Return a safe <script type="application/ld+json"> tag string."""
    json_ld = json.dumps(schema_dict, ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">{json_ld}</script>'
