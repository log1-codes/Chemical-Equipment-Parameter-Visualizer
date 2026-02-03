import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadHistory, EquipmentData
from .serializers import UploadHistorySerializer
from django.db import transaction
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        print(f"Received file upload request: {file_obj.name if file_obj else 'No File'}")
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file_obj)
            
            # Basic validation
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": f"Missing columns. Required: {required_columns}"}, status=status.HTTP_400_BAD_REQUEST)

            summary_stats = {
                'total_count': len(df),
                'avg_flowrate': df['Flowrate'].mean(),
                'avg_pressure': df['Pressure'].mean(),
                'avg_temperature': df['Temperature'].mean(),
                'type_distribution': df['Type'].value_counts().to_dict()
            }

            with transaction.atomic():
                history = UploadHistory.objects.create(
                    filename=file_obj.name,
                    total_count=summary_stats['total_count'],
                    avg_flowrate=summary_stats['avg_flowrate'],
                    avg_pressure=summary_stats['avg_pressure'],
                    avg_temperature=summary_stats['avg_temperature'],
                    type_distribution=summary_stats['type_distribution']
                )

                equipment_objects = [
                    EquipmentData(
                        upload_history=history,
                        name=row['Equipment Name'],
                        equipment_type=row['Type'],
                        flowrate=row['Flowrate'],
                        pressure=row['Pressure'],
                        temperature=row['Temperature']
                    ) for index, row in df.iterrows()
                ]
                EquipmentData.objects.bulk_create(equipment_objects)

                # Keep only last 5 uploads
                ids_to_keep = UploadHistory.objects.order_by('-uploaded_at')[:5].values_list('id', flat=True)
                UploadHistory.objects.exclude(id__in=ids_to_keep).delete()

            return Response(UploadHistorySerializer(history).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    def get(self, request):
        history = UploadHistory.objects.all()[:5]
        serializer = UploadHistorySerializer(history, many=True)
        return Response(serializer.data)

class LatestSummaryView(APIView):
    def get(self, request):
        latest = UploadHistory.objects.first()
        if not latest:
            return Response(None, status=status.HTTP_200_OK)
        serializer = UploadHistorySerializer(latest)
        return Response(serializer.data)

class PDFReportView(APIView):
    def get(self, request, pk):
        try:
            history = UploadHistory.objects.get(pk=pk)
            records = history.equipment_records.all()

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setTitle(f"Equipment Report - {history.uploaded_at}")

            p.drawString(100, 750, "Chemical Equipment Parameter Report")
            p.drawString(100, 730, f"Date: {history.uploaded_at}")
            p.drawString(100, 710, f"Total Count: {history.total_count}")
            p.drawString(100, 690, f"Avg Flowrate: {history.avg_flowrate:.2f}")
            p.drawString(100, 670, f"Avg Pressure: {history.avg_pressure:.2f}")
            p.drawString(100, 650, f"Avg Temperature: {history.avg_temperature:.2f}")

            y = 600
            p.drawString(100, y, "Equipment Details:")
            y -= 20
            p.drawString(100, y, "Name | Type | Flowrate | Pressure | Temp")
            y -= 10
            p.line(100, y, 500, y)
            y -= 15

            for rec in records:
                if y < 50:
                    p.showPage()
                    y = 750
                p.drawString(100, y, f"{rec.name} | {rec.equipment_type} | {rec.flowrate} | {rec.pressure} | {rec.temperature}")
                y -= 15

            p.showPage()
            p.save()

            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
        except UploadHistory.DoesNotExist:
            return Response({"error": "History not found"}, status=status.HTTP_404_NOT_FOUND)
