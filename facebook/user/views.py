from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import User_Data, Post, Friend, Like, Comment, CommentLike


# ================= HOME =================
def homepage(request):
    if 'user_id' not in request.session:
        return render(request, 'homepage_guest.html')
    return redirect('home')


def home(request):
    if 'user_id' not in request.session:
        return redirect('homepage')

    user = User_Data.objects.get(id=request.session['user_id'])

    # HANDLE POST FIRST
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if content or image or video:
            post = Post(user=user, content=content)
            if image:
                post.image = image
            if video:
                post.video = video
            post.save()

        return redirect('home')

    friends_ids = Friend.objects.filter(
        user=user
    ).values_list('friend', flat=True)

    posts = (
        Post.objects
        .filter(user__in=list(friends_ids) + [user.id])
        .select_related('user')
        .order_by('-created_at')
    )

    for post in posts:
        post.is_liked = post.likes.filter(user=user).exists()

    contacts = User_Data.objects.filter(id__in=friends_ids).distinct()

    return render(request, 'home.html', {
        'user': user,
        'posts': posts,
        'contacts': contacts,
    })


# ================= PROFILE =================
def profile(request, user_id=None):
    if 'user_id' not in request.session:
        return redirect('login')

    logged_in_user = get_object_or_404(
        User_Data, id=request.session['user_id']
    )

    profile_user = (
        get_object_or_404(User_Data, id=user_id)
        if user_id else logged_in_user
    )

    # ===== CREATE POST (ONLY OWN PROFILE) =====
    if request.method == "POST" and profile_user == logged_in_user:
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if content or image or video:
            post = Post(user=logged_in_user, content=content)
            if image:
                post.image = image
            if video:
                post.video = video
            post.save()

        return redirect('profile')

    friendship = Friend.objects.filter(
        user=logged_in_user,
        friend=profile_user
    ).first()

    reverse_friendship = Friend.objects.filter(
        user=profile_user,
        friend=logged_in_user
    ).first()

    friendship_status = None
    if friendship and friendship.status == 'accepted':
        friendship_status = 'friends'
    elif reverse_friendship and reverse_friendship.status == 'accepted':
        friendship_status = 'friends'
    elif friendship and friendship.status == 'pending':
        friendship_status = 'request_sent'
    elif reverse_friendship and reverse_friendship.status == 'pending':
        friendship_status = 'request_received'

    posts = (
        Post.objects
        .filter(user=profile_user)
        .select_related('user')
        .prefetch_related('likes', 'comments__user', 'comments__children')
        .order_by('-created_at')
    )

    for post in posts:
        post.is_liked = post.likes.filter(user=logged_in_user).exists()

    friend_relations = Friend.objects.filter(
        Q(user=profile_user) | Q(friend=profile_user),
        status='accepted'
    )

    friend_ids = {
        fr.friend_id if fr.user_id == profile_user.id else fr.user_id
        for fr in friend_relations
    }

    friends = User_Data.objects.filter(id__in=friend_ids)

    photos = (
        Post.objects
        .filter(user=profile_user, image__isnull=False)
        .exclude(image='')
        .order_by('-created_at')[:9]
    )

    return render(request, 'profile.html', {
        'user': profile_user,
        'posts': posts,
        'friends': friends,
        'photos': photos,
        'friendship_status': friendship_status,
        'is_own_profile': profile_user == logged_in_user,
    })

def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User_Data.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']

        if request.FILES.get('cover_photo'):
            user.cover_photo = request.FILES['cover_photo']

        user.first_name = request.POST.get('first_name')
        user.surname = request.POST.get('surname')
        user.bio = request.POST.get('bio')
        user.work = request.POST.get('work')
        user.education = request.POST.get('education')
        user.location = request.POST.get('location')

        user.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': user})

# ================= AUTH =================
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User_Data.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        if User_Data.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        User_Data.objects.create(
            username=username,
            password=password,
            email=email
        )
        return redirect('login')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User_Data.objects.get(username=username)
            if user.password == password:
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                messages.error(request, 'Invalid password')
        except User_Data.DoesNotExist:
            messages.error(request, 'User does not exist')

    return render(request, 'homepage_guest.html')


def logout(request):
    request.session.flush()
    return redirect('login')


