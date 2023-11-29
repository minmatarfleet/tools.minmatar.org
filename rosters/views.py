from django.shortcuts import render, redirect
from esi.decorators import token_required
from .models import EveRoster
from pydantic import BaseModel

# Create your views here.
def list_rosters(request):
    rosters = EveRoster.objects.all()
    return render(request, 'rosters/list_rosters.html', {'rosters': rosters})

def view_roster(request, roster_id):
    roster = EveRoster.objects.get(pk=roster_id)
    return render(request, 'rosters/view_roster.html', {'roster': roster})

@token_required(scopes=['esi-corporations.read_corporation_membership.v1', 'esi-mail.send_mail.v1'], new=True)
def add_token(request, token):
    return redirect("rosters")