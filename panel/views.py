from django.shortcuts import render
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.forms import ValidationError
from .models import Student, Book, Borrow, Transaction
from django.contrib.auth import authenticate, login, logout
from panel.qSort import qSortBooks,qSortStudents,qSortBorrows
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
# Create your views here.
def testView(request):
    return render (request, 'panel/index.html')



def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password )
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'panel/login.html', {'message':'Invalid Credentials'})
    return render(request, 'panel/login.html')



def signupPage(request):
    data={}
# Data Validation
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        regno = request.POST.get('regno')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confpass = request.POST.get('confpass')

        if fullname == '':
            data['error'] = "'Fullname' field cannot be empty"
        if regno == '':
            data['error'] = "'Register number' field cannot be empty"
        if email == '':
            data['error'] = "'Email' field cannot be empty"

    #    Password validation
        if password != '' and confpass != '' and password == confpass:
            try:
                val = validate_password(password)
                if val == None:
                    fullnamearr = fullname.split(' ')
                    firstname = fullnamearr[0],''.join(fullnamearr[1:])
                    user = User.objects.create_user(firstname,email,password)
                    user.first_name = firstname
                    user.save()
                    st = Student.objects.create(
                        fullname = fullname,
                        regno = regno,
                        email = email,
                        user = user,
                    )
                    st.save()
                    messages.success(request, "Yayy..! Account created successfully.")
                    return redirect('login')
            except ValidationError as v:
                data['error'] = '\n'.join(v)
                return render(request, 'panel/signup.html', data)
            return render(request, 'panel/signup.html', data)
    
    

    return render(request, 'panel/signup.html')


@login_required
def dashBoard(request):
    
    stud = Student.objects.get(user = User.objects.get(id = request.user.id))
    book_count = Book.objects.count()
    borrow_count = Borrow.objects.filter(borrower=stud).count()
    pending_returns = 0
    borrows = list(Borrow.objects.filter(borrower = stud))
    
    
    # Total fine calculation
    borrow_fine = list(Borrow.objects.filter(borrower = stud).values_list('fine_amount', flat=True))
    total_fine = sum(borrow_fine)
    
    # Pending returns
    for s in borrow_fine:
        if s > 0:
            pending_returns += 1
            qSortBorrows(borrows, 'fine_amount')
            borrows = borrows[-5:]
            
    # Books in demand
    demand_books = list(Borrow.objects.filter(borrower = stud).values_list('book', flat=True))
    data = {'book_count': book_count, 'borrow_count':borrow_count, 'total_fine':total_fine, 'pending_returns':pending_returns, 'fullname':stud.fullname}
    if pending_returns != 0:
        data['borrows'] = borrows
    if len(demand_books) != 0:
        data['demand_books'] = demand_books
    data['fullname'] = stud.fullname
    return render(request, 'panel/dashboard.html', data)





def books(request):

    books = list(Book.objects.all())
    if request.method == 'POST':
        key = request.POST.get('sort_by')
        qSortBooks(books,key.lower())
    return render(request, 'panel/books.html', {'books':books})




def students(request):
    students = list(Student.objects.all())
    if request.method == 'POST':
        key = request.POST.get('sort_by')
        qSortStudents(students,key.lower())
    return render(request, 'panel/students.html' ,{'students':students})


# Adding books
def addBooks(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn_number = request.POST.get('isbn_number')
        copies = request.POST.get('copies')
        book = Book(
            isbn_number = isbn_number,
            title = title,
            author = author,
            copies = copies)
        
        book.save()
        messages.success(request, 'Book added successfully..!')
        return redirect('addbook')
    return render(request, 'panel/add_book.html')
        


# Adding Students
def addStudent(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        regno = request.POST.get('regno')
        email = request.POST.get('email')
        student = Student(
            fullname = fullname,
            regno = regno,
            email = email,
        )
        student.save()
        messages.success(request, 'Student added successfully..!')
        return redirect('addstudent')
    return render(request, 'panel/add_student.html')





# Make a booking
def addBookings(request, book_id):
    stud = Student.objects.get(user = User.objects.get(id = request.user.id))
    book = Book.objects.get(id = book_id)
    data = {'fullname': stud.fullname, 'book': book,}
    if request.method == 'POST':
        borrower = request.POST.get('borrower')
        due_date = request.POST.get('due_date')
        # Check book availability
        bk = list(Borrow.objects.filter(book=book).values_list('book', flat=True))
        if len(bk) < book.copies:
            borrow = Borrow(
                borrower=Student.objects.get(fullname=borrower),
                due_date=due_date,
                book=Book.objects.get(title=book)
            )
            borrow.save()
            return redirect('bookings')
        else:
            messages.error('The requested book is not in stock')
    return render(request, 'panel/add_bookings.html', data )

# Return booking


def returnbook(request, borrow_id):
    brw = Borrow.objects.get(id = borrow_id)
    if brw.due_date < timezone.now().date():
        color = 'red'
    else:
        color = 'green'
    if request.method == 'POST':
        stud = Student.objects.get(user = User.objects.get(id = request.user.id))
        if stud.balance >= brw.fine_amount:
            stud.balance = stud.balance - brw.fine_amount
            stud.save()
            tr = Transaction.objects.create(
                payer = stud,
                book  = brw.book,
                amount = brw.fine_amount
            )
            tr.save()
            brw.delete()
            return redirect('bookings')
        else:
            return render(request, 'panel/return_book.html',{'borrow':brw, 'color':color, messages:'Insufficient funds'} )
    return render(request, 'panel/return_book.html', {'borrow':brw, 'color':color})


def bookings(request):
        
      stud = Student.objects.get(user = User.objects.get(id = request.user.id))
      borrows = list(Borrow.objects.filter(borrower = stud))
      if request.method ==  'POST':
        key = request.POST.get('sort_by')
        qSortBorrows(borrows, key.lower())
      return render(request, 'panel/bookings.html', {'borrows': borrows, 'fullname': stud.fullname})
    


def wallet(request):
    stud = Student.objects.get(user = User.objects.get(id = request.user.id))
    borrow_fine = list(Borrow.objects.filter(borrower = stud).values_list('fine_amount', flat=True))
    total_fine = sum(borrow_fine)
    transactions = Transaction.objects.filter(payer = stud)
    return render(request, 'panel/wallet.html', {'student':stud, 'fullname':stud.fullname, 'total_fine':total_fine, 'transactions':transactions})

def logoutApp(request):
    logout(request)
    return redirect(loginPage)






