from django.db import models
from .static_data import TYPE,GENDER,AGE
from django.utils import timezone
# Create your models here.
class Members(models.Model):
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    username=models.CharField(max_length=15,unique=True)
    password=models.CharField(max_length=25)
    gender=models.CharField(max_length=255,choices=GENDER,default='Male')
    age=models.IntegerField(default=18)

class Hostels(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    hostel_name=models.CharField(max_length=255,default='')
    creation_date=models.DateField(default=timezone.now)

class Blocks(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    block_name=models.CharField(max_length=100)
    total_rooms=models.IntegerField()
    room_strength=models.CharField(max_length=100)
    creation_date=models.DateField(default=timezone.now)

class Beds(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    block_id=models.CharField(max_length=255,default=None)
    room_no=models.IntegerField(default=1)
    bed_no=models.IntegerField(default=1)
    bed_status=models.CharField(max_length=100,default='available')
    person_name=models.CharField(max_length=255,null=True,blank=True)
    person_age=models.CharField(max_length=100,null=True,blank=True)
    payment=models.CharField(max_length=100,null=True,blank=True)
    added_date=models.DateField(default=timezone.now)

class Leaved_person(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    bed=models.ForeignKey(Beds,on_delete=models.CASCADE)
    person_name=models.CharField(max_length=255)
    person_age=models.CharField(max_length=255)
    added_date=models.DateField(default=None)
    leave_date=models.DateField(default=timezone.now)
    
class In_out(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    bed_id=models.CharField(max_length=255,default=None)
    person_name=models.CharField(max_length=255,null=True,blank=True)
    in_out_status=models.CharField(max_length=255,null=True,blank=True)
    date=models.DateField(default=timezone.now)
    time=models.TimeField(default=timezone.now)

class visitors(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    visitor_name=models.CharField(max_length=255)
    whome_to_meet=models.CharField(max_length=255)
    in_time=models.DateTimeField(default=timezone.now)
    out_time=models.DateTimeField(blank=True,null=True)

