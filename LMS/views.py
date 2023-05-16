from email import message
from locale import currency
from unicodedata import category
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from app.models import UserCourse
from app.models import Categories, Course, Level, UserCourse, Payment, Video
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from time import time
from .settings import *
from django.conf import settings
import math
import random
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.EmailBackEnd import EmailBackEnd

from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime











def BASE(request):
    return render(request, 'base.html')

def HOME(request):
    category = Categories.objects.all().order_by('id')[0:6]
    course = Course.objects.filter(status = 'PUBLISH').order_by('-id')
    current_year=datetime.now().year
    
    context = {
        'category': category,
        'course': course,
        'current_year': current_year,
    }
    return render(request, 'Main/home.html', context)

def DO_LOGIN(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        
        user = EmailBackEnd.authenticate(request, username=email, password=password)
        
        if user!=None:
            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or Password is Invalid!')
            return redirect('login')


def SINGLE_COURSE(request):
    category = Categories.get_all_category(Categories)
    if request.method == 'GET':
        category = Categories.get_all_category(Categories)
        level = Level.objects.all()
        course = Course.objects.all()
        FreeCourse_count =Course.objects.filter(price=0).count()
        PaidCourse_count = Course.objects.filter(price__gte=1).count()
        context = {
            'category': category,
            'level':level,
            'course': course,
            'FreeCourse_count':FreeCourse_count,
            'PaidCourse_count': PaidCourse_count,
        }
        
    return render(request, 'Main/single_course.html', context)


@login_required
def filter_data(request):
    category = request.GET.getlist('category[]')
    level = request.GET.getlist('level[]')
    price = request.GET.getlist('price[]')
    
    if price ==['PriceFree']:
        course = Course.objects.filter(price=0)
        
    elif price == ['PricePaid']:
        course = Course.objects.filter(price__gte=1)
        
    elif price == ['PriceAll']:
        course = Course.objects.all()
      
    elif category:
        course = Course.objects.filter(category__id__in = category).order_by('-id')
        
    elif level: Course.objects.filter(level__id__in = level).order_by('-id')
    else:
        course = Course.objects.all().order_by('-id')
    
    context = {
        'course' : course
    }
    t = render_to_string('ajax/course.html', context)
    return JsonResponse({'data': t})
    

def CONTACT_US(request):
    return render(request, 'Main/contact_us.html')

def ABOUT_US(request):
    return render(request, 'Main/about_us.html')


@login_required
def SEARCH_COURSE(request):
    query = request.GET['query']
    course = Course.objects.filter(title__icontains=query)
    context ={
        'course':course,
    }
    return render(request, 'search/search.html', context)

def COURSE_DETAILS(request, slug):
    
   
    course_id = Course.objects.get(slug=slug)
   
    
    course = Course.objects.filter(slug = slug)
    check_enroll = None
    if request.user.is_authenticated:
        try: 
                check_enroll = UserCourse.objects.get(user=request.user, course = course_id )
        except UserCourse.DoesNotExist:
                pass
            
            
            
    if course.exists():
        course = course.first()
    else:
        return render('404')
    
    context = {
        'course': course,
        'category': category,
        
        'check_enroll': check_enroll,
    }
    return render(request, 'course/course_details.html', context)

def PAGE_NOT_FOUND(request):
    return render(request, 'error/404.html')




def CHECKOUT(request, slug):
    # auth_token= 'SK_FLU'
    # hed = {'Authorization': 'Bearer ' + auth_token}
    course = Course.objects.get(slug=slug)
    # action =request.GET.get('action')
    # order =None
    
    if course.price == 0:
      
       course=UserCourse(
           user= request.user,
           course= course,
           
       )
       
       course.save()
       messages.success(request, 'Course successfully enrolled!')
       
    return redirect('home')
  
    
   
    
#     elif action == 'create_payment':
#         if request.method =="POST":
#             first_name = request.POST.get('first_name')
#             last_name = request.POST.get('last_name')
#             country = request.POST.get('country')
#             address_1 = request.POST.get('address_1')
#             city= request.POST.get('city')
#             phone= request.POST.get('phone')
#             email = request.POST.get('email')
#             order_comments = request.POST.get('order_comment')
          
            
            
#             price = int(price)
#             discount = int(discount)

#             amount_cal = course.price-(course.price*course.discount/100)
#             amount = amount_cal * 100
            
#             currency = "USD"
#             notes ={
#                 "name":f'{first_name} {last_name}',
#                 "country": country,
#                 "address": address_1,
#                 "city": city,
#                 "phone":phone,
#                 "email":email,
#                 "order_comments":order_comments,
                
#             }  
#             payment = Payment(
#                 course = course,
#                 user = request.user,
#                 order_id = order.get('id')
                
                
#             )
#             payment.save()
           
            
#     context={
#        'course': course,
#        'order':order,
#    }
    #return render(request, 'checkout/checkout.html', context)






def MY_COURSE(request):
    if request.user.is_authenticated:
        course = UserCourse.objects.filter(user=request.user)
        
        context = {
            'course':course,
        }
        return render(request, 'course/my-course.html', context)
    else:
        return render(request, 'registration/register.html' )

@csrf_exempt
def VERIFY_PAYMENT(request, pk):
    if request.method == 'POST':
        data=request.POST
        payment = get_object_or_404(payment, id=pk )
        status = payment.VERIFY_PAYMENT()
        if status:
            payment =Payment.objects.get(payment, id=pk)
            payment.status = True
            usercourse= UserCourse(
                user=payment.user,
                course =payment.course,
            )
            usercourse.save()
            payment.user_course = usercourse
            payment.save()
            
            context ={
                'payment':payment,
            }
            messages.success(request, "Payment Successfull")
            return render(request, 'verify_payment/success.html', context)
            
        else:
            messages.error(request, "Verification Failed")
            return redirect (request, 'verify_payment/fail.html')
        
def WATCH_COURSE(request, slug):
    course = Course.objects.filter(slug=slug)
    lecture = request.GET.get('lecture')
    video = Video.objects.filter(id=lecture)
    if course.exists():
        course=course.first()
    else:
        return redirect('404')
    
    
    context= {
        'course':course,
        'video':video,
        
    }
    
        
    return render(request, 'course/watch-course.html', context)        
        