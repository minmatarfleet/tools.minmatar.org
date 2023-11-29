import re
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from .authorization import required_roles, character_id_has_roles
from .models import EveFleet, EveDoctrine, EveFitting, EveFleetDiscordNotification, EsiFleet, fleet_type_audience_lookup
from contracts_v2.models import EveContractLocation
from .forms import EveFleetForm, EveFleetEditForm
from .motd import get_motd
from fleets import eft, helpers
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from esi.clients import EsiClientProvider
from esi.decorators import token_required
from .tasks import update_esi_fleet_members

esi = EsiClientProvider()


# Create your views here.
def list_fleet(request):
    query = Q(start_time__gte=timezone.now() - timezone.timedelta(minutes=15))

    if request.user.is_anonymous:
        query = query & ~Q(audience='alliance')
        query = query & ~Q(audience='militia')
        messages.warning(request, 'Only public fleets are shown, you must be logged in to view additional fleets.')
    elif character_id_has_roles(request.user.eve_character.character_id, ['Alliance']):
        pass 
    elif character_id_has_roles(request.user.eve_character.character_id, ['Academy']):
        pass 
    else:
        query = query & ~Q(audience='alliance')
        messages.info(request, 'Some fleets are hidden, you must be in Minmatar Fleet Alliance to view them.')

    fleets = EveFleet.objects.filter(query).order_by('start_time')
    return render(request, 'fleets/fleet_list.html', {'fleets': fleets})

def list_fleet_history(request):
    fleets = EveFleet.objects.filter(start_time__lt=timezone.now()).order_by('-start_time')
    return render(request, 'fleets/fleet_list_history.html', {'fleets': fleets})

@login_required
@required_roles(roles=["Alliance"], redirect_url='list_fleet')
def create_fleet(request):
    eve_character = request.user.eve_character
    # guard types by roles
    allowed_types = (
        ('fun_fleet', 'Fun Fleet'),
        ('random', 'Random'),
        ('training', 'Training'),
    )
    if character_id_has_roles(eve_character.character_id, ['Frontline FC', 'FC']):
        allowed_types = allowed_types + (('frontline', 'Frontline'), ('battlefield', 'Battlefield'))

    if character_id_has_roles(eve_character.character_id, ['FC']):
        allowed_types = allowed_types + (('stratop', 'Stratop'), ('flash_form', 'Flash Form'))


    if request.method == 'POST':
        form = EveFleetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['type'] not in [t[0] for t in allowed_types]:
                messages.add_message(
                    request, 
                    messages.ERROR, 
                    'You are only authorized for the following fleet types: ' +  str([t[0] for t in allowed_types]),
                )
                return redirect('create_fleet')
            fleet = EveFleet(
                fleet_commander_id=eve_character.character_id,
                fleet_commander_name=eve_character.character_name,
                type=form.cleaned_data['type'],
                audience=fleet_type_audience_lookup[form.cleaned_data['type']],
                start_time=form.cleaned_data['start_time'],
                end_time=form.cleaned_data['end_time'],
                staging=EveContractLocation.objects.get(primary=True),
                doctrine=form.cleaned_data['doctrine'],
                description=form.cleaned_data['description'],
            )
            fleet.save()
            return redirect('list_fleet')
    
    form = EveFleetForm()
    form.fields['type'].choices = allowed_types
    return render(request, 'fleets/fleet_create.html', {'form': form})

def view_fleet(request, pk):
    is_fleet_commander = False
    fleet = EveFleet.objects.get(pk=pk)
    if not request.user.is_anonymous and fleet.fleet_commander_id == request.user.eve_character.character_id:
        is_fleet_commander = True
    if not request.user.is_anonymous and character_id_has_roles(request.user.eve_character.character_id, ['FC', 'Frontline FC']):
        is_fleet_commander = True
    return render(request, 'fleets/fleet_view.html', {'fleet': fleet, 'is_fleet_commander': is_fleet_commander})


