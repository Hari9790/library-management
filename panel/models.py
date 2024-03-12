from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    fullname = models.CharField(max_length=200, null=True)
    regno = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    balance = models.DecimalField(decimal_places=2,max_digits=7,default=0.0)


    def __str__(self):
        return self.fullname
    
    def delete(self, *args, **kwargs):
        # Custom logic to delete related records before deleting the student
        # Example: Delete all associated Borrow records
        self.borrow_set.all().delete()
        super().delete(*args, **kwargs)
    

class Book(models.Model):
    title = models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=200, null=True)
    isbn_number = models.CharField(max_length=20, null=True)
    copies = models.IntegerField(null=True)


    def __str__(self):
        return self.title
    

class Borrow(models.Model):
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE, default=None)
    borrowed_on = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True)
    fine_amount = models.DecimalField(decimal_places=2, max_digits=7, default=0.0)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.borrower)+"-"+str(self.book)
    
    
    
class Transaction(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4, max_length=256)
    payment_timestamp = models.DateTimeField(auto_now_add=True)
    payer = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(decimal_places=2, max_digits=7, default=0.0)


    def __str__(self):
        return self.id
