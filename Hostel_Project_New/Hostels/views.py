from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Members,Hostels,Blocks,Beds,Leaved_person,In_out,visitors
from . import forms
import re
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from .decorators import login_check
# Create your views here

def sign_in_view(request):
    if request.session.has_key('ActiveUserUsername'):
        return redirect('homepage')
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        try:
            user=Members.objects.get(username=username,password=password)
            request.session['ActiveUserUsername']=user.username
            request.session['ActiveUserFirstName']=user.first_name
            request.session.set_expiry(0)
            try:
                hostel=Hostels.objects.get(user=user)
            except Hostels.DoesNotExist:
                return redirect('set_hostel_page')
            else:
                request.session['ActiveHostelName']=hostel.hostel_name
                request.session.set_expiry(0)
                return redirect('homepage')
        except Members.DoesNotExist:
            response=redirect('sign_in_page')
            response.set_cookie('alert_danger', 'Invalid Username or Password', 5)
            return response
    return render(request,'hostels/sign_in.html')

def create_new_account_view(request):
    form=forms.registration_forms()
    if request.method=='POST':
        form=forms.registration_forms(request.POST)
        if form.is_valid():
            form.save(commit=True)
            response=redirect('sign_in_page')
            response.set_cookie('alert_success', 'Registered Successfully.', 5)
            return response
    return render(request,'hostels/registration.html',{'form':form})

@login_check
def set_hostel_view(request):
    context={
        'error':'',
        'hostel_name':''
    }
    if request.method=='POST':
        hostel_name=request.POST['hostel_name']
        if hostel_name:
            if not re.match('^[a-zA-Z]{3,15}$',hostel_name):
                context['error']='Hostel Name must be letters only and max 15 digits are allowed.'
                context['hostel_name']=hostel_name
            else:
                username=request.session['ActiveUserUsername']
                user=Members.objects.get(username=username)
                try:
                    hostel=Hostels.objects.get(user=user)
                except Hostels.DoesNotExist:
                    new_hostel=Hostels(user=user,hostel_name=hostel_name)
                    new_hostel.save()
                    logout_view(request)
                    response=redirect('sign_in_page')
                    response.set_cookie('alert_success', 'Hostel Name Set, please log in.', 5)
                    return response 
                else:
                    request.session['ActiveHostelName']=hostel.hostel_name
                    return redirect('dashboard')
        else:
            context['error']='Hostel Name cannot be empty.'
            context['hostel_name']=hostel_name
    return render(request,'hostels/set_hostel.html',context)

@login_check
def homepage_view(request):
    username=request.session['ActiveUserUsername']
    user=Members.objects.get(username=username)
    blocks=Blocks.objects.filter(user=user).values()
    for each in blocks:
        total_beds=Beds.objects.filter(block_id=each['id']).values().count()
        available_beds=Beds.objects.filter(block_id=each['id'],bed_status='available').values().count()
        booked_beds=Beds.objects.filter(block_id=each['id'],bed_status='booked').values().count()
        each['total_beds']=total_beds
        each['available_beds']=available_beds
        each['booked_beds']=booked_beds
    context={
        'blocks':blocks
    }
    return render(request,'hostels/homepage.html',context)

@login_check
def all_enrolled_persons_view(request):
    username=request.session['ActiveUserUsername']
    user=Members.objects.get(username=username)
    persons=Beds.objects.filter(user=user,bed_status='booked').values()
    for each in persons:
        block=Blocks.objects.get(id=each['block_id'])
        each['block_name']=block.block_name
    context={
        'persons':persons
    }
    return render(request,'hostels/all_enrolled.html',context)

@login_check
def all_leaved_persons_view(request):
    username=request.session['ActiveUserUsername']
    user=Members.objects.get(username=username)
    leaved=Leaved_person.objects.filter(user=user).values()
    for each in leaved:
        bed=Beds.objects.get(id=each['bed_id'])
        block=Blocks.objects.get(id=bed.block_id)
        each['block_name']=block.block_name
    context={
        'leaved':leaved
    }
    return render(request,'hostels/leaved.html',context)