def edit_fleet(request, pk):
    eve_character = request.user.eve_character
    fleet = EveFleet.objects.get(pk=pk)
    # must be fleet commander
    if fleet.fleet_commander_id != eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    if request.method == 'POST':
        form = EveFleetEditForm(request.POST)
        if form.is_valid():
            fleet.type=form.cleaned_data['type']
            fleet.audience=fleet_type_audience_lookup[form.cleaned_data['type']]
            fleet.start_time=form.cleaned_data['start_time']
            fleet.end_time=form.cleaned_data['end_time']
            fleet.staging=form.cleaned_data['staging']
            fleet.doctrine=form.cleaned_data['doctrine']
            fleet.description=form.cleaned_data['description']
            fleet.save()
            return redirect('fleet_detail', pk=pk)
    form = EveFleetEditForm(initial={'staging': fleet.staging, 'doctrine': fleet.doctrine, 'start_time': fleet.start_time, 'end_time': fleet.end_time, 'type': fleet.type, 'audience': fleet.audience})
    return render(request, 'fleets/fleet_edit.html', {'form': form})

def delete_fleet(request, pk):
    eve_character = request.user.eve_character
    fleet = EveFleet.objects.get(pk=pk)
    # must be fleet commander
    if fleet.fleet_commander_id != eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    fleet.delete()
    return redirect('list_fleet')

def preping_fleet(request, pk):
    eve_character = request.user.eve_character
    fleet = EveFleet.objects.get(pk=pk)
    # must be fleet commander
    if fleet.fleet_commander_id != eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)

    invalid_reason = fleet.invalid_for_preping_reason
    if invalid_reason:
        messages.add_message(request, messages.WARNING, invalid_reason)
        return redirect('fleet_detail', pk=pk)
    try:
        EveFleetDiscordNotification.objects.create(type='preping', fleet=fleet)
    except Exception as e:
        messages.add_message(request, messages.WARNING, "Error creating notification, it was most likely already sent.")
    return redirect('fleet_detail', pk=pk)

def ping_fleet(request, pk):
    eve_character = request.user.eve_character
    fleet = EveFleet.objects.get(pk=pk)
    # must be fleet commander
    if fleet.fleet_commander_id != eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    invalid_reason = fleet.invalid_for_ping_reason
    if invalid_reason:
        messages.add_message(request, messages.WARNING, invalid_reason)
        return redirect('fleet_detail', pk=pk)
    try:
        EveFleetDiscordNotification.objects.create(type='ping', fleet=fleet)
    except Exception as e:
        messages.add_message(request, messages.WARNING, "Error creating notification, it was most likely already sent.")
    return redirect('fleet_detail', pk=pk)

@login_required
@token_required(scopes=['esi-fleets.read_fleet.v1', 'esi-fleets.write_fleet.v1'])
def create_esi_fleet(request, token, pk):
    fleet = EveFleet.objects.get(pk=pk)
    if fleet.fleet_commander_id != request.user.eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    
    try:
        character_fleet = esi.client.Fleets.get_characters_character_id_fleet(character_id=request.user.eve_character.character_id, token=token.valid_access_token()).results()
    except Exception as e:
        messages.add_message(request, messages.ERROR, f"Failed to sync fleet: {e}" )
        return redirect('fleet_detail', pk=pk)

    character_fleet_information = esi.client.Fleets.get_fleets_fleet_id(fleet_id=character_fleet['fleet_id'], token=token.valid_access_token()).results()
    EsiFleet.objects.create(
        id=character_fleet['fleet_id'],
        fleet=fleet,
        is_free_move=character_fleet_information['is_free_move'],
        is_registered=character_fleet_information['is_registered'],
        is_voice_enabled=character_fleet_information['is_voice_enabled'],
        motd=character_fleet_information['motd'],
    )

    fc_character_id = fleet.fleet_commander_id
    fc_character_name = fleet.fleet_commander_name
    station_id = fleet.staging.location_id
    station_name = fleet.staging.friendly_location_name
    discord_link = "https://discord.gg/minmatar"
    discord_name = "Minmatar Fleet Discord"
    if fleet.doctrine:
        doctrine_link = "https://tools.minmatar.org/fleets/doctrines/" + fleet.doctrine.slug
        doctrine_name = fleet.doctrine.name
    else:
        doctrine_link = "https://tools.minmatar.org/fleets/doctrines"
        doctrine_name = "TBD"

    motd = get_motd(fc_character_id, fc_character_name, station_id, station_name, discord_link, discord_name, doctrine_link, doctrine_name)

    esi.client.Fleets.put_fleets_fleet_id(
        fleet_id=character_fleet['fleet_id'], 
        new_settings = {
            "is_free_move": True,
            "motd": motd,
        },
        token=token.valid_access_token()
    ).results()

    messages.add_message(request, messages.INFO, 'Fleet is now being tracked through ESI and will stop when the fleet is closed.')
    return redirect('fleet_detail', pk=pk)

