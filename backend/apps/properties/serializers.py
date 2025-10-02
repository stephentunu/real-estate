from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, PropertyType, PropertyStatus, PropertyImage, PropertyFeature, SavedProperty, Amenity, PropertyAmenity

User = get_user_model()


class PropertyTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for PropertyType model
    Handles property type data serialization
    """
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for PropertyStatus model
    Handles property status data serialization
    """
    class Meta:
        model = PropertyStatus
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyImageSerializer(serializers.ModelSerializer):
    """
    Serializer for PropertyImage model
    Handles property image data serialization
    """
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class PropertyFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for PropertyFeature model
    Handles property feature data serialization
    """
    class Meta:
        model = PropertyFeature
        fields = ['id', 'name', 'description', 'icon', 'is_active']
        read_only_fields = ['id']


class AmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for Amenity model
    Handles property amenity data serialization
    """
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'description', 'icon', 'category', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for PropertyAmenity model
    Handles property-amenity relationship data serialization
    """
    amenity_name = serializers.CharField(source='amenity.name', read_only=True)
    amenity_icon = serializers.CharField(source='amenity.icon', read_only=True)
    amenity_category = serializers.CharField(source='amenity.category', read_only=True)
    
    class Meta:
        model = PropertyAmenity
        fields = ['id', 'amenity', 'amenity_name', 'amenity_icon', 'amenity_category', 'created_at']
        read_only_fields = ['id', 'created_at']


class SavedPropertySerializer(serializers.ModelSerializer):
    """
    Serializer for SavedProperty model
    Handles user saved properties
    """
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_price = serializers.SerializerMethodField()
    property_image = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedProperty
        fields = [
            'id', 'property', 'property_title', 'property_price',
            'property_image', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_property_price(self, obj):
        """
        Get property price display
        """
        return obj.property.get_price_display()
    
    def get_property_image(self, obj):
        """
        Get primary image URL for the saved property
        """
        primary_image = obj.property.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None


class PropertyListSerializer(serializers.ModelSerializer):
    """
    Serializer for Property model in list view
    Optimized for listing properties with minimal data
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'property_type_name', 'status', 'status_name',
            'listing_type', 'sale_price', 'rent_price', 'currency', 'price_display',
            'square_feet', 'bedrooms', 'bathrooms', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'latitude', 'longitude',
            'owner', 'owner_name', 'primary_image', 'is_published', 'is_featured',
            'is_saved', 'views_count', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'views_count', 'created_at']
    
    def get_primary_image(self, obj):
        """
        Get the primary image URL for the property
        """
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None
    
    def get_price_display(self, obj):
        """
        Get formatted price display
        """
        return obj.get_price_display()
    
    def get_is_saved(self, obj):
        """
        Check if the property is saved by the current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedProperty.objects.filter(
                user=request.user,
                property=obj
            ).exists()
        return False


class PropertyDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Property model detail view
    Includes all property information with related data
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    features = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'property_type_name',
            'status', 'status_name', 'listing_type', 'owner', 'owner_name', 'owner_email',
            'agent', 'agent_name', 'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'latitude', 'longitude', 'full_address',
            'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built',
            'sale_price', 'rent_price', 'currency', 'price_display',
            'parking_spaces', 'has_garage', 'has_pool', 'has_garden', 'is_furnished',
            'is_featured', 'is_published', 'views_count', 'images', 'features',
            'is_saved', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'owner', 'views_count', 'is_saved', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_features(self, obj):
        """
        Get property features through the assignment relationship
        """
        assignments = obj.feature_assignments.select_related('feature').all()
        return [{
            'id': assignment.feature.id,
            'name': assignment.feature.name,
            'description': assignment.feature.description,
            'icon': assignment.feature.icon,
            'value': assignment.value
        } for assignment in assignments]
    
    def get_price_display(self, obj):
        """
        Get formatted price display
        """
        return obj.get_price_display()
    
    def get_full_address(self, obj):
        """
        Get full formatted address
        """
        return obj.get_full_address()
    
    def get_is_saved(self, obj):
        """
        Check if property is saved by current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedProperty.objects.filter(user=request.user, property=obj).exists()
        return False


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Property model creation and updates
    Handles property creation and update operations
    """
    features = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of features with optional values"
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'status', 'listing_type',
            'agent', 'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'latitude', 'longitude',
            'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built',
            'sale_price', 'rent_price', 'currency',
            'parking_spaces', 'has_garage', 'has_pool', 'has_garden', 'is_furnished',
            'features', 'is_featured', 'is_published'
        ]
    
    def create(self, validated_data):
        """
        Create property with features
        """
        features_data = validated_data.pop('features', [])
        property_instance = Property.objects.create(**validated_data)
        
        # Add features to property through assignments
        self._create_feature_assignments(property_instance, features_data)
        
        return property_instance
    
    def update(self, instance, validated_data):
        """
        Update property with features
        """
        features_data = validated_data.pop('features', None)
        
        # Update property fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update features if provided
        if features_data is not None:
            # Remove existing assignments
            instance.feature_assignments.all().delete()
            # Create new assignments
            self._create_feature_assignments(instance, features_data)
        
        return instance
    
    def _create_feature_assignments(self, property_instance, features_data):
        """
        Create PropertyFeatureAssignment instances
        """
        from .models import PropertyFeatureAssignment
        
        for feature_data in features_data:
            feature_id = feature_data.get('feature_id')
            value = feature_data.get('value', '')
            
            if feature_id:
                try:
                    feature = PropertyFeature.objects.get(id=feature_id)
                    PropertyFeatureAssignment.objects.create(
                        property=property_instance,
                        feature=feature,
                        value=value
                    )
                except PropertyFeature.DoesNotExist:
                    continue
    
    def validate_sale_price(self, value):
        """
        Validate property sale price
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Sale price must be greater than 0")
        return value
    
    def validate_rent_price(self, value):
        """
        Validate property rent price
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Rent price must be greater than 0")
        return value
    
    def validate_square_feet(self, value):
        """
        Validate property square feet
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Square feet must be greater than 0")
        return value
    
    def validate_bedrooms(self, value):
        """
        Validate number of bedrooms
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("Bedrooms cannot be negative")
        return value
    
    def validate_bathrooms(self, value):
        """
        Validate number of bathrooms
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("Bathrooms cannot be negative")
        return value