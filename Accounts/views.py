from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from .forms import CustomAuthenticationForm
from django.views.generic.edit import CreateView
from .forms import UserCreationForm
from django.contrib import messages
from .models import MyUser
from django.contrib.auth.mixins import LoginRequiredMixin


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        # Call the parent class's form_valid() method to perform the default authentication checks
        response = super().form_valid(form)

        # Perform additional authentication checks here
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user is None or not user.is_active:
            # Authentication failed, return an error response
            return self.form_invalid(form)

        # Authentication succeeded, log the user in and redirect to the success URL
        login(self.request, user)
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Username Or Password.')
        return super().form_invalid(form)


class UserRegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        # Save the user and return the response
        email = form.cleaned_data.get('email')
        if MyUser.objects.filter(email=email).exists():
            form.add_error('email', 'This Email is already taken.')
            return super().form_invalid(form)
        messages.success(self.request, 'Your account has been created. Please log in to continue.')
        return super().form_valid(form)


class UserLogoutView(LoginRequiredMixin, LogoutView):
    pass