def logout_view(request):
    if request.session.has_key('ActiveUserUsername'):
        del request.session['ActiveUserUsername']
    
    if request.session.has_key('ActiveUserFirstName'):
        del request.session['ActiveUserFirstName']

    if request.session.has_key('ActiveHostelName'):
        del request.session['ActiveHostelName']

    response=redirect('sign_in_page') 
    response.set_cookie('alert_success', 'Logout Successful please log in.', 5)
    return response

@login_check
def block_details_view(request,id,user_id):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    if user.id == user_id:
        rooms={}
        block=Blocks.objects.get(id=id)
        for room_no in range(1,int(block.total_rooms)+1):
            all_beds=Beds.objects.filter(user=user,block_id=block.id,room_no=room_no).values().order_by('bed_no')
            total_beds=len(all_beds)
            rooms[room_no]={
                'beds':all_beds,
                'total_beds':total_beds
            }
            
        context={
            'block_name':block.block_name,
            'rooms':rooms,
            'room_strength':block.room_strength
        }
    else:
        context={'block':None}
    return render(request,'hostels/block_details.html',context)

@login_check
def delete_block_view(request,id,user_id):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    if user.id == user_id:
        try:
            block=Blocks.objects.get(id=id)
            block_name=block.block_name
            beds=Beds.objects.filter(user=user,block_id=block.id,bed_status='booked')
            if beds:
                response=redirect('homepage')
                response.set_cookie('alert_danger', 'Block contain person enrolled. first Deallocate those persons.', 5)
                return response
            else:
                available_beds=Beds.objects.filter(user=user,block_id=block.id)
                available_beds.delete()
                block.delete()
                response=redirect('homepage') 
                response.set_cookie('alert_success', f'Block {block_name} Deleted Successfully...', 5)
                return response

        except:
            response=redirect('homepage')
            response.set_cookie('alert_danger', 'Block doesnot exists..', 5)
            return response
    else:
        response=redirect('homepage') 
        response.set_cookie('alert_success', 'Login with valid user....', 5)
        return response
    
@login_check
def delete_leaved_person_view(request,id):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    leaved=Leaved_person.objects.get(user=user,id=id)
    person_name=leaved.person_name
    leaved.delete()
    response=redirect('all_leaved_persons') 
    response.set_cookie('alert_success', f'Deleted {person_name} Successfully..', 5)
    return response

@login_check
def in_out_view(request,date=None):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    todays_date=datetime.now().date();
    if not date:
        today_in_out=In_out.objects.filter(user=user,date=todays_date).values().order_by('-id')
        context={
            'in_out':today_in_out
        }
    else:
        parsed_date=datetime.strptime(date,"%d-%B-%Y")
        today_in_out=In_out.objects.filter(user=user,date=parsed_date.date()).values().order_by('-id')
        context={
            'in_out':today_in_out
        }
    if request.method=='POST':
        pass
    return render(request,'hostels/in_out_page.html',context)

@login_check
def delete_in_out_view(request,id):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    in_out_row = In_out.objects.get(user=user,id=id)
    in_out_row.delete()
    return in_out_view(request,date=in_out_row.date.strftime("%d-%B-%Y"))

@login_check
def all_visitors_view(request,date=None):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    if not date:
        todays_date=datetime.now().date()
        tommarrow=todays_date+timedelta(days=1)
        todays_visitors=visitors.objects.filter(user=user,in_time__range=(todays_date,tommarrow)).values().order_by('-id')
        context={'visitors':todays_visitors}
    else:
        parsed_date=datetime.strptime(date,"%d-%B-%Y")
        tommarrow=parsed_date+timedelta(days=1)
        date_visitors=visitors.objects.filter(user=user,in_time__range=(parsed_date,tommarrow)).values().order_by('-id')
        context={'visitors':date_visitors}
    return render(request,'hostels/visitors.html',context)
@login_check
def visitor_out_time_view(request,id):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    visitor=visitors.objects.get(user=user,id=id)
    visitor.out_time=datetime.now()
    visitor.save()
    return all_visitors_view(request)
