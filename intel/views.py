from django.shortcuts import render
from datetime import datetime
from .models import StructureIntel, StructureIntelCampaign, StructureTimer
from .forms import StructureForm, StructureTimerForm, StructureTimerPasteForm
from esi.clients import EsiClientProvider
from django.contrib import messages
from django.shortcuts import redirect
from fleets.authorization import required_roles
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import IntegrityError


esi = EsiClientProvider()

structure_type_ids = {
    "astrahus": 35832,
    "fortizar": 35833,
    "keepstar": 35834,
    "raitaru": 35825,
    "azbel": 35826,
    "sotiyo": 35827,
    "athanor": 35835,
    "tatara": 35836,
    "ansiblex": 35841,
    "pharolux": 35840,
}

@login_required
def view_structure_campaign(request, campaign_id):
    campaign = StructureIntelCampaign.objects.get(id=campaign_id)
    return render(request, 'intel/view_structure_campaign.html', {'campaign': campaign})

@login_required
def list_structure_campaigns(request):
    campaigns = StructureIntelCampaign.objects.all()
    return render(request, 'intel/list_structure_campaigns.html', {'campaigns': campaigns})

@login_required
def view_structure(request, structure_id):
    structure = StructureIntel.objects.get(id=structure_id)
    return render(request, 'intel/view_structure.html', {'structure': structure})

@login_required
def list_structures(request):
    structures = StructureIntel.objects.all()
    return render(request, 'intel/list_structures.html', {'structures': structures, 'campaigns': StructureIntelCampaign.objects.filter(status="active")})

@login_required
def delete_structure(request, structure_id):
    structure = StructureIntel.objects.get(id=structure_id)
    structure.delete()
    return redirect('list-structures')

@login_required
def create_structure(request):
    if request.method == 'POST':
        form = StructureForm(request.POST)
        if form.is_valid():
            structure = StructureIntel(
                structure_name = form.cleaned_data['structure_name'],
                structure_type = form.cleaned_data['structure_type'],
                system = form.cleaned_data['system'],
                corporation_name = form.cleaned_data['corporation_name'],
                alliance_name = form.cleaned_data['alliance_name'],
                related_alliance_name = form.cleaned_data['related_alliance_name'],
                timer = form.cleaned_data['timer'],
                fitting = form.cleaned_data['fitting'],
            )

            structure.structure_type_id = structure_type_ids[structure.structure_type]
            structure.created_by_character_id = request.user.eve_character.character_id
            structure.created_by_character_name = request.user.eve_character.character_name
            
            try: 
                names_to_resolve = set() 
                names_to_resolve.add(structure.corporation_name)
                names_to_resolve.add(structure.system)
                if structure.alliance_name:
                    names_to_resolve.add(structure.alliance_name)
                if structure.related_alliance_name:
                    names_to_resolve.add(structure.related_alliance_name)
                resolved_ids = esi.client.Universe.post_universe_ids(names=list(names_to_resolve)).results()
                for id in resolved_ids['corporations']:
                    if id['name'] == structure.corporation_name:
                        structure.corporation_id = id['id']
                
                if resolved_ids['alliances']:
                    for id in resolved_ids['alliances']:
                        if structure.alliance_name and id['name'] == structure.alliance_name:
                            structure.alliance_id = id['id']
                        if structure.related_alliance_name and id['name'] == structure.related_alliance_name:
                            structure.related_alliance_id = id['id']

                for id in resolved_ids['systems']:
                    if id['name'] == structure.system:
                        structure.system_id = id['id']
                        # fetch constellation id from esi 
                        structure.constellation_id = esi.client.Universe.get_universe_systems_system_id(system_id=id['id']).results()['constellation_id']
                        structure.constellation = esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=structure.constellation_id).results()['name']
                        # fetch region id from esi
                        structure.region_id = esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=structure.constellation_id).results()['region_id']
                        structure.region = esi.client.Universe.get_universe_regions_region_id(region_id=structure.region_id).results()['name']

            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, 'Failed to resolve corporation name, alliance name, or related alliance name')
                return render(request, 'intel/create_structure.html', {'form': form})
        
            try:
                structure.save()
            except IntegrityError as e:
                messages.add_message(request, messages.ERROR, e)
                return render(request, 'intel/create_structure.html', {'form': form})
            
            # register campaign if it exists
            query = Q(status='active') & (Q(system=structure.system) | Q(constellation=structure.constellation) | Q(region=structure.region) | Q(alliance_name=structure.alliance_name) | Q(related_alliance_name=structure.related_alliance_name) | Q(corporation_name=structure.corporation_name))
            if StructureIntelCampaign.objects.filter(query).exists():
                campaign = StructureIntelCampaign.objects.get(query)
                campaign.structures.add(structure)
                campaign.save() 

            return redirect('list-structures')
    else:
        form = StructureForm()
    return render(request, 'intel/create_structure.html', {'form': form})

