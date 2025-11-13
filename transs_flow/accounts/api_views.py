# accounts/api_views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = EmployeeSerializer(request.user)
        return Response(serializer.data)
