from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import models
from .models import Message, UserPublicKey
import json

def landing_view(request):
    return render(request, 'chat/landing.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:user_list')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat:user_list')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('chat:login')

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

@login_required
def chat_room(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    return render(request, 'chat/chat_room.html', {'recipient': recipient})

@login_required
def save_public_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        public_key_str = data.get('public_key')
        UserPublicKey.objects.update_or_create(user=request.user, defaults={'public_key': public_key_str})
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_public_key(request, user_id):
    pk_info = get_object_or_404(UserPublicKey, user_id=user_id)
    return JsonResponse({'public_key': pk_info.public_key})

@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        encrypted_for_recipient = data.get('encrypted_for_recipient')
        encrypted_for_sender = data.get('encrypted_for_sender')
        recipient = get_object_or_404(User, id=recipient_id)
        Message.objects.create(
            sender=request.user, 
            recipient=recipient, 
            encrypted_for_recipient=encrypted_for_recipient,
            encrypted_for_sender=encrypted_for_sender
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_messages(request, other_user_id):
    messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(recipient_id=other_user_id)) |
        (models.Q(sender_id=other_user_id) & models.Q(recipient=request.user))
    ).order_by('timestamp')

    data = []
    for msg in messages:
        if msg.sender == request.user:
            content = msg.encrypted_for_sender
        else:
            content = msg.encrypted_for_recipient

        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'encrypted_content': content,
            'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            'is_edited': msg.is_edited
        })
    return JsonResponse({'messages': data})

@login_required
def edit_message(request, message_id):
    if request.method == 'POST':
        msg = get_object_or_404(Message, id=message_id, sender=request.user)
        data = json.loads(request.body)
        msg.encrypted_for_recipient = data.get('encrypted_for_recipient')
        msg.encrypted_for_sender = data.get('encrypted_for_sender')
        msg.is_edited = True
        msg.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        msg = get_object_or_404(Message, id=message_id, sender=request.user)
        msg.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_user(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'forbidden'}, status=403)
    user = get_object_or_404(User, id=user_id)
    if not user.is_superuser: # Prevent deleting superuser via this
        user.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
