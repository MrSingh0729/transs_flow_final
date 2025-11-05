from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


@login_required
def chat_index(request):
    rooms = ChatRoom.objects.filter(participants=request.user).order_by('-updated_at')

    # Add display name safely for template
    for r in rooms:
        r.display_name = r.display_name_for(request.user)

    return render(request, 'chat/index.html', {'rooms': rooms})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id)
    if not room.participants.filter(pk=request.user.pk).exists():
        return redirect("chat:index")
    messages = room.messages.select_related("sender").all()[:200]
    return render(request, "chat/room.html", {"room": room, "messages": messages})


@login_required
def create_private_chat(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    existing = ChatRoom.objects.filter(is_group=False, participants=request.user).filter(participants=other)
    if existing.exists():
        return redirect("chat:room", room_id=existing.first().id)
    room = ChatRoom.objects.create(is_group=False)
    room.participants.add(request.user, other)
    return redirect("chat:room", room_id=room.id)


@login_required
def create_group_chat(request):
    if request.method == "POST":
        name = request.POST.get("name")
        participants = request.POST.getlist("participants")
        room = ChatRoom.objects.create(name=name, is_group=True)
        room.participants.add(request.user)
        for pid in participants:
            u = User.objects.filter(pk=pid).first()
            if u:
                room.participants.add(u)
        return redirect("chat:room", room_id=room.id)
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, "chat/create_group.html", {"users": users})
