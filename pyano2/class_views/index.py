from django.shortcuts import render
from django.views import View


class IndexView(View):
    template_name = 'pyano2/index.html'

    def get(self, request, *args, **kwargs):
        context = {"message": "Welcome to PsYchological ANnOtation page.", "topic": "shoplifting"}
        if request.GET.get("topic") is not None:
            context["topic"] = request.GET.get("topic")
        return render(request, template_name=self.template_name, context=context)