@login_required
def delete_esi_fleet(request, pk):
    fleet = EveFleet.objects.get(pk=pk)
    if fleet.fleet_commander_id != request.user.eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    
    try:
        fleet.esifleet.delete()
    except Exception as e:
        messages.add_message(request, messages.ERROR, f"Failed to delete fleet: {e}" )
        return redirect('fleet_detail', pk=pk)
    
    messages.add_message(request, messages.INFO, 'Fleet is no longer being tracked through ESI.')
    return redirect('fleet_detail', pk=pk)

@login_required
def refresh_esi_fleet_members(request, pk):
    fleet = EveFleet.objects.get(pk=pk)
    if fleet.fleet_commander_id != request.user.eve_character.character_id:
        messages.add_message(request, messages.ERROR, 'You are not the fleet commander')
        return redirect('fleet_detail', pk=pk)
    if not fleet.esifleet:
        messages.add_message(request, messages.ERROR, 'Fleet is not being tracked through ESI.')
        return redirect('fleet_detail', pk=pk)
    update_esi_fleet_members(fleet.esifleet.id)
    messages.add_message(request, messages.INFO, 'Fleet members were successfuly updated.')
    return redirect('fleet_detail', pk=pk)


def list_doctrines(request):
    primary_doctrines = EveDoctrine.objects.filter(primary=True, active=True, universal=False)
    secondary_doctrines = EveDoctrine.objects.filter(primary=False, active=True, universal=False)
    return render(request, 'fleets/doctrines.html', {'primary_doctrines': primary_doctrines, 'secondary_doctrines': secondary_doctrines})

def list_fittings(request):
    fittings = EveFitting.objects.all().order_by("name")
    fitting_type_re = re.compile("^\[(.*)\]")

    for fitting in fittings:
        match = fitting_type_re.match(fitting.name)
        if match:
            fitting.fitting_type = match.group(1)
        else:
            fitting.fitting_type = "Unknown"
    return render(request, 'fleets/fittings.html', {'fittings': fittings})

def view_fitting(request, fitting_slug):
    fitting = EveFitting.objects.get(slug=fitting_slug)
    return render(request, 'fleets/fitting.html', {'fitting': fitting})

def view_fitting_multibuy(request, fitting_slug):
    eft_fit = eft.parse_eft(EveFitting.objects.get(slug=fitting_slug).eft_format)
    fit = {
        "hull": eft_fit.hull,
        "name": eft_fit.name,
        "sections": [],
    }
    for section, items in eft_fit.sections():
        fit["sections"].append({"name": section, "items": [{"name": i.name, "amount": i.amount} for i in items]})
    
    return render(request, 'fleets/fitting_multibuy.html', {"fit": fit})

def view_doctrine(request, doctrine_slug):
    doctrine = EveDoctrine.objects.get(slug=doctrine_slug)
    universal_fittings = EveFitting.objects.filter(evedoctrine__universal=True)
    composition = doctrine.composition.split("\n")
    return render(request, 'fleets/doctrine.html', {'doctrine': doctrine, 'universal_fittings': universal_fittings, 'composition': composition})

def view_doctrine_fitting(request, doctrine_slug, fitting_slug):
    doctrine = EveDoctrine.objects.get(slug=doctrine_slug)
    fitting = EveFitting.objects.get(slug=fitting_slug)
    return render(request, 'fleets/fitting.html', {'doctrine': doctrine, 'fitting': fitting})

# cache for six hours
@cache_page(60 * 60 * 6)
def view_fittings_items(request):
    def get_names(items): return [i.eve_type.name for i in items]
    def get_all_names(fits, section): return [get_names(getattr(fit, section)) for fit in fits]
    fits = [eft.parse_eft(f.eft_format) for f in EveFitting.objects.all()]
    items = {
        section: sorted(set().union(*get_all_names(fits, section)), key=str.casefold)
        for section in eft.EftFit.section_names()
    }
    return render(request, 'fleets/fittings_items.html', {"items": items})
    
def mark_as_complete(request, alliance):
    if alliance == "fl33t":
        fittings = EveFitting.objects.filter(fl33t_updated=False)
        for fitting in fittings:
            fitting.fl33t_updated = True
            fitting.save()

    if alliance == "build":
        fittings = EveFitting.objects.filter(build_updated=False)
        for fitting in fittings:
            fitting.build_updated = True
            fitting.save()

    return redirect("/")
