from pydantic import BaseModel
from typing import List, Any
from contracts_v2.models import EveContractExpectation, EveContract
from fleets.models import EveFitting
from django.db.models import Sum
from django.db.models import Q

class ContractStatusRow(BaseModel):
    contract_title: str
    fitting: Any
    location: str 
    entities: str
    warning_level: int
    current_quantity: int 
    expected_quantity: int

class ContractStatusResponse(BaseModel):
    rows: List[ContractStatusRow]

def get_contract_summary(expectations: List[EveContractExpectation]):
    response = ContractStatusResponse(
        rows=[],
    )
    for expectation in expectations:
        outstanding_quantity = EveContract.objects.filter(fitting=expectation.fitting, status='outstanding').count()
        warning_level = 2 if outstanding_quantity < expectation.quantity * 0.1 else 1 if outstanding_quantity < expectation.quantity * 0.50 else 0
        row = ContractStatusRow(
            contract_title=expectation.fitting.name,
            fitting=expectation.fitting,
            location=expectation.location.friendly_location_name,
            entities=",".join([e.entity_name for e in expectation.entities.all()]),
            current_quantity=outstanding_quantity,
            expected_quantity=expectation.quantity,
            warning_level=warning_level
        )
        response.rows.append(row)

    return response


def get_contract_summary_by_fittings(fittings: List[EveFitting], alliance=True):
    alliance_id = 99011978
    fitting_ids = set()
    response = ContractStatusResponse(
        rows=[],
    )
    for fitting in fittings:
        if fitting.pk in fitting_ids:
            continue
        if alliance:
            outstanding_quantity = EveContract.objects.filter(fitting=fitting, status='outstanding', assignee_id=alliance_id).count()
        else:
            outstanding_quantity = EveContract.objects.filter(Q(fitting=fitting, status='outstanding') & ~Q(assignee_id=alliance_id)).count()
        warning_level = 2 if outstanding_quantity == 0 else 0
        row = ContractStatusRow(
            contract_title=fitting.name,
            fitting=fitting,
            location="",
            entities="",
            current_quantity=outstanding_quantity,
            expected_quantity=1,
            warning_level=warning_level
        )
        response.rows.append(row)
        fitting_ids.add(fitting.pk)
    return response