from django.shortcuts import render
from django.views import View
from pyano2.models import Topic

class IndexView(View):
    template_name = 'pyano2/index.html'

    def get(self, request, *args, **kwargs):
        topics = Topic.objects.all()
        context = {"topics": topics}
        if request.GET.get("topic") is not None:
            context["topic"] = request.GET.get("topic")
        return render(request, template_name=self.template_name, context=context)
