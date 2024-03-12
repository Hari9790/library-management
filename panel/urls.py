from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/', views.dashBoard, name='home'),
    path('', views.loginPage, name='login'),
    path('logout/', views.logoutApp, name='logout'),
    path('signup/', views.signupPage, name='signup'),
    path('books/',views.books, name="books"),
    path('students/', views.students,name='students'),
    path('addbook/', views.addBooks, name='addbook'),
    path('addstudent/', views.addStudent, name='addstudent'),
    path('addbookings/<int:book_id>/', views.addBookings, name='addbookings'),
    path('returnbook/<int:borrow_id>/',views.returnbook, name='returnbook'),
    path('bookings/',views.bookings, name="bookings"),
    path('wallet/', views.wallet, name='wallet'),

]
