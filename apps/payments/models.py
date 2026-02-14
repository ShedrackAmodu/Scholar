from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.students.models import Student
from apps.classes.models import Class, ClassLevel
from apps.school.models import AcademicYear, SchoolProfile
import uuid
from django.utils import timezone


class FeeCategory(models.Model):
    """Categories of fees"""

    class Frequency(models.TextChoices):
        ONE_TIME = 'ONCE', 'One Time'
        TERMLY = 'TERM', 'Termly'
        YEARLY = 'YEAR', 'Yearly'
        MONTHLY = 'MONTH', 'Monthly'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.TERMLY)
    is_compulsory = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Fee Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """Fee structure for different classes"""
    category = models.ForeignKey(
        FeeCategory,
        on_delete=models.PROTECT,
        related_name='structures')
    name = models.CharField(max_length=200)

    # Applicability
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    class_specific = models.ForeignKey(
        Class, on_delete=models.PROTECT, null=True, blank=True)

    # Amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)])

    # Dates
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    term = models.CharField(
        max_length=10,
        choices=SchoolProfile.TermChoices.choices,
        null=True,
        blank=True)

    # Due date
    due_date = models.DateField()

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-academic_year', 'term']

    def __str__(self):
        return f"{self.name} - ₦{self.amount}"


class Invoice(models.Model):
    """Invoices generated for students"""

    class Status(models.TextChoices):
        PENDING = 'PEND', 'Pending'
        PARTIAL = 'PART', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVER', 'Overdue'
        CANCELLED = 'CANC', 'Cancelled'

    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='invoices')

    # Fees included
    fee_items = models.ManyToManyField(FeeStructure, through='InvoiceItem')

    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    # Dates
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    # Status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING)

    # Academic info
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    term = models.CharField(max_length=10,
                            choices=SchoolProfile.TermChoices.choices)

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.student} - ₦{self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number (e.g., INV202400001)
            year = timezone.now().year
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV{year}"
            ).order_by('invoice_number').last()

            if last_invoice:
                last_number = int(last_invoice.invoice_number[-5:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.invoice_number = f"INV{year}{new_number:05d}"

        self.balance = self.total_amount - self.amount_paid

        # Update status based on payment
        if self.balance <= 0:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        elif timezone.now().date() > self.due_date:
            self.status = self.Status.OVERDUE

        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Individual items on an invoice"""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payments made by parents"""

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        TRANSFER = 'TRANS', 'Bank Transfer'
        CARD = 'CARD', 'Card'
        CHEQUE = 'CHQ', 'Cheque'
        PAYSTACK = 'PS', 'Paystack'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PEND', 'Pending'
        SUCCESS = 'SUCC', 'Successful'
        FAILED = 'FAIL', 'Failed'
        REFUNDED = 'REF', 'Refunded'

    transaction_id = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments')
    payer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments_made')

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices)
    reference = models.CharField(max_length=100, unique=True)

    # Paystack specific
    paystack_access_code = models.CharField(max_length=100, blank=True)
    paystack_authorization_url = models.URLField(blank=True)

    # Status
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING)

    # Dates
    payment_date = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.transaction_id} - ₦{self.amount}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{
                timezone.now().strftime('%Y%m%d%H%M%S')}{
                uuid.uuid4().hex[
                    :6].upper()}"
        super().save(*args, **kwargs)

        # Update invoice amount paid
        if self.status == self.PaymentStatus.SUCCESS:
            invoice = self.invoice
            invoice.amount_paid += self.amount
            invoice.save()


class PaymentReceipt(models.Model):
    """Receipts for successful payments"""
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    pdf_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCPT{
                timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)


class Discount(models.Model):
    """Discounts applicable to fees"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[
            MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(blank=True)

    # Applicability
    applicable_to_all = models.BooleanField(default=True)
    applicable_classes = models.ManyToManyField(Class, blank=True)

    # Validity
    valid_from = models.DateField()
    valid_to = models.DateField()

    # Usage
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
