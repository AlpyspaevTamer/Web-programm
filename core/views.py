from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def calculator_view(request):
    return render(request, "calculator.html")

def plusmenos_view(request):
    return render(request, "plusmenos.html")

def generation_view(request):
    return render(request, "generation.html")

def equalization_view(request):
    return render(request, "equalization.html")

def themes_view(request):
    return render(request, 'themes.html')

def naturalnumber_view(request):
    return render(request, 'naturalnumber.html')

def arithmeticoperations_view(request):
    return render(request, 'arithmeticoperations.html')

def units_view(request):
    return render(request, 'units.html')

def geofigures_view(request):
    return render(request, 'geofigures.html')

def simpleequations_view(request):
    return render(request, 'simpleequations.html')

def multiplication_view(request):
    return render(request, 'multiplication.html')

def fractions_view(request):
    return render(request, 'fractions.html')

def percents_view(request):
    return render(request, 'percents.html')

def integers_view(request):
    return render(request, 'integers.html')

def inequalities_view(request):
    return render(request, 'inequalities.html')

def geometrybase_view(request):
    return render(request, 'geometrybase.html')

def area_view(request):
    return render(request, 'area.html')

def quadraticequations_view(request):
    return render(request, 'quadraticequations.html')

def systesmequations_view(request):
    return render(request, 'systesmequations.html')

def functions_view(request):
    return render(request, 'functions.html')

def pythagoras_view(request):
    return render(request, 'pythagoras.html')

def volume_view(request):
    return render(request, 'volume.html')

def statistics_view(request):
    return render(request, 'statistics.html')

def trygonometry_view(request):
    return render(request, 'trygonometry.html')

def derivative_view(request):
    return render(request, 'derivative.html')

def integrals_view(request):
    return render(request, 'integrals.html')

def logarithms_view(request):
    return render(request, 'logarithms.html')

def combinatorics_view(request):
    return render(request, 'combinatorics.html')

def economicsstatistics_view(request):
    return render(request, 'economicsstatistics.html')

def vectorscoordinates_view(request):
    return render(request, 'vectorscoordinates.html')