def google_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User_Data.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('google_signup')

        User_Data.objects.create(
            username=username,
            password=password,
            email=email
        )

        messages.success(request, 'Signup successful. Please login.')
        return redirect('login')

    return render(request, 'google_signup.html')


# ================= FRIENDS =================
def search_users(request):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = User_Data.objects.get(id=request.session['user_id'])
    query = request.GET.get('q', '')

    users = User_Data.objects.exclude(id=current_user.id)

    if query:
        users = users.filter(username__icontains=query)

    # accepted friends
    friends_ids = Friend.objects.filter(
        user=current_user,
        status='accepted'
    ).values_list('friend_id', flat=True)

    # sent requests
    sent_ids = Friend.objects.filter(
        user=current_user,
        status='pending'
    ).values_list('friend_id', flat=True)

    # received requests
    received_ids = Friend.objects.filter(
        friend=current_user,
        status='pending'
    ).values_list('user_id', flat=True)

    return render(request, 'search.html', {
        'users': users,
        'friends_ids': friends_ids,
        'sent_ids': sent_ids,
        'received_ids': received_ids,
        'query': query
    })

def get_friend_status(current_user, profile_user):
    try:
        fr = Friend.objects.get(
            user=current_user,
            friend=profile_user
        )
        return fr.status

    except Friend.DoesNotExist:
        try:
            fr = Friend.objects.get(
                user=profile_user,
                friend=current_user
            )
            if fr.status == 'pending':
                return 'request_received'
            return 'accepted'
        except Friend.DoesNotExist:
            return 'not_friends'

@require_POST
def send_friend_request(request, user_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    target = get_object_or_404(User_Data, id=user_id)

    if user != target:
        Friend.objects.get_or_create(
            user=user,
            friend=target,
            defaults={'status': 'pending'}
        )

    return redirect('search_users')

@require_POST
def cancel_friend_request(request, user_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    Friend.objects.filter(
        user=user,
        friend_id=user_id,
        status='pending'
    ).delete()

    return redirect('search_users')

@require_POST
def accept_friend(request, user_id):
    logged_in_user = User_Data.objects.get(id=request.session['user_id'])
    sender = get_object_or_404(User_Data, id=user_id)

    req = Friend.objects.filter(
        user=sender,
        friend=logged_in_user,
        status='pending'
    ).first()

    if req:
        req.status = 'accepted'
        req.save()

        Friend.objects.get_or_create(
            user=logged_in_user,
            friend=sender,
            defaults={'status': 'accepted'}
        )

    return redirect('search_users')

@require_POST
def reject_friend_request(request, user_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    Friend.objects.filter(
        user_id=user_id,
        friend=user,
        status='pending'
    ).delete()

    return redirect('search_users')

@require_POST
def remove_friend(request, user_id):
    logged_in_user = User_Data.objects.get(id=request.session['user_id'])
    other_user = get_object_or_404(User_Data, id=user_id)

    Friend.objects.filter(
        user=logged_in_user,
        friend=other_user,
        status='accepted'
    ).delete()

    Friend.objects.filter(
        user=other_user,
        friend=logged_in_user,
        status='accepted'
    ).delete()

    return redirect('search_users')

# ================= POST INTERACTIONS =================
def like_post(request, post_id):
    if request.method == 'POST':
        user = User_Data.objects.get(id=request.session['user_id'])
        post = get_object_or_404(Post, id=post_id)

        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def add_comment(request, post_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    post = get_object_or_404(Post, id=post_id)

    content = request.POST.get('content')
    parent_id = request.POST.get('parent')

    if content:
        Comment.objects.create(
            user=user,
            post=post,
            content=content,
            parent_id=parent_id if parent_id else None
        )

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def edit_post(request, post_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    post = get_object_or_404(Post, id=post_id)

    if post.user != user:
        return redirect('profile')

    if request.method == 'POST':
        post.content = request.POST.get('content')
        post.save()
        return redirect('profile')

    return render(request, 'edit_post.html', {'post': post})


def delete_post(request, post_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    post = get_object_or_404(Post, id=post_id)

    if post.user == user:
        post.delete()

    return redirect(request.META.get('HTTP_REFERER', 'profile'))
 
def like_comment(request, comment_id):
    user = User_Data.objects.get(id=request.session['user_id'])
    comment = get_object_or_404(Comment, id=comment_id)

    like, created = CommentLike.objects.get_or_create(
        user=user,
        comment=comment
    )

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))