@login_check
def all_revenue_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    from collections import defaultdict
    revenue_by_hostel = defaultdict(int)
    beds = Beds.objects.filter(user=user)
    for bed in beds:
        if bed.payment:
            try:
                payment = int(bed.payment)  # Use float(bed.payment) if needed
                revenue_by_hostel[bed.block_id] += payment
            except ValueError:
                # Handle invalid payment data
                pass
    blocklist={}
    for key,value in revenue_by_hostel.items():
        block=Blocks.objects.get(id=key)
        blocklist[block.block_name]=value
    context = {'blocks':blocklist}
    return render(request,'hostels/all_revenue.html',context)


# ajax requests

@login_check 
@csrf_exempt
def ajax_request_add_block_details_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    errors=[]
    block_name=request.POST.get('block_name','').strip().title()
    total_rooms=request.POST.get('total_rooms','')
    room_strength=request.POST.get('room_strength','')

    if block_name and not re.match('^[a-zA-Z][a-zA-Z0-9-]{2,11}$',block_name):
        errors.append('block_name1')
    elif not block_name:
        errors.append('block_name1')
    elif Blocks.objects.filter(user=user,block_name=block_name):
        errors.append('block_name2')
    if re.match('^[0-9]{1,3}$',total_rooms) and not 0<int(total_rooms)<1000:
        errors.append('total_rooms')
    elif not total_rooms:
        errors.append('total_rooms')
    if re.match('^[0-9]{1,2}$',room_strength) and not 0<int(room_strength)<12:
        errors.append('room_strength')
    elif not room_strength:
        errors.append('room_strength')
    if errors:
        return JsonResponse({
            'error':True,
            'errors':errors,
            'add_block':False
        })
    else:
        new_block=Blocks(user=user,block_name=block_name,total_rooms=int(total_rooms),room_strength=room_strength)
        new_block.save()
        block=Blocks.objects.get(user=user,block_name=block_name)
        # creating beds rows
        for room in range(1,int(total_rooms)+1):
            for bed in range(1,int(room_strength)+1):
                new_bed=Beds(user=user,block_id=block.id,room_no=room,bed_no=bed)
                new_bed.save()
        return JsonResponse({
            'error':False,
            'add_block':True
        })

@login_check
@csrf_exempt
def ajax_request_add_person_to_bed_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    errors=[]
    person_name=request.POST.get('person_name','').strip().title()
    age=request.POST.get('age','')
    payment=request.POST.get('payment','')
    bed_id=request.POST.get('bed_id','')
    if not person_name or not re.match('^[a-zA-Z][a-zA-Z0-9 ]{2,15}$',person_name):
        errors.append('person_name1')
    elif Beds.objects.filter(user=user,person_name=person_name):
        errors.append('person_name2')
    if not re.match('^[0-9]{1,3}$',age) or not 4<int(age)<101:
        errors.append('age')
    if not payment or not re.match('^[0-9.]{1,10}$',payment):
        errors.append('payment_given')
    if errors:
        return JsonResponse({
            'error':True,
            'errors':errors,
            'add_person':False
        })
    else:
        bed=Beds.objects.get(id=bed_id)
        bed.person_name=person_name
        bed.person_age=age
        bed.payment=payment
        bed.bed_status='booked'
        bed.added_date=datetime.now().date()
        bed.save()
        return JsonResponse({
            'error':False,
            'errors':errors,
            'add_person':True
        })
