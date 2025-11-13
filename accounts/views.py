from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
def signup(request):
    if request.method=='POST':
        form=SignUpForm(request.POST)
        if form.is_valid():
            user=form.save(); login(request,user); return redirect('ui:app')
    else:
        form=SignUpForm()
    return render(request,'accounts/signup.html',{'form':form})
from django.contrib.auth.views import LogoutView

class LogoutGetView(LogoutView):
    def get(self, request, *args, **kwargs):
        # call the same logic as POST, so GET will log out
        return self.post(request, *args, **kwargs)
