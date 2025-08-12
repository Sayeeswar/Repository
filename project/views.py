# from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Q
from app.models import HospitalVisit
from app.models import HospitalMaster





def about(request):
    # return HttpResponse("My About page.")
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
 
    return render(request,'home.html',context)