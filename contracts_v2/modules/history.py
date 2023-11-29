from pydantic import BaseModel
from typing import List 
from contracts_v2.models import EveContractExpectation, EveContract
from fleets.models import EveFitting
from django.db.models import Sum

class ContractHistoryRow(BaseModel):
    contract_title: str
    sold_quantity: int 
    revenue: float

class ContractHistoryResponse(BaseModel):
    rows: List[ContractHistoryRow]
    total_revenue: float
    estimated_profit: float

def get_contract_historical_summary(fittings: List[EveFitting]):
    response = ContractHistoryResponse(
        rows=[],
        total_revenue=0,
        estimated_profit=0
    )
    for fitting in fittings:
        contract_title = fitting.name
        sold_quantity = EveContract.objects.filter(fitting=fitting, status='finished').count()
        contract_price_sum = EveContract.objects.filter(fitting=fitting, status='finished').aggregate(Sum('price'))['price__sum']
        if not contract_price_sum:
            revenue = 0
        else:
            revenue = float(contract_price_sum)
        row = ContractHistoryRow(
            contract_title=contract_title,
            sold_quantity=sold_quantity,
            revenue=revenue
        )
        response.rows.append(row)
        response.total_revenue += round(revenue, 2)
        response.estimated_profit += round((revenue * 0.2), 2)

    return response