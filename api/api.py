from rest_framework.response import Response
from .serializer import UserSerializer, ClientSerializer
from rest_framework.views import APIView
from rest_framework import status, viewsets, permissions, renderers
from rest_framework.decorators import action
from erp.models import Cliente
from api.permissions import IsOwnerOrReadOnly

class UserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(UserSerializer.errors, status = status.HTTP_400_BAD_REQUEST)

class ClientViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClientSerializer