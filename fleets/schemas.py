from pydantic import BaseModel 
from typing import Optional

class FittingWheelResponse():
    """Fitting wheel response for the 'fitting_wheel.html' SVG template. Pretty verbose because of the SVG definition"""
    ship_id: int
    loSlot0_type_id: Optional[int]
    loSlot1_type_id: Optional[int]
    loSlot2_type_id: Optional[int]
    loSlot3_type_id: Optional[int]
    loSlot4_type_id: Optional[int]
    loSlot5_type_id: Optional[int]
    loSlot6_type_id: Optional[int]
    loSlot7_type_id: Optional[int]
    medSlot0_type_id: Optional[int]
    medSlot1_type_id: Optional[int]
    medSlot2_type_id: Optional[int]
    medSlot3_type_id: Optional[int]
    medSlot4_type_id: Optional[int]
    medSlot5_type_id: Optional[int]
    medSlot6_type_id: Optional[int]
    medSlot7_type_id: Optional[int]
    hiSlot0_type_id: Optional[int]
    hiSlot1_type_id: Optional[int]
    hiSlot2_type_id: Optional[int]
    hiSlot3_type_id: Optional[int]
    hiSlot4_type_id: Optional[int]
    hiSlot5_type_id: Optional[int]
    hiSlot6_type_id: Optional[int]
    hiSlot7_type_id: Optional[int]
    rigSlot0_type_id: Optional[int]
    rigSlot1_type_id: Optional[int]
    rigSlot2_type_id: Optional[int]
    subSystemSlot0_type_id: Optional[int]
    subSystemSlot1_type_id: Optional[int]
    subSystemSlot2_type_id: Optional[int]
    subSystemSlot3_type_id: Optional[int]
    subSystemSlot4_type_id: Optional[int]

    def __init__(self, ship_type_id, low_slots: list[int], med_slots=[], high_slots=[], rig_slots=[], subsystem_slots=[]):
        self.ship_id = ship_type_id
        # check if list contains element before assigning 
        self.loSlot0_type_id = low_slots[0] if len(low_slots) > 0 else None
        self.loSlot1_type_id = low_slots[1] if len(low_slots) > 1 else None
        self.loSlot2_type_id = low_slots[2] if len(low_slots) > 2 else None
        self.loSlot3_type_id = low_slots[3] if len(low_slots) > 3 else None
        self.loSlot4_type_id = low_slots[4] if len(low_slots) > 4 else None
        self.loSlot5_type_id = low_slots[5] if len(low_slots) > 5 else None
        self.loSlot6_type_id = low_slots[6] if len(low_slots) > 6 else None
        self.loSlot7_type_id = low_slots[7] if len(low_slots) > 7 else None
        self.medSlot0_type_id = med_slots[0] if len(med_slots) > 0 else None
        self.medSlot1_type_id = med_slots[1] if len(med_slots) > 1 else None
        self.medSlot2_type_id = med_slots[2] if len(med_slots) > 2 else None
        self.medSlot3_type_id = med_slots[3] if len(med_slots) > 3 else None
        self.medSlot4_type_id = med_slots[4] if len(med_slots) > 4 else None
        self.medSlot5_type_id = med_slots[5] if len(med_slots) > 5 else None
        self.medSlot6_type_id = med_slots[6] if len(med_slots) > 6 else None
        self.medSlot7_type_id = med_slots[7] if len(med_slots) > 7 else None
        self.hiSlot0_type_id = high_slots[0] if len(high_slots) > 0 else None
        self.hiSlot1_type_id = high_slots[1] if len(high_slots) > 1 else None
        self.hiSlot2_type_id = high_slots[2] if len(high_slots) > 2 else None
        self.hiSlot3_type_id = high_slots[3] if len(high_slots) > 3 else None
        self.hiSlot4_type_id = high_slots[4] if len(high_slots) > 4 else None
        self.hiSlot5_type_id = high_slots[5] if len(high_slots) > 5 else None
        self.hiSlot6_type_id = high_slots[6] if len(high_slots) > 6 else None
        self.hiSlot7_type_id = high_slots[7] if len(high_slots) > 7 else None
        self.rigSlot0_type_id = rig_slots[0] if len(rig_slots) > 0 else None
        self.rigSlot1_type_id = rig_slots[1] if len(rig_slots) > 1 else None
        self.rigSlot2_type_id = rig_slots[2] if len(rig_slots) > 2 else None
        self.subSystemSlot0_type_id = subsystem_slots[0] if len(subsystem_slots) > 0 else None
        self.subSystemSlot1_type_id = subsystem_slots[1] if len(subsystem_slots) > 1 else None
        self.subSystemSlot2_type_id = subsystem_slots[2] if len(subsystem_slots) > 2 else None
        self.subSystemSlot3_type_id = subsystem_slots[3] if len(subsystem_slots) > 3 else None
        self.subSystemSlot4_type_id = subsystem_slots[4] if len(subsystem_slots) > 4 else None