from django.urls import path
from . import views

urlpatterns = [
    path('',views.intro,name='intro'),
    path('members/login/',views.login,name='login'),
    path('members/register/',views.register,name='register'),
    path('members/', views.members, name='members'),
    path("members/dashboard/",views.dashboard,name='dashboard'),
    path('members/dummy/',views.dummy,name='dummy'),
    path('members/veggies/',views.veggies,name='veggies'),
    path('members/addtocart/',views.add_cart,name='add_cart'),
    path('members/user_quantity/',views.user_update_quantity,name='user_update_quantity'),
    path("members/user_manage_order/",views.user_manage_order,name='user_manage_order'),
    path('members/addtocart/checkout/',views.checkout,name='checkout'),
    path('members/addtocart/checkout/customer_detail/',views.customerdetails,name='customer_detail'),
    path("members/nav",views.search,name="search"),
    path("members/price",views.price,name='price'),
]