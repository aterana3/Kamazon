from django.http import JsonResponse
from django.views import View
from kamazon.training.training import train_model

class ExecuteTraining(View):
    def get(self, request, pk):
        train_model(pk)
        return JsonResponse({'message': 'Training started successfully.'})