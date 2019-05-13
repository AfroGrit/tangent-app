from rest_framework import serializers
from core.models import Tag, Department, Employee


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for an dept object"""

    class Meta:
        model = Department
        fields = ('id', 'name')
        read_only_fields = ('id',)


class EmployeeSerializer(serializers.ModelSerializer):
    """Serialize an Employee"""
    department = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Department.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Employee
        fields = (
            'id', 'title',
            'department', 'tags',
            'experience', 'salary', 'link',
        )
        read_only_fields = ('id',)


class EmployeeDetailSerializer(EmployeeSerializer):
    """ Serialize employee details"""
    department = DepartmentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class EmployeeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to employees"""

    class Meta:
        model = Employee
        fields = ('id', 'image')
        read_only_fields = ('id',)
