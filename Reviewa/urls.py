from django.urls import path

from Reviewa import views


urlpatterns = [

    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('profile/', views.profile, name='profile'),
    path('n/', views.n, name='n'),
    path('admin_product/<int:product_id>/', views.admin_product, name='admin_product'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('feedback/', views.create_feedback, name='feedback'),
    path('products/', views.display_products, name='display_products'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),

]