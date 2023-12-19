from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import EveCourierEntity, EveCourierPilot, EsiCourierEntityResponse
from .helpers import get_historical_statistics, get_current_statistics
from esi.decorators import token_required

from .forms import StandardFreightCalculatorForm, WormholeCalculatorForm
from .models import FreightRoute
from pydantic import BaseModel


isotope_price = 675
base_isk_m3 = 150
midpoint_isk_m3 = 100
collateral_modifier = 0.01

corporation = 'Minmatar Fleet Logistics'


class FreightCalculatorResult(BaseModel):
    corporation: str
    reward: int
    collateral: int
    start: str
    end: str


class FreightCalculatedValues(BaseModel):
    fuel_reward: int
    base_isk_m3_reward: int
    additional_isk_m3_reward: int
    collateral_reward: int
    total_cost: int


class FreightCalculatorInfo(BaseModel):
    route_isotopes: int
    isotope_price: int
    isotope_per_m3: float
    isk_m3_modifier: int
    collateral_modifier: float
    midpoint_isk_m3: int
    midpoints: int
    

def index(request):
    courier_historical_statistics = get_historical_statistics()
    courier_current_statistics = get_current_statistics()
    print(courier_current_statistics)
    print(courier_historical_statistics)
    context = {
        'entities': EveCourierEntity.objects.all(),
        'courier_historical_statistics': courier_historical_statistics,
        'courier_current_statistics': courier_current_statistics
    }
    return render(request, 'logistics/index.html', context=context)

def standard_freight(request):
    result = None
    if request.method == 'POST':
        form = StandardFreightCalculatorForm(request.POST)
        if form.is_valid():
            # convert to ints 
            form.cleaned_data['collateral'] = int(form.cleaned_data['collateral'])
            
            route = FreightRoute.objects.get(pk=form.cleaned_data['route'].pk)
            # Base reward
            if form.cleaned_data['m3'] == 'small':
                base_reward = route.small_price
            elif form.cleaned_data['m3'] == 'medium':
                base_reward = route.medium_price
            elif form.cleaned_data['m3'] == 'large':
                base_reward = route.large_price
            
            # Collateral
            current_collateral_modifier = collateral_modifier
            if route.no_collateral:
                current_collateral_modifier = 0
            collateral_reward = form.cleaned_data['collateral'] * \
                current_collateral_modifier
            
            # Total reward
            total_cost = base_reward + collateral_reward

            # Create calculator result
            result = FreightCalculatorResult(
                reward=total_cost,
                corporation=corporation,
                collateral=form.cleaned_data['collateral'],
                start=route.origin,
                end=route.destination
            )
    else:
        form = StandardFreightCalculatorForm()
    return render(request, 'logistics/standard_freight.html', context={'form': form, 'result': result, 'current_statistics': get_current_statistics()})

def wormhole_freight(request):
    result = None
    if request.method == 'POST':
        form = WormholeCalculatorForm(request.POST)
        if form.is_valid():
            # convert to ints 
            form.cleaned_data['collateral'] = int(form.cleaned_data['collateral'])
            
            route = FreightRoute.objects.get(pk=form.cleaned_data['route'].pk)
            # Base reward
            if form.cleaned_data['m3'] == 'small':
                base_reward = route.small_price
            elif form.cleaned_data['m3'] == 'medium':
                base_reward = route.medium_price
            elif form.cleaned_data['m3'] == 'large':
                base_reward = route.large_price
            
            # Collateral
            current_collateral_modifier = collateral_modifier
            collateral_reward = form.cleaned_data['collateral'] * \
                current_collateral_modifier
            
            # Total reward
            total_cost = base_reward + collateral_reward

            # Create calculator result
            result = FreightCalculatorResult(
                reward=total_cost,
                corporation=corporation,
                collateral=form.cleaned_data['collateral'],
                start=route.origin,
                end=route.destination
            )
    else:
        form = WormholeCalculatorForm()

    return render(request, 'logistics/wormhole_freight.html', context={'form': form, 'result': result, 'current_statistics': get_current_statistics()})

@token_required(scopes=['esi-contracts.read_corporation_contracts.v1'], new=True)
def add_token(request, token):
    return redirect("/")