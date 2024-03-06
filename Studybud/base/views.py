from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room,Topic,Message
from .forms import RoomForm,UserForm


# Create your views here.

# rooms=[
#     {'id':1, 'name':'Let us learn python'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developers21'},
# ]


def loginPage(request):
    page='login'#page value
    #if the user is already logged in no need to login again
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user=authenticate(request,username=username,password=password)

  
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username OR Password does not exist')

    context={'page':page}
    return render(request,'base/login_register.html',context)



def logoutUser(request):
    logout(request)#delete that token which means deleting user
    return redirect('home')

def registerPage(request):
    #page='register'#specifying the page
    form=UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)#creates a new User object but does not save it to the database yet.
            user.username=user.username.lower()
            user.save()#saves the User object to the database

            login(request,user)#The user just registered have to login
            return redirect('home')
        else:
            messages.error(request,'An error occurred during registration')

    return render(request,'base/login_register.html',{'form':form})

def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(

        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        
        )#gives all the room in the database
    
    topics=Topic.objects.all()[0:10]#only display 0-5 topics
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))#if we click on one topic we have see only activity related to that topic only
    
    context={'rooms':rooms,'topics':topics,
            'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)



# def room(request,pk):
#     room=Room.objects.get(id=pk)
#     #get all children of this room
#     room_messages=room.message_set.all()#New message comes first
#     participants=room.participants.all()

#     if request.method == 'POST':
#         message=Message.objects.create(
#             user=request.user,
#             room=room,
#             body=request.POST.get('body')
#         )
#         room.participants.add(request.user)#As soon as the user send message they are added to participants and their user is visble


#         return redirect('room',pk=room.id)#redirects the user to the room view

#     context={'room': room, 'room_messages':room_messages,
#             'participants':participants
#     }
#     return render(request,'base/room.html',context)



def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)

        print(message.user.id)  # Print the value of message.user.id

        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    }
    return render(request, 'base/room.html', context)





















def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,
             'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)


#only authenticate user can create the room if not the user redirect to the login page
@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':#if request is post add the data to the form, if valid save form and redirect the user to the home page
        #if topic already exist it doesn't create
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create (name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home') #sending the user to the home page

    context={'form':form,'topics':topics}
    return render(request, 'base/room_form.html',context)


#only authenticated user can update the room
@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    #if the user is not the owner of the room they are not allowed to update the room
    if request.user!=room.host:
        return HttpResponse('you are not allowed here')

    if request.method=='POST':
        #if topic already exist it doesn't create
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create (name=topic_name)
        room.name=request.POST.get('name')
        room.topic=topic
        room.description=request.POST.get('description')
        room.save()
        return redirect('home')   

    context={'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)



#only authenticated user can delete the room
@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)

        #if the user is not the owner of the room and not superuser they are not allowed to delete the room
    if request.user != room.host and not request.user.is_superuser:
        return HttpResponse('You are not allowed here')

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})



@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)

    #check if the user is the message owner
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete')

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})



@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    return render(request,'base/update-user.html',{'form':form})


def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topic':topics})


def activityPage(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})

