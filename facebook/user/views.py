from django.shortcuts import render, redirect  
from .models import User_Data, Post, Friend  
from django.contrib import messages   
from django.core.mail import send_mail
from django.conf import settings   
import uuid  
import os
import ssl
  
def homepage(request):  
   if 'user_id' not in request.session:  
      return render(request, 'homepage_guest.html')    
   return redirect('profile')  
  
def profile(request):  
   user = User_Data.objects.get(id=request.session['user_id'])  
   posts = Post.objects.filter(user=user).order_by('-created_at')  
   friends = Friend.objects.filter(user=user).values_list('friend', flat=True)  
   friend_list = User_Data.objects.filter(id__in=friends)  
   newsfeed_posts = Post.objects.filter(user__in=friend_list).order_by('-created_at')  
  
   if request.method == 'POST':  
      if user.profile_picture:  
        profile_picture_url = user.profile_picture.url  
      else:  
        profile_picture_url = "https://picsum.photos/50/50"  
      user.bio = request.POST.get('bio', user.bio)  
      user.work = request.POST.get('work', user.work)  
      user.education = request.POST.get('education', user.education)  
      user.location = request.POST.get('location', user.location)  
      user.save()  
      if 'content' in request.POST:  
        content = request.POST.get('content')  
        if content:  
           Post.objects.create(content=content, user=user)  
        return redirect('profile')  
  
   context = {  
      'user': user,  
      'posts': posts,  
      'edit': request.GET.get('edit') == 'true',  
      'friends': friend_list,  
      'newsfeed_posts': newsfeed_posts,  
   }  
   return render(request, 'profile.html', context)

  
def signup(request):  
    if request.method == 'POST':  
        username = request.POST.get('username')  
        password = request.POST.get('password')  
        first_name = request.POST.get('first_name')  
        surname = request.POST.get('surname')  
        mobile_number = request.POST.get('mobile_number')  
        email = request.POST.get('email')  
        dob = request.POST.get('dob')  
        gender = request.POST.get('gender')   
        if User_Data.objects.filter(username=username).exists():  
            error_message = "Username already exists. Please choose a different username."  
            return render(request, 'signup.html', {'error_message': error_message})  
        if User_Data.objects.filter(email=email).exists():  
            error_message = "Email already exists. Please use a different email."  
            return render(request, 'signup.html', {'error_message': error_message})  
  
        user = User_Data(  
            username=username,  
            password=password,  
            first_name=first_name,  
            surname=surname,  
            mobile_number=mobile_number,  
            email=email,  
            dob=dob,  
            gender=gender  
        )  
        user.save()  
  
        send_mail(
            'Welcome to our platform!',
            f'Dear {first_name},\n\nThank you for signing up with us! We are excited to have you on board.\n\nBest regards,\n[Your Platform Name]',
            settings.EMAIL_HOST_USER,
            [email], 
            fail_silently=False
        )  
  
        messages.success(request, 'Signup successful! Please login to continue.')  
        return redirect('login')  
  
    return render(request, 'signup.html')

def login(request):  
   error_message = None  
    
   if request.method == 'POST':  
      username = request.POST.get('username')  
      password = request.POST.get('password')  
       
      try:  
        user = User_Data.objects.get(username=username)  
        if user.password == password:  
           request.session['user_id'] = user.id  
           return redirect('homepage')  
        else:  
           error_message = 'Invalid Password'  
      except User_Data.DoesNotExist:  
        error_message = 'Invalid username or password'  
    
   return render(request, 'homepage_guest.html', {'error_message': error_message})  
  
def logout(request):  
   if 'user_id' in request.session:  
      del request.session['user_id']  
   return redirect('login')  
  
def handle_uploaded_file(f):  
   filename = f"{uuid.uuid4()}.jpg"  
   filepath = f"profile_pictures/{filename}"  
   with open(filepath, 'wb+') as destination:  
      for chunk in f.chunks():  
        destination.write(chunk)  
   return f"/media/{filepath}"
  

def search_users(request):  
   query = request.GET.get('query')  
   if query is None:  
      query = ''  
   users = User_Data.objects.filter(username__icontains=query)  
   return render(request, 'search_user.html', {'users': users})
  
def add_friend(request, user_id):  
   user = User_Data.objects.get(id=request.session['user_id'])  
   friend = User_Data.objects.get(id=user_id)  
   Friend.objects.create(user=user, friend=friend)  
   return redirect('friends')  
  
def friends(request):  
   user = User_Data.objects.get(id=request.session['user_id'])  
   friends = Friend.objects.filter(user=user).values_list('friend', flat=True)  
   friend_list = User_Data.objects.filter(id__in=friends)  
   return render(request, 'friends.html', {'friends': friend_list})

def google_signup(request):  
   if request.method == 'POST':  
      username = request.POST.get('username')  
      password = request.POST.get('password')  
      first_name = request.POST.get('first_name')  
      surname = request.POST.get('surname')  
      mobile_number = request.POST.get('mobile_number')  
      email = request.POST.get('email')  
      dob = request.POST.get('dob')  
      gender = request.POST.get('gender')  
    
      if User_Data.objects.filter(email=email).exists():  
        error_message = "Email already exists. Please use a different email."  
        return render(request, 'google_signup.html', {'error_message': error_message})  
  
      user = User_Data(  
        username=username,  
        password=password,  
        first_name=first_name,  
        surname=surname,  
        mobile_number=mobile_number,  
        email=email,  
        dob=dob,  
        gender=gender  
      )  
      user.save()  
      subject = 'Welcome to our platform!'  
      message = f'Dear {first_name},\n\nThank you for signing up with us! We are excited to have you on board.\n\nBest regards,\n[Your Name]'  
      from_email = settings.EMAIL_HOST_USER  
      to_email = email  
      send_mail(subject, message, from_email, [to_email], fail_silently=False)  
      messages.success(request, 'Signup successful! Please login to continue.')  
  
      return redirect('login')   
   return render(request, 'google_signup.html')

def unfriend(request, friend_id):  
   user = User_Data.objects.get(id=request.session['user_id'])  
   friend = User_Data.objects.get(id=friend_id)  
   try:  
      Friend.objects.filter(user=user, friend=friend).delete()  
   except Friend.DoesNotExist:  
      messages.error(request, 'You are not friends with this person.')  
   return redirect('friends')



