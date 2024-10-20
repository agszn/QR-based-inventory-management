from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .models import *


from .forms import *
from .models import *
from django.db.models import Q

from django.http import JsonResponse
from django.conf import settings
import os

import joblib
import numpy as np

def base(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'about/about.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #create a new registration object and avoid saving it yet
            new_user = user_form.save(commit=False)
            #reset the choosen password
            new_user.set_password(user_form.cleaned_data['password'])
            #save the new registration
            new_user.save()
            return render(request, 'registration/register_done.html',{'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html',{'user_form':user_form})

def profile(request):
    return render(request, 'profile/profile.html')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        user_form = EditProfileForm(instance=request.user)
    
    return render(request, 'profile/edit_profile.html', {'user_form': user_form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account was successfully deleted.')
        return redirect('base')  # Redirect to the homepage or another page after deletion

    return render(request, 'registration/delete_account.html')
# das

@login_required
def dashboard(request):
    users_count = User.objects.all().count()
    return render(request, "dashboard/dashboard_crop.html")
#CRUD operations start here
@login_required
def dashvalues(request):
    consumers = Consumer.objects.all()
    search_query = ""
    
    if request.method == "POST": 
        if "create" in request.POST:
            name = request.POST.get("name")
            email = request.POST.get("email")
            image = request.FILES.get("image")
            content = request.POST.get("content")

            Consumer.objects.create(
                name=name,
                email=email,
                image=image,
                content=content
            )
            messages.success(request, "Consumer added successfully")
    
        elif "update" in request.POST:
            id = request.POST.get("id")
            name = request.POST.get("name")
            email = request.POST.get("email")
            image = request.FILES.get("image")
            content = request.POST.get("content")

            consumer = get_object_or_404(Consumer, id=id)
            consumer.name = name
            consumer.email = email
            consumer.image = image
            consumer.content = content
            consumer.save()
            messages.success(request, "Consumer updated successfully")
    
        elif "delete" in request.POST:
            id = request.POST.get("id")
            Consumer.objects.get(id=id).delete()
            messages.success(request, "Consumer deleted successfully")
        
        elif "search" in request.POST:
            search_query = request.POST.get("query")
            consumers = Consumer.objects.filter(Q(name__icontains=search_query) | Q(email__icontains=search_query))

    context = {
        "consumers": consumers, 
        "search_query": search_query
    }
    return render(request, "crud/dashvalue.html", context=context)
# CRUD operations end here

@login_required
def generate_notification(request):
    # Generate a random number between 31 and 40
    import random
    random_number = random.randint(30, 34)
    
    # Check if the random number is above 32
    if random_number > 32:
        # Get the current user
        current_user = request.user
        
        # Create a notification message
        message = f"Tempeature has excedded threshold level: {random_number}"
        
        # Save the notification in the Notification model
        Notification.objects.create(user=current_user, message=message)
        
        # Redirect to the user_notifications page
        return redirect('user_notifications')
    
    # Return an HttpResponse object if the condition is not met
    return HttpResponse("No notification generated.")

# Contact start
@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us!")
            return redirect('dashboard')  # Redirect to the same page to show the modal
    else:
        form = ContactForm()

    return render(request, 'contact/contact_form.html', {'form': form})

# contact end

# review start
def add_review(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    consumer_name = consumer.name

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Assuming you have a Review model with fields 'comment' and 'rating'
            review = form.save(commit=False)
            review.consumer = consumer
            review.save()
            # You may want to add a success message here
            return redirect('dashboard')  # Redirect to the dashboard or any other page
    else:
        form = ReviewForm()

    return render(request, 'review/review.html', {'consumer_id': consumer_id, 'consumer_name': consumer_name, 'form': form})
# review end

# views.py


def view_reviews(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    reviews = Review.objects.filter(consumer=consumer)

    return render(request, 'review/view_reviews.html', {'consumer': consumer, 'reviews': reviews})

#notification

@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification/user_notifications.html', {'notifications': notifications})


import smtplib
from email.message import EmailMessage
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

@login_required
def send_email(request):
    if request.method == 'POST':
        receiver = request.POST.get('receiver')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[receiver],
        )
        try:
            email.send()
            messages.success(request, 'Email sent successfully!')
        except:
            messages.error(request, 'Failed to send email.')

        return redirect('send_email')

    return render(request, 'email/sendemail.html')


@login_required
def chat(request):
    return render(request, 'chat/chat.html')


# #################################
from django.shortcuts import render
import serial
import time
from django.http import HttpResponse
from inventory.models import Item
from inventory.forms import ItemForm
import qrcode
from PIL import Image

def sensor_data(request):
    # Replace 'COM6' with your Arduino's serial port
    serial_port = 'COM4'
    baud_rate = 9600

    try:
        # Establish serial connection
        ser = serial.Serial(serial_port, baud_rate)

        # Read data from Arduino
        data = ser.readline().decode('latin-1').strip()

        # Close serial connection
        ser.close()

        # Pass the data to the template
        return render(request, 'sensrc/sensor_val.html', {'data': data})
    except serial.SerialException:
        # Handle serial port error
        return HttpResponse("Error: Serial port not available or accessible.")

# views.py
from django.shortcuts import render, redirect, get_object_or_404


def item_list(request):
    items = Item.objects.all()
    return render(request, 'sensrc/item_list.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'sensrc/item_detail.html', {'item': item})

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'sensrc/item_form.html', {'form': form})

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'sensrc/item_form.html', {'form': form})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'sensrc/item_confirm_delete.html', {'item': item})


import os
from django.conf import settings
def generate_qr_code(item):
    # Format data into a string
    data = f"Name: {item.name}\nUnits: {item.units}\nFragile: {'Yes' if item.fragile else 'No'}\nWeight: {item.weight}\nUnit Choices: {item.unit_choices}\nItem Class: {item.item_class}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Specify the file path within the models/qr folder
    file_path = f"static/qr/{item.name}_qr_code.png"
    
    # Save the QR code image
    img.save(file_path)


def generate_qr(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    generate_qr_code(item)
    return HttpResponse("QR code generated successfully!")
