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
    template_name = 'index.html'


class ContactUsListView(ListView):
    queryset = ContactUs.objects.all()
    template_name = 'contact_us.html'


class RateListView(FilterView):
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
    # queryset = ContactUs.objects.all()
    template_name = 'latest_rate.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rate_list'] = get_latest_rates()
        return context


class SourceListView(ListView):
    queryset = Source.objects.all()
    template_name = 'source_list.html'


class RateDetailView(LoginRequiredMixin, DetailView):
    queryset = Rate.objects.all()
    template_name = 'rate_details.html'


class SourceDetailView(LoginRequiredMixin, DetailView):
    queryset = Source.objects.all()
    template_name = 'source_details.html'


class RateCreateView(UserPassesTestMixin, CreateView):
    queryset = Rate.objects.all()
    form_class = RateCrispyForm
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'create_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class RateDeleteView(UserPassesTestMixin, DeleteView):
    queryset = Rate.objects.all()
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'delete_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class RateUpdateView(UserPassesTestMixin, UpdateView):
    queryset = Rate.objects.all()
    form_class = RateCrispyForm
    success_url = reverse_lazy('currency:rate-list')
    template_name = 'update_rate.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceCreateView(CreateView):
    queryset = Source.objects.all()
    form_class = SourceCrispyForm
    success_url = reverse_lazy('currency:source-list')
    template_name = 'create_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceDeleteView(UserPassesTestMixin, DeleteView):
    queryset = Source.objects.all()
    success_url = reverse_lazy('currency:source-list')
    template_name = 'delete_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class SourceUpdateView(UserPassesTestMixin, UpdateView):
    queryset = Source.objects.all()
    form_class = SourceCrispyForm
    success_url = reverse_lazy('currency:source-list')
    template_name = 'update_source.html'

    def test_func(self):
        return self.request.user.is_superuser


class EmailCreateView(CreateView):
    model = ContactUs
    template_name = 'contact_us.html'
    success_url = reverse_lazy('currency:index')
    fields = (
            'email_from',
            'subject',
            'message',
    )

    # form.clean_data - провалидированные данные
    def form_valid(self, form):
        email = form.cleaned_data['email_from']
        subject = form.cleaned_data['subject']
        text = form.cleaned_data['message']

        full_email = f'''
        Email from: {email}
        Subject: {subject}
        Message: {text}

        '''
        send_email.apply_async(args=(subject, full_email))
        return super().form_valid(form)
