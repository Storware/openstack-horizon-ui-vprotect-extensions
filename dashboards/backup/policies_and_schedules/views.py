from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'backup/policies_and_schedules/index.html'