@login_check
@csrf_exempt  
def ajax_request_update_person_to_bed_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    errors=[]
    person_name=request.POST.get('person_name','').strip().title()
    age=request.POST.get('age','')
    payment=request.POST.get('payment','')
    bed_id=request.POST.get('bed_id','')

    bed=Beds.objects.get(id=bed_id)

    if not person_name or not re.match('^[a-zA-Z][a-zA-Z0-9 ]{2,15}$',person_name):
        errors.append('person_name1')
    elif Beds.objects.filter(user=user,person_name=person_name) and bed.person_name !=person_name :
        errors.append('person_name2')
    if not re.match('^[0-9]{1,3}$',age) or not 4<int(age)<101:
        errors.append('age')
    if not payment or not re.match('^[0-9.]{1,10}$',payment):
        errors.append('payment_given')
    if errors:
        return JsonResponse({
            'error':True,
            'errors':errors,
            'add_person':False
        })
    else:
        bed=Beds.objects.get(id=bed_id)
        bed.person_name=person_name
        bed.person_age=age
        bed.payment=payment
        bed.save()
        return JsonResponse({
            'error':False,
            'errors':errors,
            'add_person':True
        })

@login_check
@csrf_exempt
def ajax_request_deallocate_person_from_bed_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    person_name=request.POST.get('person_name','').strip().title()
    bed_id=request.POST.get('bed_id','')
    try:
        bed=Beds.objects.get(id=bed_id,person_name=person_name)
        leaved=Leaved_person(user=user,bed=bed,person_name=person_name,person_age=bed.person_age,added_date=bed.added_date)
        leaved.save()
        bed.person_name=''
        bed.person_age=''
        bed.payment=''
        bed.bed_status='available'
        bed.save()
        return JsonResponse({
            'error':False,
            'deallocate_person':True
        })
    except Beds.DoesNotExist as e:
        return JsonResponse({
            'error':True,
            'deallocate_person':False
        })

@login_check
@csrf_exempt
def ajax_request_retrive_bed_details_view(request):
    bed_id=request.POST.get('bed_id','')
    bed=Beds.objects.get(id=bed_id)
    return JsonResponse({
        'detail_retrieve':True,
        'person_name':bed.person_name,
        'age':bed.person_age,
        'payment_given':bed.payment,
        'added_date':bed.added_date,
    })

@login_check
@csrf_exempt
def ajax_request_update_block_name_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    new_block_name=request.POST.get('block_name','')
    block_id=request.POST.get('block_id','')
    user_id=request.POST.get('user_id','')
    if not user.id==int(user_id):
        return JsonResponse({
            'error':True,
            'error_txt':'Please Login with valid user.',
            'update':False
        })
    if not new_block_name or not re.match('^[a-zA-Z][a-zA-Z0-9-]{2,11}$',new_block_name.strip()):
      return JsonResponse({
            'error':True,
            'error_txt':'Block Name can be letters and digit,-. Must start with letter and max 12 digit allowed.',
            'update':False
        })
    elif Blocks.objects.filter(user=user,block_name=new_block_name):
        return JsonResponse({
            'error':True,
            'error_txt':'Block Name already Exists.',
            'update':False
        })
    try:
        block=Blocks.objects.get(id=block_id,user=user)
        if block.block_name==new_block_name.strip():
            return JsonResponse({
                'error':False,
                'update':False
                })
        block.block_name=new_block_name.strip()
        block.save()
        return JsonResponse({
                'error':False,
                'update':True
                })
    except Blocks.DoesNotExist as e:
        return JsonResponse({
            'error':True,
            'error_txt':'Block does not exists.',
            'update':False
        }) 
@login_check
@csrf_exempt
def ajax_request_add_bed_to_room_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    bed_id=request.POST.get('bed_id','')
    try:
        bed=Beds.objects.get(id=bed_id,user=user)
        bed_exist=Beds.objects.filter(user=user,block_id=bed.block_id,room_no=bed.room_no,bed_no=bed.bed_no+1).exists()
        if bed_exist:
            return JsonResponse({'bed_added':True})
        new_bed=Beds(user=user,block_id=bed.block_id,room_no=bed.room_no,bed_no=bed.bed_no+1)
        new_bed.save()
    except Exception as e:
        return JsonResponse({'bed_added':False})
    else:
        return JsonResponse({'bed_added':True})
    
@login_check
@csrf_exempt
def ajax_request_remove_bed_from_room_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    bed_id=request.POST.get('bed_id','')
    try:
        bed=Beds.objects.get(id=bed_id,user=user)
        bed.delete()
    except Exception as e:
        return JsonResponse({'bed_remove':False})
    else:
        return JsonResponse({'bed_removed':True})
    
