from django.shortcuts import redirect
from django.views import View
from kamazon.ia.training import train_model

class TrainingBuildView(View):
    def get(self, request, *args, **kwargs):
        train_model()
        return redirect('home')