from django.shortcuts import redirect
from django.views import View
from kamazon.ia.training import create_yaml_file, create_model

class TrainingBuildView(View):
    def get(self, request, *args, **kwargs):
        create_model()
        return redirect('home')