from django.db import models  
  
class User_Data(models.Model):  
  username = models.CharField(max_length=100, unique=True)  
  password = models.CharField(max_length=100)  
  first_name = models.CharField(default='', max_length=100)  
  surname = models.CharField(default='', max_length=100)  
  mobile_number = models.CharField(default='0000000000', max_length=15)  
  email = models.EmailField(default='example@example.com', max_length=254, unique=True)  
  dob = models.DateField()  
  gender = models.CharField(default='unknown', max_length=10)  
  profile_picture = models.URLField(blank=True, null=True)  # Store URL instead of ImageField  
  bio = models.TextField(default='This is a default bio.')  
  work = models.CharField(default='Current work information.', max_length=255)  
  education = models.CharField(default='Education details here.', max_length=255)  
  location = models.CharField(default='Location information.', max_length=255)
  profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
  
class Post(models.Model):  
  content = models.TextField()  
  created_at = models.DateTimeField(auto_now_add=True)  
  user = models.ForeignKey(User_Data, on_delete=models.CASCADE)  
  
class Friend(models.Model):  
  user = models.ForeignKey(User_Data, related_name='user', on_delete=models.CASCADE)  
  friend = models.ForeignKey(User_Data, related_name='friends', on_delete=models.CASCADE)




