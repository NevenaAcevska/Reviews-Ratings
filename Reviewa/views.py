from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.db import IntegrityError
from django.db.models import Count, Avg
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse

from Reviewa.forms import UserProfileForm, FeedbackForm
from Reviewa.models import User, Product, Feedback, Business


def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, email=username, password=password)
        print(username)
        print(password)
        print(user)
        all=User.objects.all()
        print(all)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            if user.first_login:
                # Set first_login to False
                user.first_login = False
                user.save()
                # Redirect to the edit profile page
                return redirect('edit_profile')
            elif user.is_admin:
                # Redirect to the dashboard
                return redirect('n')
            else:
                # Redirect to the index page
                return redirect('index')  # Redirect to the index page after successful login
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))




def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            return redirect("index")  # Redirect to the index page after successful registration
        except IntegrityError:
            return render(request, "register.html", {
                "message": "An error occurred during registration."
            })
    else:
        return render(request, "register.html")


@login_required
def profile(request):
    # Get the current authenticated user
    user = request.user

    return render(request, 'profile.html', {'user': user})

@login_required
def n(request):
    user = request.user
    all_users=User.objects.filter(is_admin=False)
    # Get the user's stores
    user_stores = user.store.all() if user.is_authenticated else None

    # Get the selected business from the dropdown
    selected_business_id = request.GET.get('business_id', None)

    selected_user = request.GET.get('user', None)
    selected_product = request.GET.get('product', None)
    selected_rate = request.GET.get('rate', None)
    selected_date = request.GET.get('date', None)
    # Debug prints
    print("Selected store:", selected_business_id)
    print("Selected user:", selected_user)
    print("Selected product:", selected_product)
    print("Selected rate:", selected_rate)
    print("Selected date:", selected_date)
    # Check if 'All' is selected
    if selected_business_id == '0':
        feedbacks = Feedback.objects.filter(product__business__in=user_stores)
        selected_business = None
    elif selected_business_id:
        selected_business = Business.objects.get(id=selected_business_id)  # Fetch the selected business object
        feedbacks = Feedback.objects.filter(product__business__id=selected_business_id)
    else:
        feedbacks = Feedback.objects.filter(product__business__in=user_stores)
        selected_business = None

    # Apply filtering based on selected parameters
    if selected_user and selected_user != '0':
        if selected_user == 'anonymous':
            feedbacks = feedbacks.filter(user=None)
        else:
            feedbacks = feedbacks.filter(user_id=selected_user)
    if selected_product and selected_product != '0':
        feedbacks = feedbacks.filter(product_id=selected_product)
    if selected_rate and selected_rate != '0':
        feedbacks = feedbacks.filter(rate=selected_rate)
    if selected_date:
        feedbacks = feedbacks.filter(time_date__date=selected_date)

    # Filter products by the user's stores
    products = Product.objects.filter(business__in=user_stores) if user_stores else Product.objects.none()

    # Calculate average rating
    average_rating = feedbacks.values('product__product_name').annotate(average_rate=Avg('rate'))

    # Count number of feedbacks per product
    feedbacks_per_product = feedbacks.values('product__product_name', 'product__id').annotate(
        count=Count('product')).order_by('-count')

    # Feedback distribution by rating for each product
    feedback_distribution = feedbacks.values('product__product_name', 'rate').annotate(
        count=Count('rate')).order_by('product__product_name', 'rate')

    return render(request, 'ADMIN_JAS.html', {
        'feedbacks': feedbacks,
        'products': products,
        'average_rating': average_rating,
        'feedbacks_per_product': feedbacks_per_product,
        'feedback_distribution': feedback_distribution,
        'selected_business': selected_business,
        'all_users': all_users,
    })




from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from .models import Product, Feedback

@login_required
def admin_product(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)

        # Calculate average rating for the specific product
        average_rating = Feedback.objects.filter(product=product).aggregate(average_rate=Avg('rate'))

        # Count number of feedbacks for the specific product
        feedbacks_per_product = Feedback.objects.filter(product=product).values('product__product_name', 'product__id').annotate(
            count=Count('product')).order_by('-count')

        # Feedback distribution by rating for the specific product
        feedback_distribution = Feedback.objects.filter(product=product).values('product__product_name',
                                                                                'rate').annotate(
            count=Count('rate')).order_by('product__product_name', 'rate')
        all_feedbacks = Feedback.objects.filter(product=product)
        return render(request, 'ADMIN_PRODUCT.html', {
            'product': product,
            'average_rating': average_rating,
            'feedbacks_per_product': feedbacks_per_product,
            'all_feedbacks': all_feedbacks,
            'feedback_distribution': feedback_distribution,
        })
    except Product.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'Product does not exist.'})



def display_products(request):
    # Get all products from the database
    products = Product.objects.all().values('id', 'product_name')

    products_list = list(products)

    # Render the template with the products
    return JsonResponse({'products': products_list})


def product_detail(request, product_id):
    # Get the product object or return a 404 error if the product does not exist
    product = get_object_or_404(Product, pk=product_id)
    print(f"Retrieved product: {product}")  # Debugging line
     # Render the template with the product and the form
    return render(request, 'product_detail.html', {'product': product})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db import IntegrityError


def create_feedback(request):
    response_data = {}

    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)

            # Set user to authenticated user if available, else set to None
            feedback.user = request.user if request.user.is_authenticated else None

            try:
                feedback.save()
                response_data['result'] = 'success'
                response_data['message'] = 'Feedback submitted successfully.'
                response_data['feedback'] = model_to_dict(feedback)
                print(f"New Feedback - Product: {feedback.product}, Rate: {feedback.rate}, Comment: {feedback.comment}")

            except IntegrityError as e:
                response_data['result'] = 'error'
                response_data['message'] = 'Error submitting feedback.'
                response_data['errors'] = {'user': ['User must be authenticated or set to None.']}

        else:
            response_data['result'] = 'error'
            response_data['message'] = 'Error submitting feedback.'
            response_data['errors'] = form.errors
    else:
        form = FeedbackForm()

    return JsonResponse(response_data)
