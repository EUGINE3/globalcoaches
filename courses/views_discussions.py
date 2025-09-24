from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from programs.models import ProgramModule
from .models import (
    ModuleTopic, ModuleDiscussion, TopicDiscussion, 
    DiscussionPost, DiscussionLike, DiscussionView
)
from .utils import ProgressiveAccessManager


@login_required
def module_discussion(request, module_id):
    """Module discussion forum"""
    program_module = get_object_or_404(ProgramModule, id=module_id, is_active=True)
    
    # Check access
    if not ProgressiveAccessManager.can_access_program_module(request.user, program_module):
        messages.error(request, 'You need to complete previous modules before accessing this discussion.')
        return redirect('courses:progressive_modules')
    
    # Get or create discussion
    discussion, created = ModuleDiscussion.objects.get_or_create(
        program_module=program_module,
        defaults={
            'title': f"{program_module.module.name} Discussion",
            'description': f"Discussion forum for {program_module.module.name}"
        }
    )
    
    # Handle new post submission
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if title and content:
            parent_post = None
            if parent_id:
                parent_post = get_object_or_404(DiscussionPost, id=parent_id, module_discussion=discussion)
            
            DiscussionPost.objects.create(
                module_discussion=discussion,
                author=request.user,
                title=title,
                content=content,
                parent_post=parent_post
            )
            messages.success(request, 'Your post has been added successfully!')
            return redirect('courses:module_discussion', module_id=module_id)
    
    # Get posts with pagination
    posts = discussion.posts.filter(parent_post=None, is_approved=True).order_by('-is_pinned', '-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)
    
    # Track view
    DiscussionView.objects.update_or_create(
        module_discussion=discussion,
        user=request.user,
        defaults={'last_viewed_at': timezone.now()}
    )
    
    context = {
        'program_module': program_module,
        'discussion': discussion,
        'posts': page_posts,
        'total_posts': discussion.total_posts,
    }
    return render(request, 'courses/module_discussion.html', context)


@login_required
def topic_discussion(request, topic_id):
    """Topic discussion forum"""
    topic = get_object_or_404(ModuleTopic, id=topic_id, is_active=True)
    program_module = topic.program_module
    
    # Check access
    if not ProgressiveAccessManager.can_access_program_module(request.user, program_module):
        messages.error(request, 'You need to complete previous modules before accessing this discussion.')
        return redirect('courses:progressive_modules')
    
    # Get or create discussion
    discussion, created = TopicDiscussion.objects.get_or_create(
        topic=topic,
        defaults={
            'title': f"{topic.title} Discussion",
            'description': f"Discussion forum for {topic.title}"
        }
    )
    
    # Handle new post submission
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if title and content:
            parent_post = None
            if parent_id:
                parent_post = get_object_or_404(DiscussionPost, id=parent_id, topic_discussion=discussion)
            
            DiscussionPost.objects.create(
                topic_discussion=discussion,
                author=request.user,
                title=title,
                content=content,
                parent_post=parent_post
            )
            messages.success(request, 'Your post has been added successfully!')
            return redirect('courses:topic_discussion', topic_id=topic_id)
    
    # Get posts with pagination
    posts = discussion.posts.filter(parent_post=None, is_approved=True).order_by('-is_pinned', '-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)
    
    # Track view
    DiscussionView.objects.update_or_create(
        topic_discussion=discussion,
        user=request.user,
        defaults={'last_viewed_at': timezone.now()}
    )
    
    context = {
        'topic': topic,
        'program_module': program_module,
        'discussion': discussion,
        'posts': page_posts,
        'total_posts': discussion.total_posts,
    }
    return render(request, 'courses/topic_discussion.html', context)


@login_required
def discussion_post_detail(request, post_id):
    """View individual discussion post with replies"""
    post = get_object_or_404(DiscussionPost, id=post_id, is_approved=True)
    
    # Check access based on discussion type
    if post.module_discussion:
        if not ProgressiveAccessManager.can_access_program_module(request.user, post.module_discussion.program_module):
            messages.error(request, 'Access denied.')
            return redirect('courses:progressive_modules')
    elif post.topic_discussion:
        if not ProgressiveAccessManager.can_access_program_module(request.user, post.topic_discussion.topic.program_module):
            messages.error(request, 'Access denied.')
            return redirect('courses:progressive_modules')
    
    # Handle reply submission
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if title and content:
            DiscussionPost.objects.create(
                module_discussion=post.module_discussion,
                topic_discussion=post.topic_discussion,
                author=request.user,
                title=title,
                content=content,
                parent_post=post
            )
            messages.success(request, 'Your reply has been added successfully!')
            return redirect('courses:discussion_post_detail', post_id=post_id)
    
    # Get replies
    replies = post.replies.filter(is_approved=True).order_by('created_at')
    
    context = {
        'post': post,
        'replies': replies,
        'can_reply': post.can_reply(request.user),
    }
    return render(request, 'courses/discussion_post_detail.html', context)


@login_required
@require_POST
def like_post(request, post_id):
    """Like/unlike a discussion post"""
    post = get_object_or_404(DiscussionPost, id=post_id, is_approved=True)
    
    # Check access
    if post.module_discussion:
        if not ProgressiveAccessManager.can_access_program_module(request.user, post.module_discussion.program_module):
            return JsonResponse({'error': 'Access denied'}, status=403)
    elif post.topic_discussion:
        if not ProgressiveAccessManager.can_access_program_module(request.user, post.topic_discussion.topic.program_module):
            return JsonResponse({'error': 'Access denied'}, status=403)
    
    like, created = DiscussionLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # Unlike
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })


@login_required
@require_POST
def delete_post(request, post_id):
    """Delete a discussion post (author or staff only)"""
    post = get_object_or_404(DiscussionPost, id=post_id)
    
    if not post.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('courses:discussion_post_detail', post_id=post_id)
    
    # Determine redirect URL
    if post.module_discussion:
        redirect_url = 'courses:module_discussion'
        redirect_id = post.module_discussion.program_module.id
    elif post.topic_discussion:
        redirect_url = 'courses:topic_discussion'
        redirect_id = post.topic_discussion.topic.id
    else:
        redirect_url = 'courses:progressive_modules'
        redirect_id = None
    
    post.delete()
    messages.success(request, 'Post deleted successfully.')
    
    if redirect_id:
        return redirect(redirect_url, redirect_id)
    else:
        return redirect(redirect_url)
