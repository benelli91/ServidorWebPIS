from tlc.models import Travel, City, Currency
from datetime import date, datetime, timedelta
from django.db.models import Q, F
import time


start_time = datetime.now()
# print ''
# Buses = 3
def load_exchanges():
    #loads exchanges from database
    base = Currency.objects.filter(base = True).first()
    cotizaciones = [(c.cod,c.divisor) for c in Currency.objects.all() if c.cod != base.cod ]
    cotizaciones = dict(cotizaciones)
    return cotizaciones
# print 'entra1'
cotizaciones = load_exchanges()
travels_id_to_keep = []

cities = City.objects.all()

min_travel_date = list(Travel.objects.all().order_by('departure')[:1])
min_date = min_travel_date[0].departure
max_travel_date = list(Travel.objects.all().order_by('-departure')[:1])
max_date = max_travel_date[0].departure

for city in cities:
    travel_per_city = list(Travel.objects.filter(
        Q(origin_city=city) &
        Q(traveltype=3)).distinct('destination_city'))
    for t in travel_per_city:
        city2 = t.destination_city
        if city.id != city2.id:
            # print 'pair:' + city.name + ' - ' + city2.name
            # for travel_per_day in dates:
            #     aux_date = travel_per_day.departure.date()
            #     current_date = datetime(year=aux_date.year, month=aux_date.month, day=aux_date.day)
            current_date = min_date
            travels_for_period = []
            while current_date < max_date:
                travels_for_period = list(Travel.objects.filter(
                    Q(origin_city=city) &
                    Q(destination_city=city2) &
                    Q(traveltype=3) &
                    Q(departure__gte=current_date ) &
                    Q(departure__lt=current_date + timedelta(hours=4))
                ))
                if len(travels_for_period) > 0:
                    best_travel = travels_for_period[0]
                    if best_travel.currency != 'USD':
                        divider = cotizaciones[best_travel.currency]
                        best_travel.price = round(best_travel.price / divider,2)
                        best_travel.currency = 'USD'

                    for t in travels_for_period:
                        if t.currency != 'USD':
                            divider = cotizaciones[t.currency]
                            t.price = round(t.price / divider,2)
                            t.currency = 'USD'

                        if t.price < best_travel.price:
                            best_travel = t
                        elif (t.price == best_travel.price and
                            t.duration < best_travel.duration):
                            best_travel = t

                    travels_id_to_keep.append(best_travel.idtravel)
                    #print travels_id_to_keep
                current_date = current_date + timedelta(hours=4)
    # print 'to keep: '+ str(len(travels_id_to_keep))
# Vamo a borrar
Travel.objects.filter(~Q(pk__in=travels_id_to_keep) & Q(traveltype=3)).delete()

# print 'tiempo total:' , datetime.now() - start_time
# print 'empezo:' , start_time
# print 'termino:' , datetime.now()
