from kamazon.training.training import train_model
from django.shortcuts import redirect
from django.views import View

class TrainingBuildView(View):
    def get(self, request, *args, **kwargs):
        train_model()
        return redirect('home')