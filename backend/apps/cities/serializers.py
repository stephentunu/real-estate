from rest_framework import serializers
from django.db.models import Count
from .models import Country, State, City


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for Country model
    """
    
    state_count = serializers.ReadOnlyField()
    city_count = serializers.ReadOnlyField()
    property_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'code', 'slug', 'continent',
            'currency_code', 'currency_symbol', 'phone_code',
            'flag_emoji', 'is_active', 'state_count',
            'city_count', 'property_count', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']


class CountryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for country lists
    """
    
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'code', 'slug', 'currency_symbol',
            'flag_emoji', 'is_active'
        ]


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer for State model
    """
    
    country = CountryListSerializer(read_only=True)
    country_id = serializers.IntegerField(write_only=True)
    city_count = serializers.ReadOnlyField()
    property_count = serializers.ReadOnlyField()
    
    class Meta:
        model = State
        fields = [
            'id', 'name', 'code', 'slug', 'country', 'country_id',
            'type', 'is_active', 'city_count', 'property_count',
            'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
    
    def validate_country_id(self, value):
        """Validate that the country exists and is active"""
        try:
            country = Country.objects.get(id=value, is_active=True)
        except Country.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive country.")
        return value


class StateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for state lists
    """
    
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    
    class Meta:
        model = State
        fields = [
            'id', 'name', 'code', 'slug', 'type',
            'country_name', 'country_code', 'is_active'
        ]


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model
    """
    
    state = StateListSerializer(read_only=True)
    state_id = serializers.IntegerField(write_only=True)
    country = serializers.SerializerMethodField()
    full_name = serializers.ReadOnlyField()
    coordinates = serializers.ReadOnlyField()
    property_count = serializers.ReadOnlyField()
    
    class Meta:
        model = City
        fields = [
            'id', 'name', 'slug', 'state', 'state_id', 'country',
            'latitude', 'longitude', 'coordinates', 'population',
            'area_km2', 'timezone', 'postal_codes', 'is_capital',
            'is_major', 'is_active', 'description', 'image',
            'full_name', 'property_count', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
    
    def get_country(self, obj):
        """Get country information"""
        return {
            'id': obj.state.country.id,
            'name': obj.state.country.name,
            'code': obj.state.country.code,
            'currency_symbol': obj.state.country.currency_symbol,
            'flag_emoji': obj.state.country.flag_emoji
        }
    
    def validate_state_id(self, value):
        """Validate that the state exists and is active"""
        try:
            state = State.objects.select_related('country').get(
                id=value, is_active=True, country__is_active=True
            )
        except State.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive state.")
        return value
    
    def validate_postal_codes(self, value):
        """Validate postal codes format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Postal codes must be a list.")
        
        for code in value:
            if not isinstance(code, str) or len(code.strip()) == 0:
                raise serializers.ValidationError(
                    "Each postal code must be a non-empty string."
                )
        
        return value


class CityListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for city lists
    """
    
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='state.country.name', read_only=True)
    country_code = serializers.CharField(source='state.country.code', read_only=True)
    currency_symbol = serializers.CharField(source='state.country.currency_symbol', read_only=True)
    flag_emoji = serializers.CharField(source='state.country.flag_emoji', read_only=True)
    
    class Meta:
        model = City
        fields = [
            'id', 'name', 'slug', 'state_name', 'country_name',
            'country_code', 'currency_symbol', 'flag_emoji',
            'is_capital', 'is_major', 'is_active', 'image'
        ]


class CityDetailSerializer(CitySerializer):
    """
    Detailed serializer for city detail view
    """
    
    nearby_cities = serializers.SerializerMethodField()
    
    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ['nearby_cities']
    
    def get_nearby_cities(self, obj):
        """Get nearby cities"""
        nearby = obj.get_nearby_cities(radius_km=100)[:5]  # Limit to 5 nearby cities
        return CityListSerializer(nearby, many=True).data


class CityCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating cities
    """
    
    class Meta:
        model = City
        fields = [
            'name', 'state', 'latitude', 'longitude', 'population',
            'area_km2', 'timezone', 'postal_codes', 'is_capital',
            'is_major', 'is_active', 'description', 'image'
        ]
    
    def validate(self, attrs):
        """Validate city data"""
        # Check for duplicate city name in the same state
        name = attrs.get('name')
        state = attrs.get('state')
        
        if name and state:
            existing_city = City.objects.filter(
                name__iexact=name,
                state=state,
                is_deleted=False
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_city = existing_city.exclude(pk=self.instance.pk)
            
            if existing_city.exists():
                raise serializers.ValidationError({
                    'name': f'A city with name "{name}" already exists in {state.name}.'
                })
        
        # Validate coordinates if provided
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if latitude is not None and longitude is not None:
            if not (-90 <= float(latitude) <= 90):
                raise serializers.ValidationError({
                    'latitude': 'Latitude must be between -90 and 90 degrees.'
                })
            
            if not (-180 <= float(longitude) <= 180):
                raise serializers.ValidationError({
                    'longitude': 'Longitude must be between -180 and 180 degrees.'
                })
        
        return attrs


class CityStatsSerializer(serializers.Serializer):
    """
    Serializer for city statistics
    """
    
    total_cities = serializers.IntegerField()
    active_cities = serializers.IntegerField()
    major_cities = serializers.IntegerField()
    capital_cities = serializers.IntegerField()
    cities_by_country = serializers.DictField()
    cities_by_state = serializers.DictField()
    top_cities_by_properties = serializers.ListField()


class CountryStatsSerializer(serializers.Serializer):
    """
    Serializer for country statistics
    """
    
    total_countries = serializers.IntegerField()
    active_countries = serializers.IntegerField()
    countries_by_continent = serializers.DictField()
    top_countries_by_cities = serializers.ListField()
    top_countries_by_properties = serializers.ListField()


class StateStatsSerializer(serializers.Serializer):
    """
    Serializer for state statistics
    """
    
    total_states = serializers.IntegerField()
    active_states = serializers.IntegerField()
    states_by_type = serializers.DictField()
    top_states_by_cities = serializers.ListField()
    top_states_by_properties = serializers.ListField()