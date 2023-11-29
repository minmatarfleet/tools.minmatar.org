from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import FreightCalculatorForm
from .models import FreightRoute
from logistics.helpers import get_current_statistics
from pydantic import BaseModel

isotope_price = 675
base_isk_m3 = 150
midpoint_isk_m3 = 100
collateral_modifier = 0.01
high_collateral_modifier = 0.025

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


def freight_calculator(request):
    return redirect('standard_freight')
    result = None
    info = None
    values = None
    if request.method == 'POST':
        form = FreightCalculatorForm(request.POST)
        if form.is_valid():
            # convert to ints 
            form.cleaned_data['m3'] = int(form.cleaned_data['m3'])
            form.cleaned_data['collateral'] = int(form.cleaned_data['collateral'])
            
            route = FreightRoute.objects.get(pk=form.cleaned_data['route'].pk)
            # Fuel reward
            isotope_per_m3 = route.isotopes / 335000
            fuel_isk_m3 = isotope_per_m3 * isotope_price
            fuel_reward = form.cleaned_data['m3'] * fuel_isk_m3
            # ISK / m3
            base_isk_m3_reward = form.cleaned_data['m3'] * base_isk_m3
            additional_isk_m3_reward = form.cleaned_data['m3'] * \
                (midpoint_isk_m3 * route.midpoints)
            # Collateral
            current_collateral_modifier = collateral_modifier
            if form.cleaned_data['collateral'] > 1000000000:
                current_collateral_modifier = high_collateral_modifier
            collateral_reward = form.cleaned_data['collateral'] * \
                current_collateral_modifier
            # Total reward
            total_cost = fuel_reward + base_isk_m3_reward + \
                additional_isk_m3_reward + collateral_reward
            # Create calculator result
            result = FreightCalculatorResult(
                reward=total_cost,
                corporation=corporation,
                collateral=form.cleaned_data['collateral'],
                start=route.origin,
                end=route.destination
            )
            # Create 'how was this calculated' info
            info = FreightCalculatorInfo(route_isotopes=route.isotopes,
                                         midpoints=route.midpoints,
                                         midpoint_isk_m3=midpoint_isk_m3,
                                         isotope_price=isotope_price,
                                         isotope_per_m3=isotope_per_m3,
                                         isk_m3_modifier=base_isk_m3,
                                         collateral_modifier=current_collateral_modifier
                                         )
            # Values
            values = FreightCalculatedValues(fuel_reward=fuel_reward,
                                             base_isk_m3_reward=base_isk_m3_reward,
                                             additional_isk_m3_reward=additional_isk_m3_reward,
                                             collateral_reward=collateral_reward,
                                             total_cost=total_cost
                                             ).dict
    else:
        form = FreightCalculatorForm()

    return render(request, 'calculators/freight_calculator.html', {'form': form, 'result': result, 'info': info, 'values': values, 'current_statistics': get_current_statistics()})
