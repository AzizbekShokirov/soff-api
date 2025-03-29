from rest_framework.permissions import BasePermission


class GroupPermission(BasePermission):
    """
    Base permission to check if a user belongs to a specific group.
    """

    def __init__(self, group_name):
        self.group_name = group_name

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.groups.filter(name=self.group_name).exists()
        )


class HasAccessToSwagger(GroupPermission):
    """
    Custom permission to only allow users in the 'Swagger Access' group.
    """

    def __init__(self):
        super().__init__("Swagger Access")


class IsCustomer(GroupPermission):
    """
    Custom permission to only allow users in the 'Customer' group.
    """

    def __init__(self):
        super().__init__("Customer")


class IsManufacturer(GroupPermission):
    """
    Custom permission to only allow users in the 'Manufacturer' group.
    """

    def __init__(self):
        super().__init__("Manufacturer")


class IsGuest(BasePermission):
    """
    Custom permission to only allow unregistered users.
    """

    def has_permission(self, request, view):
        return not request.user or not request.user.is_authenticated
