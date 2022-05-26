from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'backup/task_console/index.html'
