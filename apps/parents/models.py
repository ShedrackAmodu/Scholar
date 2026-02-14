from django.db import models
from apps.accounts.models import User
from apps.students.models import Student


class Parent(models.Model):
    """Parent profile extending User"""

    class Relationship(models.TextChoices):
        FATHER = 'FATHER', 'Father'
        MOTHER = 'MOTHER', 'Mother'
        GUARDIAN = 'GUARDIAN', 'Legal Guardian'
        GRANDPARENT = 'GRANDPARENT', 'Grandparent'
        OTHER = 'OTHER', 'Other'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile')

    # Personal Info
    occupation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)

    # Contact
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()

    # Emergency Contact (if different)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relationship = models.CharField(
        max_length=50, blank=True)

    # Children
    children = models.ManyToManyField(
        Student, through='ParentStudentRelationship')

    # Notification Preferences
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.user.get_full_name()


class ParentStudentRelationship(models.Model):
    """Link parents to students with relationship type"""
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    relationship = models.CharField(
        max_length=20, choices=Parent.Relationship.choices)
    is_primary_contact = models.BooleanField(default=False)
    can_pickup = models.BooleanField(
        default=True)  # Can pick child from school
    receives_notifications = models.BooleanField(default=True)

    class Meta:
        unique_together = ['parent', 'student']

    def __str__(self):
        return f"{
            self.parent} - {
            self.student} ({
            self.get_relationship_display()})"
