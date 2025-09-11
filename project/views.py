from django.shortcuts import render
from django.db.models import Sum, Q
from app.models import HospitalVisit, HospitalMaster
import json


def about(request):
    return render(request, 'about.html')


def hospital_overview1(request):
    hospitals = HospitalVisit.objects.values_list('hospital', flat=True).distinct()
    selected_hospital = request.GET.get('hospital', '').strip()
    selected_department = request.GET.get('departments', '').strip()

    context = {
        'hospitals': hospitals,
        'selected_hospital': selected_hospital,
        'selected_department': selected_department,
    }

    if not selected_hospital:
        # ===== Overall Stats =====
        overall_qs = HospitalVisit.objects.all()
        context['total_discharges'] = overall_qs.filter(category__iexact='DISCHARGES').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_admissions'] = overall_qs.filter(category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_new'] = overall_qs.filter(subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_revisit'] = overall_qs.filter(subcatg__iexact='REVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['totals'] = overall_qs.aggregate(total=Sum('thevalue'))['total'] or 0
        context['surgeries'] = overall_qs.filter(category__iexact='SURGERIES').count()

        # ===== Chart Data =====
        chart_stats = (
            overall_qs.values('theyr', 'themnth')
            .annotate(
                newvisits=Sum('thevalue', filter=Q(subcatg__iexact='NEWVISIT')),
                revisits=Sum('thevalue', filter=Q(subcatg__iexact='REVISIT')),
                discharges=Sum('thevalue', filter=Q(category__iexact='DISCHARGES')),
                admissions=Sum('thevalue', filter=Q(category__iexact='ADMISSIONS')),
            )
            .order_by('theyr', 'themnth')
        )

        labels = [f"{row['theyr']}-{row['themnth']}" for row in chart_stats]
        newvisits = [row['newvisits'] or 0 for row in chart_stats]
        revisits = [row['revisits'] or 0 for row in chart_stats]
        discharges = [row['discharges'] or 0 for row in chart_stats]
        admissions = [row['admissions'] or 0 for row in chart_stats]

        context.update({
            'labels': json.dumps(labels),
            'newvisits': json.dumps(newvisits),
            'revisits': json.dumps(revisits),
            'discharges': json.dumps(discharges),
            'admissions': json.dumps(admissions),
        })

        # ===== Dept Comparison =====
        dept_stats = (
            overall_qs.values('speciality')
            .annotate(total=Sum('thevalue'))
            .order_by('speciality')
        )
        dept_labels = [d['speciality'] for d in dept_stats]
        dept_values = [d['total'] or 0 for d in dept_stats]

        context['dept_labels'] = json.dumps(dept_labels)
        context['dept_values'] = json.dumps(dept_values)

    else:
        # ===== Stats for Selected Hospital =====
        hospital_qs = HospitalVisit.objects.filter(hospital__iexact=selected_hospital)
        context['total_discharges'] = hospital_qs.filter(category__iexact='DISCHARGES').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_admissions'] = hospital_qs.filter(category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_new'] = hospital_qs.filter(subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_revisit'] = hospital_qs.filter(subcatg__iexact='REVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['totals'] = hospital_qs.aggregate(total=Sum('thevalue'))['total'] or 0
        context['surgeries'] = hospital_qs.filter(category__iexact='SURGERIES').count()

        # ===== Chart Data =====
        chart_stats = (
            hospital_qs.values('theyr', 'themnth')
            .annotate(
                newvisits=Sum('thevalue', filter=Q(subcatg__iexact='NEWVISIT')),
                revisits=Sum('thevalue', filter=Q(subcatg__iexact='REVISIT')),
                discharges=Sum('thevalue', filter=Q(category__iexact='DISCHARGES')),
                admissions=Sum('thevalue', filter=Q(category__iexact='ADMISSIONS')),
            )
            .order_by('theyr', 'themnth')
        )

        labels = [f"{row['theyr']}-{row['themnth']}" for row in chart_stats]
        newvisits = [row['newvisits'] or 0 for row in chart_stats]
        revisits = [row['revisits'] or 0 for row in chart_stats]
        discharges = [row['discharges'] or 0 for row in chart_stats]
        admissions = [row['admissions'] or 0 for row in chart_stats]

        context.update({
            'labels': json.dumps(labels),
            'newvisits': json.dumps(newvisits),
            'revisits': json.dumps(revisits),
            'discharges': json.dumps(discharges),
            'admissions': json.dumps(admissions),
        })

        # ===== Departments =====
        departments = hospital_qs.values_list('speciality', flat=True).distinct()
        context['departments'] = departments

        # Stats per department
        department_stats = {}
        for dept in departments:
            outpatients = hospital_qs.filter(speciality__iexact=dept, subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
            inpatients = hospital_qs.filter(speciality__iexact=dept, category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
            department_stats[dept] = {
                'outpatients': outpatients,
                'inpatients': inpatients,
            }
        context['department_stats'] = department_stats

        # ===== Department Time-Series (if selected) =====
        if selected_department:
            dept_qs = hospital_qs.filter(speciality__iexact=selected_department)
            monthly_stats = (
                dept_qs.values('theyr', 'themnth')
                .annotate(
                    outpatients=Sum('thevalue', filter=Q(subcatg__iexact='NEWVISIT')),
                    inpatients=Sum('thevalue', filter=Q(category__iexact='ADMISSIONS'))
                )
                .order_by('theyr', 'themnth')
            )

            dept_time_labels = [f"{row['theyr']}-{row['themnth']}" for row in monthly_stats]
            dept_outpatients = [row['outpatients'] or 0 for row in monthly_stats]
            dept_inpatients = [row['inpatients'] or 0 for row in monthly_stats]

            context.update({
                'dept_time_labels': json.dumps(dept_time_labels),
                'dept_outpatients': json.dumps(dept_outpatients),
                'dept_inpatients': json.dumps(dept_inpatients),
                'surgeries': dept_qs.filter(category__iexact='SURGERIES').count(),
            })

    return render(request, 'home.html', context)
