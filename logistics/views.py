from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import EveCourierEntity, EveCourierPilot, EsiCourierEntityResponse
from .helpers import get_historical_statistics, get_current_statistics
from esi.decorators import token_required

from calculators.forms import FreightCalculatorForm, StandardFreightCalculatorForm, JumpFreightCalculatorForm
from calculators.models import FreightRoute
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
    isk_per_jump = 500000
    result = None
    if request.method == 'POST':
        form = StandardFreightCalculatorForm(request.POST)
        if form.is_valid():
            # convert to ints 
            form.cleaned_data['m3'] = int(form.cleaned_data['m3'])
            form.cleaned_data['collateral'] = int(form.cleaned_data['collateral'])
            
            route = FreightRoute.objects.get(pk=form.cleaned_data['route'].pk)
            # Base reward
            base_reward = route.jumps * route.isk_jump
            # Collateral
            current_collateral_modifier = collateral_modifier
            collateral_reward = form.cleaned_data['collateral'] * \
                current_collateral_modifier
            # Add JF reward if JF capable and m3 > 12.5k
            # Why? Because they'll have to do a handoff.
            if route.jump_freight_required and form.cleaned_data['m3'] > 12500:
                base_reward += route.isk_m3 * form.cleaned_data['m3']
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

def jump_freight(request):
    result = None
    if request.method == 'POST':
        form = JumpFreightCalculatorForm(request.POST)
        if form.is_valid():
            # convert to ints 
            form.cleaned_data['m3'] = int(form.cleaned_data['m3'])
            form.cleaned_data['collateral'] = int(form.cleaned_data['collateral'])
            
            route = FreightRoute.objects.get(pk=form.cleaned_data['route'].pk)
            # Fuel reward
            base_reward = route.isk_m3 * form.cleaned_data['m3']
            # Collateral
            if route.low_risk:
                collateral_reward = 0
            else:
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
        form = JumpFreightCalculatorForm()

    return render(request, 'logistics/jump_freight.html', context={'form': form, 'result': result, 'current_statistics': get_current_statistics()})

@token_required(scopes=['esi-contracts.read_corporation_contracts.v1'], new=True)
def add_token(request, token):
    return redirect("/")