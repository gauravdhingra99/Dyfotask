from django.shortcuts import render
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
    "apiKey": "***************************************",
    "authDomain": "dyfolabs-task.firebaseapp.com",
    "databaseURL": "https://dyfolabs-task.firebaseio.com",
    "projectId": "dyfolabs-task",
    "storageBucket": "dyfolabs-task.appspot.com",
    "messagingSenderId": "860497692481"
  };


firebase=pyrebase.initialize_app(config);

auth= firebase.auth()
database = firebase.database()


class LoginUserView(APIView):
	def post(self,request):
		print(request.data)
		email=request.data.get('email')
		password=request.data.get('password')
		try:
			user = auth.sign_in_with_email_and_password(email, password)
			print(auth.current_user)
			print(user['localId'])
		except:
			return Response({"message": "Invalid Credentials","flag":False})

		#print(user)
		# if user is not None:
		# 	session_id=user['localId']
		# 	request.session['uid']=str(session_id)
		return Response({"message":"Success","flag":True})
		


class SignupUserView(APIView):
	def post(self,request):
		name=request.data.get('name')
		email=request.data.get('email')
		password=request.data.get('password')
		password2=request.data.get('password2')
		if name and email and password and password2:
			if password2!=password:
				return Response({"error":"passwords not matched","flag":False})
			elif password==password2:
				# if User.objects.filter(username=username).exists():
				# 	return Response({"error":"User already exists"})
				try:
					user=auth.create_user_with_email_and_password(email,password)
				except:
					return Response({"message":"User already Exists","flag":False})

				uid=user['localId']
				data={"name":name,"status":"1","email":email}
				database.child("users").child(uid).set(data)
				return Response({"message":"created","flag":True})
		else:
			return Response({'message':'Credentials required',"flag":False})

class Creategroup(APIView):
	def post(self,request):
		room_name=request.data.get('room_name')
		if room_name:
			user=auth.current_user
			print("sdfghjkl"+str(user))
			print(user)
			try:
				user = auth.refresh(user['refreshToken'])
			except:
				return Response({"message":"Signin again Session expired"})
			print(user)
			print(user['userId'])
			uid=user['userId']
			data={"roomname":room_name,"no_of_users":1}
			data_users={uid:True}
			data1={room_name:True}
			database.child("room").child(room_name).set(data)
			database.child("room").child(room_name).child("members").push(data_users)

			database.child("users").child(uid).child("rooms").push(data1)
			return Response({"message":"created","flag":True})			
		else:
			return Response({"message":"Groupname and created_by is required","flag":False})


class Addusertogroup(APIView):
	def post(self,request):
		room_name=request.data.get('room_name')
		email_id=request.data.get('email')
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
				return Response({'message':'user does not exists',"flag":False})


			rooms=database.child('room').child(room_name).get().val()
			roomname=''
			print(rooms)
			if rooms['roomname']== room_name:
				roomname=room_name
				n=int(rooms['no_of_users'])
				n=n+1

			if roomname=='':
				return Response({'message':'Room does not exists',"flag":False})

			data_users={uid:True}
			data_rooms={room_name:True}
			# usersRef = database.ref("room");
			database.child("room").child(room_name).child("members").push(data_users)
			database.child("room").child(room_name).update({'no_of_users':n})
			database.child("users").child(uid).child("rooms").push(data_rooms)	

			return Response({"message":"User added","flag":True})			
		else:
			return Response({"message":"room_name and email_id is required","flag":False})


class Users_in_room(APIView):

	# renderer_classes = [TemplateHTMLRenderer]
	# template_name = 'Dyfotask/index.html'	

	def get(self,request):
		room_name=request.query_params.get('room_name')
		if room_name:
			uidList=[]
			nameList=[]
			emailList=[]
			rooms=database.child("room").child(room_name).child("members").get().val()
			# print(rooms)
			for key,val in rooms.items():
				for k,v in val.items():
					uidList.append(k)

			for uid in uidList:
				users=database.child("users").child(uid).get().val()
				emailList.append(users['email'])
				nameList.append(users['name'])


			return Response({"names":nameList,"email":emailList})
		else:
			return Response({'message':'room_name required'})

class Allrooms(APIView):

	def get(self,request):
		roomList=[]
		user=auth.current_user
		print("sdfghjkl"+str(user))
		try:
			user = auth.refresh(user['refreshToken'])
		except:
			return Response({"message":"Signin again Session expired"})
		print(user)
		print(user['userId'])
		uid=user['userId']
		rooms=database.child("users").child(uid).child("rooms").get().val()
		for key,val in rooms.items():
			for k,v in val.items():
				roomList.append(k)

		return Response({'rooms':roomList})

