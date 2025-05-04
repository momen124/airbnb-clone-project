from rest_framework import serializers
from .models import User, Property, PropertyImage, Booking, Payment, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'bio', 'is_host', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'is_primary']

class PropertySerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'host', 'title', 'description', 'address', 'city', 
                  'state', 'country', 'zip_code', 'price_per_night', 
                  'max_guests', 'bedrooms', 'bathrooms', 'is_available', 
                  'property_type', 'amenities', 'images', 'average_rating',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return None

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), 
        write_only=True,
        source='property'
    )
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'property', 'property_id', 'check_in', 'check_out', 
                  'guests', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['total_price', 'status', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Check that the booking dates are valid and the property is available
        """
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("Check-out must be after check-in")
        
        # Check if property is available for these dates
        property_obj = data['property']
        if not property_obj.is_available:
            raise serializers.ValidationError("This property is not available")
        
        # Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            property=property_obj,
            status__in=['pending', 'confirmed'],
            check_in__lt=data['check_out'],
            check_out__gt=data['check_in']
        )
        
        if conflicting_bookings.exists():
            raise serializers.ValidationError("Property is already booked for these dates")
        
        return data
    
    def create(self, validated_data):
        # Calculate total price
        property_obj = validated_data['property']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        nights = (check_out - check_in).days
        total_price = property_obj.price_per_night * nights
        
        validated_data['total_price'] = total_price
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), 
        write_only=True,
        source='booking'
    )
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'booking_id', 'amount', 'payment_method', 
                  'transaction_id', 'status', 'transaction_date']
        read_only_fields = ['status', 'transaction_date']
    
    def validate(self, data):
        booking = data['booking']
        if booking.status != 'pending':
            raise serializers.ValidationError("Payment can only be made for pending bookings")
        
        if data['amount'] != booking.total_price:
            raise serializers.ValidationError("Payment amount must match booking total price")
        
        return data

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), 
        write_only=True,
        source='booking'
    )
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'property', 'booking_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        booking = data['booking']
        
        # Check if the booking belongs to the user
        if booking.user != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own bookings")
        
        # Check if the booking is completed
        if booking.status != 'completed':
            raise serializers.ValidationError("You can only review completed bookings")
        
        # Check if a review already exists for this booking
        if Review.objects.filter(booking=booking).exists():
            raise serializers.ValidationError("You have already reviewed this booking")
        
        # Set the property based on the booking
        data['property'] = booking.property
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['property'] = validated_data['booking'].property
        return super().create(validated_data)
