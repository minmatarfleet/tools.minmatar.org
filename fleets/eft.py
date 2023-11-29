import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

from eveuniverse.models import EveEntity, EveType, EveMarketGroup

# from fleets.models import EveFitting

OFFLINE_SUFFIX = "/OFFLINE"
NAME_CHARS = "[^,/\[\]]"  # Characters which are allowed to be used in name
HULL_RE = re.compile("\[(?P<hull>.+),(?P<name>.+)\]")
MODULE_RE = re.compile(f"^(?P<type_name>{NAME_CHARS}+?)(,\s*(?P<charge_name>{NAME_CHARS}+?))?(?P<offline>\s*{OFFLINE_SUFFIX})?(\s*\[(?P<mutation>\d+?)\])?$")
DRONE_CARGO_RE = re.compile(f"^(?P<type_name>{NAME_CHARS}+?) x(?P<amount>\d+?)(\s*\[(?P<mutation>\d+?)\])?$")

MARKET_GROUP_MODULES_ID=9
MARKET_GROUP_RIGS_ID=955
MARKET_GROUP_DRONES_ID=157

@dataclass
class EftItem:
    name: str
    in_cargo: bool
    amount: int
    eve_type: Optional[EveType] = None

    def __str__(self) -> str:
        return f"{self.name} x{self.amount}"

@dataclass
class EftFit:
    name: str
    hull: str
    modules: list[EftItem] = field(default_factory=list)
    rigs: list[EftItem] = field(default_factory=list)
    drones: list[EftItem] = field(default_factory=list)
    cargo: list[EftItem] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.hull}, {self.name}]"

    def sections(self):
        return [
            ("modules", self.modules), 
            ("rigs", self.rigs), 
            ("drones", self.drones), 
            ("cargo", self.cargo)
        ]
    
    def section_names():
        return ["modules", "rigs", "drones", "cargo"]

    def from_items(name: str, hull: str, items: Iterable[EftItem]):
        items = {i.name: i for i in items}
        entities = fetch_by_names(items.keys())
        eve_types = EveType.objects.bulk_get_or_create_esi(
                    ids=[entity.id for entity in entities],
                    enabled_sections=[EveType.Section.MARKET_GROUPS],
                )

        fit = EftFit(name=name, hull=hull)
        for eve_type in eve_types:
            item: EftItem = items[eve_type.name]
            item.eve_type = eve_type

            market_group = resolve_top_market_group(eve_type.eve_market_group)
            if market_group.id == MARKET_GROUP_MODULES_ID:
                if item.in_cargo:
                    fit.cargo.append(item)
                else:
                    fit.modules.append(item)
            elif market_group.id == MARKET_GROUP_RIGS_ID:
                fit.rigs.append(item)
            elif market_group.id == MARKET_GROUP_DRONES_ID:
                fit.drones.append(item)
            else:
                fit.cargo.append(item)
        
        return fit

def fetch_by_names(names: Iterable[str]):
    names = set(names)
    query = EveEntity.objects.fetch_by_names_esi(names=names).filter(category=EveEntity.CATEGORY_INVENTORY_TYPE)
    if query.count() < len(names):
        query = EveEntity.objects.fetch_by_names_esi(names=names, update=True).filter(category=EveEntity.CATEGORY_INVENTORY_TYPE)
    return query

def resolve_top_market_group(market_group: EveMarketGroup) -> EveMarketGroup:
    while market_group.parent_market_group is not None:
        market_group = market_group.parent_market_group
    return market_group

def parse_eft(eft_format: str) -> EftFit:
    def parse_line(line: str):
        line = line.strip()
        if len(line) == 0 or line.startswith("["):
            return False
        if m := DRONE_CARGO_RE.match(line):
            return EftItem(m.group("type_name"), in_cargo=True, amount=int(m.group("amount")))
        if m := MODULE_RE.match(line):
            return EftItem(m.group("type_name"), in_cargo=False, amount=1)
        return False
    
    lines = eft_format.splitlines()

    if m := HULL_RE.match(lines.pop(0)):
        name = m.group("name").strip()
        hull = m.group("hull").strip()
    else:
        return None

    parsed_items = filter(bool, map(parse_line, eft_format.splitlines()))
    items = {}
    for item in parsed_items:
        if found := items.get((item.name, item.in_cargo)):
            found.amount += item.amount
        else:
            items[(item.name, item.in_cargo)] = item
    
    return EftFit.from_items(name, hull, items.values())
