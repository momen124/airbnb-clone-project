from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from .models import User, Property, PropertyImage, Booking, Payment, Review
from .serializers import (
    UserSerializer, PropertySerializer, PropertyImageSerializer,
    BookingSerializer, PaymentSerializer, ReviewSerializer
)
from .permissions import IsOwnerOrReadOnly, IsHost

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'state', 'country', 'price_per_night', 'bedrooms', 'bathrooms', 'is_available']
    search_fields = ['title', 'description', 'address', 'city', 'state', 'country']
    ordering_fields = ['price_per_night', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        property = self.get_object()
        reviews = Review.objects.filter(property=property)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        properties = Property.objects.filter(host=request.user)
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property']
    ordering_fields = ['check_in', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        elif user.is_host:
            return Booking.objects.filter(property__host=user)
        return Booking.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {"detail": "This booking cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=user)
    
    def perform_create(self, serializer):
        payment = serializer.save()
        
        # In a real application, you would integrate with a payment gateway here
        # For this example, we'll just mark the payment as completed
        payment.status = 'completed'
        payment.save()
        
        # Update the booking status
        booking = payment.booking
        booking.status = 'confirmed'
        booking.save()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        property_id = self.request.query_params.get('property_id')
        if property_id:
            return Review.objects.filter(property_id=property_id)
        return Review.objects.all()
