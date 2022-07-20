from abc import ABC, abstractmethod
from better_abc import ABCMeta, abstract_attribute
import uuid
import random
import string
from copy import deepcopy


def random_string(N):
    s = "".join(random.choices(string.ascii_uppercase + string.digits, k=N))
    return s


def generate_id_long():
    return random_string(5)


def generage_id_1char():
    list_of_possible_chars = string.printable[:68]
    random_char = random.choice(list_of_possible_chars)
    return random_char


class all_members_not_none:
    def get_member_names(self):
        member_names = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("_")
        ]
        print(member_names)
        return member_names

    def all_members_not_none(self):
        member_names = self.get_member_names()
        is_not_none_list = [
            getattr(self, member_name) != None for member_name in member_names
        ]

        return all(is_not_none_list)


class drivable(metaclass=ABCMeta):
    @abstract_attribute
    def vehicle():
        pass

    def is_free(self):
        return self.vehicle is None


class actor(metaclass=ABCMeta):
    @abstractmethod
    def step(self):
        pass


class linear_connection(metaclass=ABCMeta):
    @abstract_attribute
    def previous(self):
        pass

    @abstract_attribute
    def next(self):
        pass


class has_repr(metaclass=ABCMeta):
    @abstract_attribute
    def id(self):
        pass

    def __repr__(self):
        class_name = type(self).__name__
        return class_name + " with ID: " + self.id


class visual_representation_0d:
    @abstract_attribute
    def i(self):
        pass

    @abstract_attribute
    def j(self):
        pass


class roadlet(
    drivable,
    linear_connection,
    visual_representation_0d,
    all_members_not_none,
    has_repr,
):
    def __init__(self, previous=None, next=None, i=None, j=None) -> None:
        super().__init__()
        self.vehicle = None
        self.id = generate_id_long()
        self.previous = previous
        self.next = next
        self.i = i
        self.j = j


class junction(drivable, all_members_not_none, has_repr):
    def __init__(self, incomming=None, outgoing=None, i=None, j=None) -> None:
        super().__init__()
        self.vehicle = None
        self.id = generate_id_long()
        self.incomming = incomming
        self.outgoing = outgoing
        self.i = i
        self.j = j

    @property
    def next(self):
        if self.outgoing is not None:
            return random.choice(self.outgoing)
        else:
            return None

    def light_change(self):
        if len(self.incomming) > 1:
            roll = random.uniform(0, 1)
            assert False
        else:
            assert False
            return None


class source(visual_representation_0d, all_members_not_none, has_repr, drivable, actor):
    def __init__(self, next=None, i=None, j=None) -> None:
        super().__init__()
        self.vehicle = None
        self.id = generate_id_long()
        self.next = next
        self.i = i
        self.j = j
        self.threshold = 0.8

    def step(self):
        roll = random.uniform(0, 1)
        if roll > self.threshold and self.is_free():
            self.spawn()
            return self.vehicle
        else:
            return None

    def spawn(self):
        self.vehicle = vehicle(self)


class sink(visual_representation_0d, all_members_not_none, has_repr, drivable, actor):
    def __init__(self, previous=None, i=None, j=None) -> None:
        super().__init__()
        self.vehicle = None
        self.id = generate_id_long()
        self.previous = previous
        self.i = i
        self.j = j

    def step(self):
        if not self.is_free():
            vehicle_to_remove = deepcopy(self.vehicle)
            self.vehicle = None
            return vehicle_to_remove
        else:
            return None


class vehicle(actor, has_repr):
    def __init__(self, location) -> None:
        super().__init__()
        self.id_visual = generage_id_1char()
        self.id = self.create_id_strarting_with(self.id_visual)
        self.location = location
        self.location.vehicle = self

    def create_id_strarting_with(self, c):
        id_tmp = generate_id_long()
        id_tmp = list(id_tmp)[0] = c
        id = "".join(id_tmp)
        return id

    def step(self):
        next = self.location.next
        if next.is_free():
            self.location.vehicle = None
            self.location = next
            self.location.vehicle = self


if __name__ == "__main__":

    previous_dummy = "previous_dummy"
    next_dummy = "next_dummy"

    rl = roadlet(previous_dummy, next_dummy)
    print(rl)