@login_check
@csrf_exempt
def ajax_request_retrieve_person_details_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    person_name=request.POST.get('person_name','')
    try:
        if person_name:
            bed=Beds.objects.get(user=user,person_name=person_name.title())
        else:
            return JsonResponse({
            "error":"",
            'details':False
        })
        block=Blocks.objects.get(user=user,id=bed.block_id)
        return JsonResponse({
            'details':True,
            'block_name':block.block_name,
            'room_no':bed.room_no,
            'bed_no':bed.bed_no,
            'age':bed.person_age,
            'bed_id':bed.id
        })
    except Beds.DoesNotExist as e:
        error=f'person {person_name} does not found.'
        return JsonResponse({
            "error":error,
            'details':False
        })
@login_check
@csrf_exempt   
def ajax_request_add_in_entry_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    person_name=request.POST.get('person_name','')
    bed_id=request.POST.get('bed_id','')
    date=request.POST.get('date','')
    time=request.POST.get('time','')
    date_obj=datetime.strptime(date,"%Y-%m-%d").date()
    time_obj=datetime.strptime(time,"%H:%M:%S").time()
    try:
        try:
            entries=In_out.objects.filter(user=user,person_name=person_name).values().order_by('-id')
            if entries:
                last_entry=entries[0]
                if last_entry['in_out_status']=="IN":
                    return JsonResponse({
                        'error':f"Person Already IN on {last_entry['date']}, at {last_entry['time']}"
                    })
        except Exception as e:
            print(e)
        new_in_entry=In_out(user=user,person_name=person_name,bed_id=bed_id,date=date_obj,time=time_obj,in_out_status="IN")
        new_in_entry.save()
        return JsonResponse({'in_entry':True,'error':False})
    except Exception as e:
        return JsonResponse({'in_entry':False,'error':e})

@login_check
@csrf_exempt   
def ajax_request_add_out_entry_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username) if username else None
    person_name=request.POST.get('person_name','')
    bed_id=request.POST.get('bed_id','')
    date=request.POST.get('date','')
    time=request.POST.get('time','')
    date_obj=datetime.strptime(date,"%Y-%m-%d").date()
    time_obj=datetime.strptime(time,"%H:%M:%S").time()
    try:
        try:
            entries=In_out.objects.filter(user=user,person_name=person_name).values().order_by('-id')
            if entries:
                last_entry=entries[0]
               
                if last_entry['in_out_status']=="OUT":
                    return JsonResponse({
                        'error':f"Person Already OUT on {last_entry['date']}, at {last_entry['time']}"
                    })
        except Exception as e:
            print(e)
        new_in_entry=In_out(user=user,person_name=person_name,bed_id=bed_id,date=date_obj,time=time_obj,in_out_status="OUT")
        new_in_entry.save()
        return JsonResponse({'out_entry':True,'error':False})
    except Exception as e:
        return JsonResponse({'out_entry':False,'error':e})
    
@login_check
@csrf_exempt
def ajax_request_add_visitor_view(request):
    username=request.session.get('ActiveUserUsername','')
    user=Members.objects.get(username=username)
    error=[]
    visitor_name=request.POST['visitor_name'].strip()
    whome_to_meet=request.POST['whome_to_meet'].strip()
    if not visitor_name or not re.match('^[a-zA-Z][a-zA-Z0-9 ]{2,15}$',visitor_name):
        error.append('visitor_name')
    if not whome_to_meet or not re.match('^[a-zA-Z][a-zA-Z0-9 ]{2,15}$',whome_to_meet):
        error.append('whome_to_meet')
    if error:
        return JsonResponse({
        'error':error,
        'added':False
    })
    else:
        new_visitor=visitors(user=user,visitor_name=visitor_name,whome_to_meet=whome_to_meet,in_time=datetime.now())
        new_visitor.save()
        return JsonResponse({
            'error':error,
            'added':True
        })