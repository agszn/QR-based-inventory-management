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
        return render(request, 'sensor_val.html', {'data': data})
    except serial.SerialException:
        # Handle serial port error
        return HttpResponse("Error: Serial port not available or accessible.")

# views.py
from django.shortcuts import render, redirect, get_object_or_404


def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item_detail.html', {'item': item})

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'item_form.html', {'form': form})

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'form': form})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'item_confirm_delete.html', {'item': item})


# ----------------------------------------------------------------

# generate QR
import qrcode
from PIL import Image, ImageDraw
import os
import random

def generate_random_color():
    # Generate random RGB values
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    # Format RGB values into a tuple
    return (r, g, b)

def generate_qr_code(item):
    # Generate a random color for the QR code
    color = generate_random_color()
    
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

    # Convert the image to RGBA mode to support transparency
    img = img.convert("RGBA")
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Overlay the QR code with the chosen color
    width, height = img.size
    for x in range(width):
        for y in range(height):
            pixel_color = img.getpixel((x, y))
            if pixel_color == (0, 0, 0, 255):  # Black pixels in the QR code
                draw.point((x, y), fill=color)  # Overlay with the chosen color

    # Specify the file path within the static/qr folder
    file_path = f"static/qr/{item.name}_qr_code.png"
    
    # Save the QR code image
    img.save(file_path)

def generate_qr(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    
    # Generate QR code with a random color for the item
    generate_qr_code(item)
    
    return redirect('inventory:view_images')


# ----------------------------------------------------------------

#  display images on frontend
from django.shortcuts import render, redirect
import os

mode_path = r'static/qr/'

def view_images(request):
    # Get a list of all image files in the folder
    image_files = [f for f in os.listdir(mode_path) if os.path.isfile(os.path.join(mode_path, f))]
    
    # Render the HTML template with the list of image files
    return render(request, 'view_images.html', {'image_files': image_files})

def delete_image(request, image_name):
    # Get the path to the image file
    image_path = os.path.join(mode_path, image_name)
    
    # Check if the file exists
    if os.path.exists(image_path):
        # Delete the file
        os.remove(image_path)
    
    # Redirect back to the view_images view
    return redirect('inventory:view_images')

def hide_image(request, image_name):
    # Your code to hide the image
    # For example, you can move the image to a hidden folder
    source_path = os.path.join(mode_path, image_name)
    hidden_folder = os.path.join(mode_path, 'hidden')
    destination_path = os.path.join(hidden_folder, image_name)

    # Create the hidden folder if it doesn't exist
    if not os.path.exists(hidden_folder):
        os.makedirs(hidden_folder)
    
    # Move the image to the hidden folder
    os.rename(source_path, destination_path)
    
    # Redirect back to the view_images view
    return redirect('inventory:view_images')

def show_all_images(request):
    # Your code to show all images (if they were hidden)
    # For example, you can move all images from the hidden folder back to the main folder
    hidden_folder = os.path.join(mode_path, 'hidden')

    # Check if the hidden folder exists
    if os.path.exists(hidden_folder):
        for image_name in os.listdir(hidden_folder):
            source_path = os.path.join(hidden_folder, image_name)
            destination_path = os.path.join(mode_path, image_name)
            
            # Move the image back to the main folder
            os.rename(source_path, destination_path)
    
    # Redirect back to the view_images view
    return redirect('inventory:view_images')


# scan and update qr
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product

# views.py

from django.shortcuts import render
from django.http import JsonResponse

def display_qr_content(request):
    if request.method == 'POST':
        qr_content = request.POST.get('qr_content', '')
        return JsonResponse({'qr_content': qr_content})
    else:
        return render(request, 'scan_qr.html')

# ----------------------------------------------------------------
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import scannedItems  # Import your model

@csrf_exempt
def receive_checked_values(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            checked_values = data.get('checked_values', [])
            
            # Process the received values and save them to the database
            for value in checked_values:
                # Split the value into fields
                fields = value.split('\n')
                
                # Extract field values
                name = fields[0].split(': ')[1]
                units = int(fields[1].split(': ')[1])
                fragile = fields[2].split(': ')[1] == 'Yes'
                weight = float(fields[3].split(': ')[1])
                unit = fields[4].split(': ')[1]
                item_class = fields[5].split(': ')[1]
                
                # Create and save the scanned item
                scanned_item = scannedItems(
                    name=name,
                    units=units,
                    fragile=fragile,
                    weight=weight,
                    unit=unit,
                    item_class=item_class
                )
                scanned_item.save()
                
            return JsonResponse({'message': 'Values received and saved successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# ----------------------------------------------------------------
# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import scannedItems
from .forms import ScannedItemForm

def item_list(request):
    items = scannedItems.objects.all()
    return render(request, 'crud/list_items.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(scannedItems, pk=pk)
    return render(request, 'crud/item_detail.html', {'item': item})

def item_create(request):
    if request.method == 'POST':
        form = ScannedItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item-list')
    else:
        form = ScannedItemForm()
    return render(request, 'crud/item_form.html', {'form': form})

def item_update(request, pk):
    item = get_object_or_404(scannedItems, pk=pk)
    if request.method == 'POST':
        form = ScannedItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item-list')
    else:
        form = ScannedItemForm(instance=item)
    return render(request, 'crud/item_form.html', {'form': form})

def item_delete(request, pk):
    item = get_object_or_404(scannedItems, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item-list')
    return render(request, 'crud/item_delete_confirmation.html', {'item': item})

# Optionally, you can add a function for filtering scanned items
def item_filter(request):
    items = scannedItems.objects.filter(fragile=True)  # Example: filtering fragile items
    return render(request, 'crud/list_items.html', {'items': items})
# ----------------------------------------------------------------

from django.shortcuts import render
from django.utils import timezone
from .models import scannedItems
from django.db import models


def graph_view(request):
    # Example query to get counts of fragile and non-fragile items
    fragile_count = scannedItems.objects.filter(fragile=True).count()
    non_fragile_count = scannedItems.objects.filter(fragile=False).count()

    # Example query to get total weight of items
    total_weight = scannedItems.objects.aggregate(total_weight=models.Sum('weight'))['total_weight'] or 0

    context = {
        'fragile_count': fragile_count,
        'non_fragile_count': non_fragile_count,
        'total_weight': total_weight,
    }
    return render(request, 'analytics.html', context)

