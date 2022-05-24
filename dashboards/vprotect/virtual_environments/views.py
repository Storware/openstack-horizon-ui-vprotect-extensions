from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'backup/virtual_environments/index.html'
