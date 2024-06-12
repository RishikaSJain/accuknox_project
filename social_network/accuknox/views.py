from rest_framework import generics, permissions, status
from .serializers import *
from django.contrib.auth import get_user_model
from .models import User, FriendRequest
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import time

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(email__iexact=query) | 
                Q(username__icontains=query) |
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query)
            )
        return queryset

class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from_user = self.request.user
        to_user = serializer.validated_data['to_user']
        
        if from_user == to_user:
            raise serializers.ValidationError("Cannot send friend request to yourself.")
        
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already sent.")
        
        # if FriendRequest.objects.filter(from_user=from_user, timestamp__gt=time.time() - 60).count() >= 3:
        #     raise serializers.ValidationError("Cannot send more than 3 friend requests in a minute.")
        
        serializer.save(from_user=from_user)


class AcceptRejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        friend_request = self.get_object()
        serializer = self.get_serializer(friend_request, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        action = serializer.validated_data.get('action')
        if action == 'accept':
            return Response({'message': 'Friend request accepted'}, status=200)
        elif action == 'reject':
            return Response({'message': 'Friend request rejected'}, status=200)

    def perform_update(self, serializer):
        instance = serializer.save()
        action = serializer.validated_data.get('action')
        if action == 'accept':
            instance.accepted = True
            instance.save()
        elif action == 'reject':
            if instance.id is not None: 
                instance.delete()  
    
class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friends = User.objects.filter(
            Q(sent_requests__to_user=user, sent_requests__accepted=True) | 
            Q(received_requests__from_user=user, received_requests__accepted=True)
        )
        return friends

class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)
