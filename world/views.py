import json
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from haystack.query import SearchQuerySet
from .util import otp_generator, send_otp_email, validate_otp
from .models import User, City, Country, Countrylanguage

# Home view - requires login
@login_required
def home(request):
    return render(request, "home.html")

# Search view - requires login
@login_required
def search(request):
    query = request.GET.get("query", "").strip()
    result = {"cities": [], "countries": [], "languages": []}
    
    if not query or len(query) < 3:
        return JsonResponse(result)

    city_pks = list(SearchQuerySet().autocomplete(i_city_name=query).values_list("pk", flat=True))
    country_pks = list(SearchQuerySet().autocomplete(i_country_name=query).values_list("pk", flat=True))
    language_pks = list(SearchQuerySet().autocomplete(i_language_name=query).values_list("pk", flat=True))

    result["cities"] = [City.objects.filter(pk=city_pk).values().first() for city_pk in city_pks]
    result["countries"] = [Country.objects.filter(pk=country_pk).values().first() for country_pk in country_pks]
    result["languages"] = [Countrylanguage.objects.filter(pk=language_pk).values().first() for language_pk in language_pks]

    return render(request, "search_results.html", result)

# Signup page - shows the form
def signup(request):
    return render(request, "signup.html")

# Signup validation view (handles AJAX request to validate user input)
@csrf_exempt
def signup_validate(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    email = body.get("email", "")
    first_name = body.get("first_name", "")
    last_name = body.get("last_name", "")
    gender = body.get("gender", "female")
    phone_number = body.get("phone_number", "")

    if not email:
        return JsonResponse({"success": False, "message": "Email not found"})
    if not first_name:
        return JsonResponse({"success": False, "message": "First name not found"})

    try:
        User.objects.create(email=email, 
                            first_name=first_name,
                            last_name=last_name,
                            phone_number=phone_number,
                            gender=gender)
    except IntegrityError:
        return JsonResponse({"success": False, "message": "User already exists"})

    otp = otp_generator()
    otp_status = send_otp_email(email, otp)

    if not otp_status:
        return JsonResponse({"success": False, "message": "Incorrect email"})
    
    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    result = {"success": True, "message": "OTP sent to email"}
    return JsonResponse(result)

# Login page
def c_login(request):
    return render(request, "login.html")

# Send OTP (for login)
@csrf_exempt
def send_otp(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    email = body.get("email", "")
    otp = otp_generator()
    otp_status = send_otp_email(email, otp)
    
    if not otp_status:
        return JsonResponse({"success": False, "message": "Incorrect email"})
    
    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    return JsonResponse({"success": True, "message": "OTP sent"})

# Login validation - checks the OTP and logs the user in if valid
@csrf_exempt
def login_validate(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"})

    sent_otp = request.session.get("auth_otp", "")
    sent_email = request.session.get("auth_email", "")
    email = body.get("email", "")
    otp = body.get("otp", "")

    if not email or not otp:
        return JsonResponse({"success": False, "message": "Email or OTP missing"})

    result = validate_otp(otp, sent_otp, email, sent_email)
    if not result["success"]:
        return JsonResponse(result)

    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "message": "Please signup"})

    login(request, user)
    return JsonResponse({"success": True, "message": "Login succeeded"})

# Logout - logs the user out and redirects to login page
@login_required
def c_logout(request):
    logout(request)
    return HttpResponseRedirect("/login")

# Country details view - displays details of a selected country
@login_required
def get_country_details(request, country_name):
    try:
        country = Country.objects.get(name=country_name)
    except Country.DoesNotExist:
        return JsonResponse({"success": False, "message": "Country not found"})

    result = {"country": country}
    return render(request, "country.html", result)
