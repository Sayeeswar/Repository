from django.shortcuts import render
from .models import HospitalMaster, HospitalVisit
from django.db.models import Sum,Q
import json
from collections import defaultdict
def hospital_overview(request):
    hospitals = HospitalVisit.objects.values_list('hospital', flat=True).distinct()
    selected_hospital = request.GET.get('hospital', '').strip()
    selected_department = request.GET.get('departments', '').strip()

    context = {
        'hospitals': hospitals,
        'selected_hospital': selected_hospital,
        'selected_department': selected_department,
    }

    # Overall stats (when no hospital selected)
    if not selected_hospital:
        overall_qs = HospitalVisit.objects.all()
        context['total_discharges'] = overall_qs.filter(category__iexact='DISCHARGES').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_admissions'] = overall_qs.filter(category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_new'] = overall_qs.filter(subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_revisit'] = overall_qs.filter(subcatg__iexact='REVISIT').aggregate(total=Sum('thevalue'))['total'] or 0

        # Department comparison for chart
        dept_stats = (
            overall_qs.values('speciality')
            .annotate(total=Sum('thevalue'))
            .order_by('speciality')
        )
        context['dept_labels'] = [d['speciality'] for d in dept_stats]
        context['dept_values'] = [d['total'] for d in dept_stats]

    else:
        # Stats for selected hospital
        hospital_qs = HospitalVisit.objects.filter(hospital__iexact=selected_hospital)
        context['total_discharges'] = hospital_qs.filter(category__iexact='DISCHARGES').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_admissions'] = hospital_qs.filter(category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_new'] = hospital_qs.filter(subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
        context['total_revisit'] = hospital_qs.filter(subcatg__iexact='REVISIT').aggregate(total=Sum('thevalue'))['total'] or 0

        # List of departments
        departments = hospital_qs.values_list('speciality', flat=True).distinct()
        context['departments'] = departments

        # Department stats for each department
        department_stats = {}
        for dept in departments:
            outpatients = hospital_qs.filter(speciality__iexact=dept, subcatg__iexact='NEWVISIT').aggregate(total=Sum('thevalue'))['total'] or 0
            inpatients = hospital_qs.filter(speciality__iexact=dept, category__iexact='ADMISSIONS').aggregate(total=Sum('thevalue'))['total'] or 0
            department_stats[dept] = {
                'outpatients': outpatients,
                'inpatients': inpatients,
            }
        context['department_stats'] = department_stats

        # If a department is selected, show time series for charts
        if selected_department:
            dept_qs = hospital_qs.filter(speciality__iexact=selected_department)
            # Example: monthly stats for chart
            monthly_stats = (
                dept_qs.values('theyr', 'themnth')
                .annotate(
                    outpatients=Sum('thevalue', filter=Q(subcatg__iexact='NEWVISIT')),
                    inpatients=Sum('thevalue', filter=Q(category__iexact='ADMISSIONS'))
                )
                .order_by('theyr', 'themnth')
            )
            context['dept_time_labels'] = [f"{row['theyr']}-{row['themnth']}" for row in monthly_stats]
            context['dept_outpatients'] = [row['outpatients'] or 0 for row in monthly_stats]
            context['dept_inpatients'] = [row['inpatients'] or 0 for row in monthly_stats]
 
    return render(request,'hospital.html',context)
def visit_stats(request):
    hospital = request.GET.get('hospital', '').strip()
    speciality = request.GET.get('speciality', '').strip()
    year = request.GET.get('year', '').strip()

    if year:
        if speciality:
            data = HospitalVisit.objects.filter(
                hospital__icontains=hospital,
                theyr=year,
                speciality__icontains=speciality
            ).values('speciality', 'subcatg', 'thevalue', 'category')
        else:
            data = HospitalVisit.objects.filter(
                hospital__icontains=hospital,
                theyr=year
            ).values('speciality', 'subcatg', 'thevalue', 'category')
    else:
        if speciality:
            data = HospitalVisit.objects.filter(
                hospital__icontains=hospital,
                speciality__icontains=speciality
            ).values('speciality', 'subcatg', 'thevalue', 'category')
        else:
            data = HospitalVisit.objects.filter(
                hospital__icontains=hospital
            ).values('speciality', 'subcatg', 'thevalue', 'category')

    stats = {}
    for row in data:
        spec = row['speciality']
        subcatg = row['subcatg'].upper()
        catg = row['category'].upper()
        if spec not in stats:
            stats[spec] = {'NEWVISIT': 0, 'REVISIT': 0, 'DISCHARGES': 0, 'ADMISSIONS': 0}
        if subcatg == 'NEWVISIT':
            stats[spec]['NEWVISIT'] += row['thevalue']
        elif subcatg == 'REVISIT':
            stats[spec]['REVISIT'] += row['thevalue']
        elif catg == 'DISCHARGES':
            stats[spec]['DISCHARGES'] += row['thevalue']
        elif catg == 'ADMISSIONS':
            stats[spec]['ADMISSIONS'] += row['thevalue']

    labels = list(stats.keys())
    newvisit_counts = [stats[s]['NEWVISIT'] for s in labels]
    revisit_counts = [stats[s]['REVISIT'] for s in labels]
    discharges_counts = [stats[s]['DISCHARGES'] for s in labels]
    admissions_counts = [stats[s]['ADMISSIONS'] for s in labels]

    context = {
        'stats': stats.items(),
        'labels': json.dumps(labels),
        'newvisits': json.dumps(newvisit_counts),
        'revisits': json.dumps(revisit_counts),
        'discharges': json.dumps(discharges_counts),
        'admissions': json.dumps(admissions_counts),
        'hospital': hospital,
        'speciality': speciality,
        'year': year,
    }
    return render(request, 'visit_stats.html', context)

def hospitalFilter(request):
    hospitals = HospitalMaster.objects.values_list('hospital', flat=True).distinct()
    types = HospitalMaster.objects.values_list('category', flat=True).distinct()
    selected_hospital = request.GET.get('hospital', '').strip()
    selected_type = request.GET.get('type', '').strip()

    queryset = HospitalVisit.objects.all()

    if selected_hospital:
        queryset = queryset.filter(hospital=selected_hospital)

    if selected_type:
        matching_codes = HospitalMaster.objects.filter(category=selected_type).values_list('spltycode', flat=True)
        queryset = queryset.filter(spltycode__in=matching_codes)

    stats = queryset.values('speciality').annotate(total=Sum('thevalue')).order_by('speciality')

    return render(request, 'hospital_filter.html', {
        'hospitals': hospitals,
        'types': types,
        'selected_hospital': selected_hospital,
        'selected_type': selected_type,
        'stats': stats
    })
def hospital_profile(request, hospital_code):
    hospital_code = hospital_code.strip().upper()
    highlight = request.GET.get('highlight', '').strip()
    hospital_name = hospital_code

    monthly_data = (
        HospitalVisit.objects
        .filter(hospital__iexact=hospital_code)
        .values('theyr', 'themnth', 'speciality')
        .annotate(total=Sum('thevalue'))
        .order_by('theyr', 'themnth')
    )

    trend_data = defaultdict(lambda: defaultdict(int))
    specialities = set()
    months = set()

    for row in monthly_data:
        year = str(row['theyr'])
        month = str(row['themnth']).zfill(2)
        month_str = f"{year}-{month}"
        speciality = row['speciality']
        total = row['total']
        trend_data[speciality][month_str] = total
        specialities.add(speciality)
        months.add(month_str)

    months = sorted(months)
    specialities = sorted(specialities)

    chart_series = []
    for speciality in specialities:
        if speciality.lower() == highlight.lower():
            chart_series.append({
                'label': speciality,
                'data': [trend_data[speciality].get(month, 0) for month in months],
                'borderColor': '#FF0000',
                'borderWidth': 4,
                'pointRadius': 5,
                'tension': 0.3,
                'fill': False
            })
        else:
            chart_series.append({
                'label': speciality,
                'data': [trend_data[speciality].get(month, 0) for month in months],
                'borderColor': '#BBBBBB',
                'borderWidth': 1,
                'pointRadius': 2,
                'tension': 0.3,
                'fill': False
            })

    context = {
        'hospital': hospital_name,
        'months': json.dumps(months),
        'chart_data': json.dumps(chart_series),
    }

    return render(request, 'hospital_profile.html', context)

def hospital_report(request):
    hospitals = HospitalVisit.objects.values_list('hospital', flat=True).distinct()
    speciality = HospitalVisit.objects.values_list('speciality', flat=True).distinct()

    selected_hospital = request.GET.get('hospital', '').strip().upper()
    selected_speciality = request.GET.get('speciality', '').strip().upper()

    if not selected_hospital:
        return render(request, 'hopital_report.html', {
            'hospitals': hospitals,
            'speciality': speciality,
            'hospital': '',
        })

    if selected_hospital and selected_speciality:
        visits = HospitalVisit.objects.filter(
            hospital__iexact=selected_hospital,
            speciality__iexact=selected_speciality
        )
    elif selected_hospital:
        visits = HospitalVisit.objects.filter(
            hospital__iexact=selected_hospital
        )
    elif selected_speciality:
        visits = HospitalVisit.objects.filter(
            speciality__iexact=selected_speciality
        )
    else:
        visits = HospitalVisit.objects.none()  # fallback

    # Total number of patients
    total_patients = visits.aggregate(total=Sum('thevalue'))['total'] or 0

    # Department-wise totals
    dept_data = (
        visits.exclude(speciality__isnull=True)
        .values('speciality')
        .annotate(total_visits=Sum('thevalue'))
        .order_by('-total_visits')
    )
    dept_labels = [row['speciality'] for row in dept_data]
    dept_values = [row['total_visits'] for row in dept_data]

    # Category-wise totals
    category_data = (
        visits.exclude(category__isnull=True)
        .values('category')
        .annotate(total=Sum('thevalue'))
        .order_by('category')
    )
    category_labels = [row['category'] for row in category_data]
    category_values = [row['total'] for row in category_data]

    # Monthly trend data
    categories_to_track = ['NEWVISIT', 'REVISIT', 'DISCHARGES', 'ADMISSIONS']
    monthly_trends = defaultdict(lambda: {cat: 0 for cat in categories_to_track})

    trend_qs = visits.values('theyr', 'themnth', 'category', 'subcatg').annotate(total=Sum('thevalue'))
    for row in trend_qs:
        month = f"{row['theyr']}-{str(row['themnth']).zfill(2)}"
        cat = (row['subcatg'] or row['category'] or '').upper()
        if cat in categories_to_track:
            monthly_trends[month][cat] += row['total']

    sorted_months = sorted(monthly_trends.keys())
    category_series = {
        cat: [monthly_trends[month].get(cat, 0) for month in sorted_months]
        for cat in categories_to_track
    }

    context = {
        'hospitals': hospitals,
        'speciality': speciality,
        'hospital': selected_hospital,
        'dept_labels': json.dumps(dept_labels),
        'dept_values': json.dumps(dept_values),
        'category_labels': json.dumps(category_labels),
        'category_values': json.dumps(category_values),
        'months': json.dumps(sorted_months),
        'category_series': json.dumps(category_series),
        'total_patients': total_patients,
    }

    return render(request, 'hopital_report.html', context)



