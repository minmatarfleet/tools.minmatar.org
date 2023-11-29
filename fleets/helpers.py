from eveuniverse.models import EveType, EveGroup


def type_id_to_group_name(type_id):
    eve_type, _ = EveType.objects.get_or_create_esi(id=type_id)
    eve_group, _ = EveGroup.objects.get_or_create_esi(id=eve_type.eve_group_id)
    return eve_group.name
