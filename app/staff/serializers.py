from rest_framework import serializers
from core.models import Tag, Department, Employee


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = Department
        fields = ('id', 'name')
        read_only_fields = ('id',)


class EmployeeSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""
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
