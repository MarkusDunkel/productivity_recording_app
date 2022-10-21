from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import datetime as dt
import calendar as c
import json

from zerf.models import Entry, Group

@csrf_exempt
def redirect_view(request):
    curr_date = dt.datetime.now().strftime('%d.%m.%Y')
    response = redirect(curr_date)
    return response

@csrf_exempt
def index(request, in_date):
    
    sel_date = dt.datetime.strptime(in_date, "%d.%m.%Y")
    curr_date = dt.datetime.now()
    d = []
    for i in range(c.monthrange(sel_date.year, sel_date.month)[1]):
        d.append(dt.date(sel_date.year, sel_date.month, i+1))
    
    entries =  Entry.objects.all()
    start_time = []
    end_time = []
    date_entries = []
    time_diff = []
    for e in entries:
        start_time.append(e.start_time)
        end_time.append(e.end_time)
        time_diff.append(dt.datetime.combine(dt.date.today(), e.end_time) - 
            dt.datetime.combine(dt.date.today(), e.start_time) )
        date_entries.append(e.date)

    time_agg = []
    time_agg_int = []
    day_num = []
    month_num = d[0].month
    month_name = tuple(['January', 'February', 'March', 'April', 'Mai', 'June', 'Juli', 'August', 'September', 'October', 'November', 'December'])[month_num-1]
    month_str = str(month_num + 100)[-2:]
    year_num = d[0].year
    for date in d:
        time_agg.append(dt.timedelta(hours=0))
        day_num.append(date.day)
        for i in range(len(date_entries)):
            if date == date_entries[i]:
                time_agg[-1] += time_diff[i]
        time_agg_int.append(time_agg[-1].total_seconds())
        time_agg_str = str(time_agg[-1])[:-3]
        if len(time_agg_str) == 4:
            time_agg_str = '0'+time_agg_str
        time_agg[-1] = time_agg_str
 
    time_agg_max = max(time_agg_int)
    for i in range(len(time_agg_int)):
        if time_agg_int[i] > 0:
            time_agg_int[i] /= time_agg_max
        time_agg_int[i] = int (time_agg_int[i] * 10)

    # calculate number of days between the 1. and the last monday before
    first_weekd = d[0].weekday()

    time_agg = json.dumps (time_agg)
    time_agg_int = json.dumps (time_agg_int)
    day_num = json.dumps (day_num)
    context = {'curr_date': curr_date.strftime('%d.%m.%Y'), 'date': in_date, 'year_num': year_num, 'month_name': month_name, 'month_str': month_str, 'time_agg': time_agg, 'time_agg_int': time_agg_int, 'day_num': day_num, 'first_weekd': first_weekd}

    return render(request, 'zerf/index.html', context)

@csrf_exempt
def add_entry(request, in_date):

    in_date = dt.datetime.strptime(in_date, "%d.%m.%Y").date()
    curr_date = dt.datetime.now()
    sel_month = in_date.month
    sel_year = in_date.year
    day_max = c.monthrange(sel_year, sel_month)[-1]
    if sel_month > 1:
      day_max_prev_month = c.monthrange(sel_year, sel_month-1)[-1]
    else:
      day_max_prev_month = c.monthrange(sel_year-1, 12)[-1]
    
    if request.method == 'POST':
        id_val = tuple( request.POST.getlist('id') )
        starttime_val = request.POST.getlist('stname[]')
        endtime_val = request.POST.getlist('etname[]')
        group_val = request.POST.getlist('grname[]')
        desc_val = request.POST.getlist('descname[]')
        del_val = request.POST.getlist('delname[]')
        
        for i in range(len(starttime_val)):
            if id_val[i] == 'new' and del_val[i] != '1':
                b = Entry(date = in_date, start_time = starttime_val[i], end_time = endtime_val[i], 
                    group = Group.objects.get(task_group_name=group_val[i]), description = desc_val[i])
                b.save()
            elif id_val[i] != 'new':
                b = Entry.objects.get(id=id_val[i])
                setattr(b, 'start_time', starttime_val[i])
                setattr(b, 'end_time', endtime_val[i])
                setattr(b, 'group', Group.objects.get(task_group_name=group_val[i]))
                setattr(b, 'description', desc_val[i])
                b.save()
            if del_val[i] == '1' and id_val[i] != 'new':
                b = Entry.objects.get(id=id_val[i])
                b.delete()
                
    group_names = Group.objects.values_list('task_group_name', flat = True)
    
    ids_name = list(Entry.objects.filter(date=in_date).values_list('id', flat = True))
    start_name = list(Entry.objects.filter(date=in_date).values_list('start_time', flat = True))
    end_name = list(Entry.objects.filter(date=in_date).values_list('end_time', flat = True))
    group_name = list(Entry.objects.filter(date=in_date).values_list('group', flat = True))
    desc_name = list(Entry.objects.filter(date=in_date).values_list('description', flat = True))
    stock_len = len(start_name)
    
    for i in range(stock_len):
        start_name[i] = start_name[i].strftime("%H:%M")
        end_name[i] = end_name[i].strftime("%H:%M")
        group_name[i] = getattr(Group.objects.get(id=group_name[i]),'task_group_name')
    
    ids_entries = json.dumps (ids_name)
    start_entries = json.dumps (start_name)
    end_entries = json.dumps (end_name)
    group_entries = json.dumps (group_name)
    desc_entries = json.dumps (desc_name)

    return render(request, 'zerf/add_entry.html', 
        {'curr_date': curr_date.strftime('%d.%m.%Y'), 'date': in_date.strftime('%d.%m.%Y'), 'group_names': group_names, 'stock_len': stock_len, 
            'ids_entries': ids_entries, 'start_entries': start_entries, 'end_entries': end_entries, 
            'group_entries': group_entries, 'desc_entries': desc_entries, 'day_max': day_max, 'day_max_prev_month': day_max_prev_month})