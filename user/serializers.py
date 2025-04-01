from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Customer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role','password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def validate_role(self, value):
        """Convert role to lowercase and validate against choices"""
        lc_value = value.lower()
        if lc_value not in dict(User.ROLE_CHOICES).keys():
            raise serializers.ValidationError(
                f"Invalid role. Allowed values: {dict(User.ROLE_CHOICES).keys()}"
            )
        return lc_value
    
    def create(self, validated_data):
        # extract password and hash it
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'  
