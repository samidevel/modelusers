from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

from .forms import (
    UserRegisterForm,
    LoginForm,
    UpdatePasswordForm,
    VerificacionForm

)


from django.views.generic import (
    View,
    CreateView
)

from django.views.generic.edit import (
    FormView
)

from .models import User

from .functions import code_generator

class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = '/'

    def form_valid(self, form):

        codigo = code_generator()

        usuario = User.objects.create_user(
            form.cleaned_data['username'],
            form.cleaned_data['email'],
            form.cleaned_data['password1'],
            nombres = form.cleaned_data['nombres'],
            apellidos = form.cleaned_data['apellidos'],
            genero = form.cleaned_data['genero'],
            codregistro=codigo
            
        )
        # envio de codigo
        asunto = 'Confirmacion de email'
        mensaje = 'Codigo de verificacion' + codigo
        email_remitente = 'yesideveloper@gmail.com'
        send_mail(asunto, mensaje, email_remitente, [form.cleaned_data['email'],])
        #redirigir a la pantalla de validacion

        return HttpResponseRedirect(
            reverse(
                'users_app:user-verification',
                kwargs={'pk': usuario.id}
            )      
    )


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home_app:panel')

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']

        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)




class LogoutView(View):
    def get(self, request, *args, **kargs):
        logout(request)
        return HttpResponseRedirect(
            'users_app:user-login'
        )


class UpdatePasswordView(FormView):
    template_name = 'users/update.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        usuario = self.request.user
        user = authenticate(
            username=usuario.username,
            password=form.cleaned_data['password1']
        )
        if user:
            new_password = form.cleaned_data['password2']
            usuario.set_password(new_password)
            usuario.save()

        logout(self.request)
        return super(UpdatePasswordView, self).form_valid(form)
    



    
class CodeVerificacionView(FormView):
    template_name = 'users/verification.html'
    form_class = VerificacionForm   
    success_url = reverse_lazy('home_app:panel')

    def get_form_kwargs(self):
        kwargs = super(CodeVerificacionView, self).get_form_kwargs()
        kwargs.update({
            'pk': self.kwargs['pk'],
        })
        return kwargs
    
    def form_valid(self, form):
        User.objects.filter(
            id = self.kwargs['pk']
        ).update(
            is_active=True
        )

        return super(CodeVerificacionView, self).form_valid(form)