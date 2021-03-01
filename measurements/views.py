from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium

# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent="distance_proj")


    ip_ = get_ip_address(request)
    print(ip_)
    # ip = '72.14.192.0'
    ip = '103.99.217.215'
    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city, timeout=1000)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)
    print(pointA)

    pointB = (l_lat, l_lon) # Default values

    # initial folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)

    # location Marker
    folium.Marker([l_lat, l_lon], tooltip=city['city'], popup=city['city'],
                    icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = ""
        try:
            destination = geolocator.geocode(destination_)

            # destination coordinates
            d_lat = destination.latitude
            d_lon = destination.longitude
            pointB = (d_lat, d_lon) # Setting the values

            # distance calculation
            distance = round(geodesic(pointA, pointB).km, 2)

            # folium map modification
            m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))

            # destination Marker
            folium.Marker([d_lat, d_lon], tooltip=destination, popup=destination,
                            icon=folium.Icon(color='red')).add_to(m)

            folium.Marker([l_lat, l_lon], tooltip=city['city'], popup=city['city'],
                            icon=folium.Icon(color='purple')).add_to(m)

            # draw the line between location and destination
            line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
            m.add_child(line)

            print("Passed!")

        except:
            print("No City found! Error")

        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()

    context = {
        'location': city['city'],
        'destination': destination,
        'distance' : distance,
        'form': form,
        'map': m
    }

    return render(request, 'measurements/main.html', context)