@login_required
def list_timers(request):
    timers = StructureTimer.objects.filter(Q(timer__gte=datetime.now())).order_by('timer').all()
    return render(request, 'intel/list_timers.html', {'timers': timers})

def resolve_timer_names(timer):
    names_to_resolve = set()
    names_to_resolve.add(timer.system)
    names_to_resolve.add(timer.alliance_name)
    resolved_ids = esi.client.Universe.post_universe_ids(names=list(names_to_resolve)).results()

    if resolved_ids['alliances']:
        for id in resolved_ids['alliances']:
            if id['name'] == timer.alliance_name:
                timer.alliance_id = id['id']
    if not timer.alliance_id:
        raise Exception('Failed to resolve alliance name')

    for id in resolved_ids['systems']:
        if id['name'] == timer.system:
            timer.system_id = id['id']
            # fetch constellation id from esi
            timer.constellation_id = esi.client.Universe.get_universe_systems_system_id(system_id=id['id']).results()['constellation_id']
            timer.constellation = esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=timer.constellation_id).results()['name']
            # fetch region id from esi
            timer.region_id = esi.client.Universe.get_universe_constellations_constellation_id(constellation_id=timer.constellation_id).results()['region_id']
            timer.region = esi.client.Universe.get_universe_regions_region_id(region_id=timer.region_id).results()['name']

@login_required
def create_timer(request):
    if request.method == 'POST':
        form = StructureTimerForm(request.POST)
        if form.is_valid():
            timer = StructureTimer(
                structure_name = form.cleaned_data['structure_name'],
                structure_type = form.cleaned_data['structure_type'],
                system = form.cleaned_data['system'],
                alliance_name = form.cleaned_data['alliance'],
                timer_type = form.cleaned_data['timer_type'],
                timer = form.cleaned_data['timer'],
            )

            timer.structure_type_id = structure_type_ids[timer.structure_type]
            timer.created_by_character_id = request.user.eve_character.character_id
            timer.created_by_character_name = request.user.eve_character.character_name

            try:
                resolve_timer_names(timer)
            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, 'Failed to resolve alliance name or system')
                return render(request, 'intel/create_structure.html', {'form': form})

            timer.save()

            return redirect('list-timers')
    else:
        form = StructureTimerForm()
    return render(request, 'intel/create_timer.html', {'form': form})

def parse_paste(paste):
    [first, _, third] = paste.splitlines()
    [system, structure_name] = first.split(' - ')
    [_, timer] = third.split(' until ')
    timer = datetime.strptime(timer, '%Y.%m.%d %H:%M:%S')
    return StructureTimer(
        system = system,
        structure_name = structure_name,
        timer = timer,
    )

@login_required
def paste_timer(request):
    if request.method == 'POST':
        form = StructureTimerPasteForm(request.POST)
        if form.is_valid():
            paste = form.cleaned_data['paste']
            try:
                timer = parse_paste(paste)
            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, 'Failed to parse paste')
                return render(request, 'intel/create_timer_paste.html', {'form': form})

            timer.structure_type = form.cleaned_data['structure_type']
            timer.timer_type = form.cleaned_data['timer_type']
            timer.alliance_name = form.cleaned_data['alliance']

            try:
                resolve_timer_names(timer)
            except Exception as e:
                print(e)
                messages.add_message(request, messages.ERROR, 'Failed to resolve alliance name or system')
                return render(request, 'intel/create_timer_paste.html', {'form': form})

            timer.structure_type_id = structure_type_ids[timer.structure_type]
            timer.created_by_character_id = request.user.eve_character.character_id
            timer.created_by_character_name = request.user.eve_character.character_name

            timer.save()

            return redirect('list-timers')
    else:
        form = StructureTimerPasteForm()
    return render(request, 'intel/create_timer_paste.html', {'form': form})
