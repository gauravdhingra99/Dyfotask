from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login

import pyrebase

config = {
    "apiKey": "AIzaSyBqsfini42H--uMKOMAfYWxtfLvEY_yk_Q",
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
		except:
			user=None
		print(user)
		if user is not None:
			session_id=user['localId']
			request.session['uid']=str(session_id)
			return Response({"message":"Success"})
		else:
			return Response({"message": "Invalid Credentials"})



class SignupUserView(APIView):
	def post(self,request):
		name=request.data.get('name')
		email=request.data.get('email')
		password=request.data.get('password')
		password2=request.data.get('password2')
		if name and email and password and password2:
			if password2!=password:
				return Response({"error":"passwords not matched"})
			elif password==password2:
				# if User.objects.filter(username=username).exists():
				# 	return Response({"error":"User already exists"})
				try:
					user=auth.create_user_with_email_and_password(email,password)
				except:
					return Response({"message":"User already Exists"})

				uid=user['localId']
				data={"name":name,"status":"1"}
				database.child("users").child(uid).child("details").set(data)
				return Response({"message":"created"})
		else:
			return Response({'message':'Credentials required'})



