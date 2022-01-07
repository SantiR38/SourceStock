from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import UserSerializer


class UserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(UserSerializer.errors, status = status.HTTP_400_BAD_REQUEST)
