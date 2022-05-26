from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'backup/mounted_backups/index.html'
