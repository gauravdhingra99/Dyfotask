from django.shortcuts import render,redirect
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.renderers import TemplateHTMLRenderer
import pyrebase

config = {
    "apiKey": "---------------------------------------",
    "authDomain": "dyfolabs-task.firebaseapp.com",
    "databaseURL": "https://dyfolabs-task.firebaseio.com",
    "projectId": "dyfolabs-task",
    "storageBucket": "dyfolabs-task.appspot.com",
    "messagingSenderId": "860497692481"
  };


firebase=pyrebase.initialize_app(config);

auth= firebase.auth()
database = firebase.database()

def home(request):
	return render(request,'Dyfotask/index.html')



def LoginUserView(request):
	print(request.method)
	if request.method=='POST':
		email=request.POST.get('email')
		password=request.POST.get('password')
		print(request.POST)
		try:
			user = auth.sign_in_with_email_and_password(email, password)
			print(auth.current_user)
			print(user['localId'])	
		except:
			return render(request,'Dyfotask/signin.html',{"message": "Invalid Credentials","flag":False})

		#print(user)
		# if user is not None:
		# 	session_id=user['localId']
		# 	request.session['uid']=str(session_id)
		return render(request,'Dyfotask/index.html',{"message":"Success","flag":True})
	return render(request,'Dyfotask/signin.html')



def SignupUserView(request):
	print(request.method +'-----------------------------')
	# if request.method=='GET':
		
	if request.method == 'POST':
		name=request.POST.get('name')
		email=request.POST.get('email')
		password=request.POST.get('password')
		password2=request.POST.get('password2')
		print(name)
		print(email)
		print(password)
		print(password2)
		if name and email and password and password2:
			if password2!=password:
				return render(request,'Dyfotask/signup.html',{"message":"passwords not matched","flag":False})
			elif password==password2:
				try:
					user=auth.create_user_with_email_and_password(email,password)
				except Exception as e:
					print(type(e))
					return render(request,'Dyfotask/signup.html',{"message":e,"flag":False})

				uid=user['localId']
				data={"name":name,"status":"1","email":email}
				database.child("users").child(uid).set(data)
				return 	redirect('/signin/')
				return render(request,'Dyfotask/signup.html',{"message":"created","flag":True})
		else:
			return render(request,'Dyfotask/signup.html',{'message':'Credentials Required'})
	return render(request,'Dyfotask/signup.html')


def Creategroup(request):
	if request.method=='POST':
		room_name=request.POST.get('room_name')
		print(room_name)
		if room_name:
			roomList=[]
			emailList=[]
			nameList=[]
			uidList=[]
			user=auth.current_user
			print("sdfghjkl"+str(user))
			print(user)
			try:
				user = auth.refresh(user['refreshToken'])
			except:
				return 	redirect('/signin/',{"message":"Signin again Session expired"})
			print(user)
			print(user['userId'])
			uid=user['userId']
			data={"roomname":room_name,"no_of_users":1}
			data_users={uid:True}
			data1={room_name:True}
			database.child("room").child(room_name).set(data)
			database.child("room").child(room_name).child("members").push(data_users)

			database.child("users").child(uid).child("rooms").push(data1)
			rooms=database.child("users").child(uid).child("rooms").get().val()
			for key,val in rooms.items():
				for k,v in val.items():
					roomList.append(k)
			print(roomList)
			roomList = list(set(roomList))
			rooms=database.child("room").child(room_name).child("members").get().val()
			# print(rooms)
			for key,val in rooms.items():
				for k,v in val.items():
					uidList.append(k)

			for uids in uidList:
				users=database.child("users").child(uids).get().val()
				emailList.append(users['email'])
				nameList.append(users['name'])

			return render(request,'Dyfotask/index.html',{"message":"created","flag":True,"rooms":roomList ,"currentroom":room_name , "nameList":nameList ,"emailList":emailList })			
		else:
			return render(request,'Dyfotask/index.html',{"message":"Groupname is required","flag":False})
	return render(request,'Dyfotask/index.html')

def Addusertogroup(request):
	if request.method=='POST':
		room_name=request.POST.get('room_name')
		email_id=request.POST.get('email')
		if room_name and email_id:
			uid=''
			users=database.child('users').get().val()
			# print(users)
			for keys,val in users.items():
				# print(keys,val)
				if val['email']== email_id:
					uid=keys
					name=val['name']

			if uid=='':
				return render(request,'Dyfotask/index.html',{'message':'user does not exists',"flag":False})


			rooms=database.child('room').child(room_name).get().val()
			roomname=''
			print(rooms)
			if rooms['roomname']== room_name:
				roomname=room_name
				n=int(rooms['no_of_users'])
				n=n+1

			if roomname=='':
				return render(request,'Dyfotask/index.html',{'message':'Room does not exists',"flag":False})

			data_users={uid:True}
			data_rooms={room_name:True}
			# usersRef = database.ref("room");
			database.child("room").child(room_name).child("members").push(data_users)
			database.child("room").child(room_name).update({'no_of_users':n})
			database.child("users").child(uid).child("rooms").push(data_rooms)	

			roomList=[]
			emailList=[]
			nameList=[]
			uidList=[]
			# rooms=database.child("users").child(uid).child("rooms").get().val()
			# for key,val in rooms.items():
			# 	for k,v in val.items():
			# 		roomList.append(k)
			# print(roomList)
			# roomList = list(set(roomList))
			rooms=database.child("room").child(room_name).child("members").get().val()
			# print(rooms)
			for key,val in rooms.items():
				for k,v in val.items():
					uidList.append(k)

			for uids in uidList:
				users=database.child("users").child(uids).get().val()
				emailList.append(users['email'])
				nameList.append(users['name'])
				emailList = list(set(emailList))



			return render(request,'Dyfotask/index.html',{"message":"User added","flag":True,"rooms":roomList ,"currentroom":room_name , "nameList":nameList ,"emailList":emailList })			
		else:
			return render(request,'Dyfotask/index.html',{"message":"room_name and email_id is required","flag":False})
	return render(request,'Dyfotask/index.html')


def Users_in_room(request):

	# renderer_classes = [TemplateHTMLRenderer]
	# template_name = 'Dyfotask/index.html'	

	if request.method=='POST':
		room_name=request.POST.get('room_name')
		if room_name:
			uidList=[]
			nameList=[]
			emailList=[]
			rooms=database.child("room").child(room_name).child("members").get().val()
			# print(rooms)
			if rooms == None:
				return render(request,'Dyfotask/index.html',{'message':'room by this name doesnt exists'})

				pass
			for key,val in rooms.items():
				for k,v in val.items():
					uidList.append(k)

			for uid in uidList:
				users=database.child("users").child(uid).get().val()
				emailList.append(users['email'])
				nameList.append(users['name'])


			return render(request,'Dyfotask/index.html',{"nameList":nameList,"emailList":emailList})
		else:
			return render(request,'Dyfotask/index.html',{'message':'room_name required'})
	return render(request,'Dyfotask/index.html')

def Allrooms(request):

	if request.method=='GET':
		roomList=[]
		user=auth.current_user
		print("sdfghjkl"+str(user))
		try:
			user = auth.refresh(user['refreshToken'])
		except:
			return 	redirect('/signin/',{"message":"Signin again Session expired"})
		print(user)
		print(user['userId'])
		uid=user['userId']
		rooms=database.child("users").child(uid).child("rooms").get().val()
		for key,val in rooms.items():
			for k,v in val.items():
				roomList.append(k)

		return render(request,'Dyfotask/index.html',{'rooms':roomList})
	return render(request,'Dyfotask/index.html')

