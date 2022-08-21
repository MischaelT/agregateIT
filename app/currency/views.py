from urllib.parse import urlencode

from currency.filters import RateFilter
from currency.forms import RateCrispyForm, SourceCrispyForm
from currency.models import ContactUs, Rate, Source
from currency.services import get_latest_rates
from currency.tasks import send_email

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from django_filters.views import FilterView


class IndexView(TemplateView):

    """
        Classview for index page
    """

    template_name = 'index.html'


class ContactUsListView(ListView):

    """
        Classview for contact us page
    """

    queryset = ContactUs.objects.all()
    template_name = 'contact_us.html'


class RateListView(FilterView):

    """
        Classview for rates page
    """

    queryset = Rate.objects.all().select_related('source').order_by('-created')
    template_name = 'rate_list.html'
    paginate_by = 5
    filterset_class = RateFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        get_parameters = {}
        for key, value in self.request.GET.items():
            if key != 'page':
                get_parameters[key] = value

        context['pagination_params'] = urlencode(get_parameters)

        return context


class LatestRatesListView(TemplateView):

    """
        Classview for latest rates page
    """

    # queryset = ContactUs.objects.all()
    template_name = 'latest_rate.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rate_list'] = get_latest_rates()
        return context


class SourceListView(ListView):

    """
        Classview for sources page
    """

    queryset = Source.objects.all()
    template_name = 'source_list.html'


class RateDetailView(LoginRequiredMixin, DetailView):

    """
        Classview for rate details page
    """

    queryset = Rate.objects.all()
    template_name = 'rate_details.html'


class SourceDetailView(LoginRequiredMixin, DetailView):

    """
        Classview for sourse details page
    """

    queryset = Source.objects.all()
    template_name = 'source_details.html'


class RateCreateView(UserPassesTestMixin, CreateView):

    """
        Classview for create rate page
    """

    queryset = Rate.objects.all()
    form_class = RateCrispyForm
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'create_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class RateDeleteView(UserPassesTestMixin, DeleteView):

    """
        Classview for delete rate page
    """

    queryset = Rate.objects.all()
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'delete_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class RateUpdateView(UserPassesTestMixin, UpdateView):

    """
        Classview for update rate page
    """

    queryset = Rate.objects.all()
    form_class = RateCrispyForm
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'update_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceCreateView(CreateView):

    """
        Classview for create source page
    """

    queryset = Source.objects.all()
    form_class = SourceCrispyForm
    success_url = reverse_lazy('currency:source-list')
    template_name = 'create_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceDeleteView(UserPassesTestMixin, DeleteView):

    """
        Classview for delete source page
    """

    queryset = Source.objects.all()
    success_url = reverse_lazy('currency:source-list')
    template_name = 'delete_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceUpdateView(UserPassesTestMixin, UpdateView):

    """
        Classview for update source page
    """

    queryset = Source.objects.all()
    form_class = SourceCrispyForm
    success_url = reverse_lazy('currency:source-list')
    template_name = 'update_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class EmailCreateView(CreateView):

    """
        Classview for create email page
    """

    model = ContactUs
    success_url = reverse_lazy('index')
    template_name = 'contact_us.html'
    fields = ('email_from',
              'subject',
              'message',)

    # form.clean_data - провалидированные данные
    def form_valid(self, form):
        email = form.cleaned_data['email_from']
        subject = form.cleaned_data['subject']
        text = form.cleaned_data['message']
        recipient_list = []

        full_email = f'''
        Email from: {email}
        Subject: {subject}
        Message: {text}

        '''
        send_email.apply_async(args=(subject, full_email, recipient_list))
        return super().form_valid(form)
