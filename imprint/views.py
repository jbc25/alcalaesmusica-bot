from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site


class AboutView(TemplateView):
    template_name = 'about.html'
    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['site'] = get_current_site(self.request)
        return context

