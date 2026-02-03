from django.urls import path
from .views import FileUploadView, HistoryView, LatestSummaryView, PDFReportView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('summary/latest/', LatestSummaryView.as_view(), name='latest-summary'),
    path('report/<int:pk>/', PDFReportView.as_view(), name='pdf-report'),
]
