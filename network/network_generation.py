import random
import time
import pandas as pd
from network.network_parts import roadlet, junction, source, sink


class network:

    # coordinate system
    # +----> j
    # |
    # V
    # i

    known_chars = [">", "<", "^", "v", "+", "s", "x", "."]

    def __init__(self, path):

        self.df_char = pd.read_csv(path, header=None)

        self.df = pd.DataFrame().reindex_like(self.df_char)
        self.df.iloc[:, :] = None

        self.ni = len(self.df_char)
        self.nj = len(self.df_char.columns)

        self.all_roadlets = []
        self.all_sources = []
        self.all_sinks = []
        self.all_junctions = []
        self.all_vehicles = {}
        self.load_network()
        self.establish_connections()

    def __repr__(self) -> str:
        df_with_cars = self.df_char.copy(deep=True)
        for v in self.all_vehicles.values():
            l = v.location
            df_with_cars.iloc[l.i, l.j] = v.id
        return df_with_cars.__repr__()

    def load_network(self):
        for i in range(self.ni):
            for j in range(self.nj):
                self.register_cell(i, j)

    def register_cell(self, i, j):
        c = self.df_char.iloc[i, j]
        assert c in self.known_chars
        if c in [">", "<", "^", "v"]:
            self.create_roadlet(i, j)
        elif c == "+":
            self.create_junction(i, j)
        elif c == "s":
            self.create_source(i, j)
        elif c == "x":
            self.create_sink(i, j)
        else:
            assert c == "."
            pass

    def create_roadlet(self, i, j):

        self.check_roadlet_position(i, j)
        new_roadlet = roadlet(previous=None, next=None, i=i, j=j)

        self.df.iloc[i, j] = new_roadlet
        self.all_roadlets.append(new_roadlet)

    def check_roadlet_position(self, i, j):
        out_of_bounds_error_string = (
            "roadlets are not supposed to cross the canvas boundary"
        )
        assert i > 0, out_of_bounds_error_string
        assert i < self.nj - 1, out_of_bounds_error_string
        assert j > 0, out_of_bounds_error_string
        assert j < self.ni - 1, out_of_bounds_error_string

    def create_junction(self, i, j):

        self.check_junction_position(i, j)

        new_junction = junction(incomming=None, outgoing=None, i=i, j=j)

        self.df.iloc[i, j] = new_junction
        self.all_junctions.append(new_junction)

    def check_junction_position(self, i, j):

        out_of_bounds_error_string = (
            "junctions are not supposed to border the canvas boundary"
        )
        assert i > 0, out_of_bounds_error_string
        assert i < self.nj - 1, out_of_bounds_error_string
        assert j > 0, out_of_bounds_error_string
        assert j < self.ni - 1, out_of_bounds_error_string

    def create_source(self, i, j):

        self.check_source_position(i, j)
        new_source = source(next=None, i=i, j=j)
        self.df.iloc[i, j] = new_source
        self.all_sources.append(new_source)

    def check_source_position(self, i, j):
        out_of_bounds_error_string = "sources are supposed to be on the canvas"
        assert i >= 0, out_of_bounds_error_string
        assert i <= self.nj - 1, out_of_bounds_error_string
        assert j >= 0, out_of_bounds_error_string
        assert j <= self.ni - 1, out_of_bounds_error_string

    def create_sink(self, i, j):

        self.check_sink_position(i, j)

        new_sink = sink(previous=None, i=i, j=j)
        self.df.iloc[i, j] = new_sink
        self.all_sinks.append(new_sink)

    def check_sink_position(self, i, j):

        out_of_bounds_error_string = "sinks are supposed to be on the canvas"
        assert i >= 0, out_of_bounds_error_string
        assert i <= self.nj - 1, out_of_bounds_error_string
        assert j >= 0, out_of_bounds_error_string
        assert j <= self.ni - 1, out_of_bounds_error_string

    def establish_connections(self):
        # the connection of junction depends on both others to be already established
        # the connection of sourcesinc depends on the roadlets to be already established
        # therefore the order matters.
        for establish_connection_function in [
            self.establish_roadlet_connection,
            self.establish_sourcesink_connection,
            self.establish_junction_connections,
        ]:
            for i in range(self.ni):
                for j in range(self.nj):
                    c = self.df_char.iloc[i, j]
                    establish_connection_function(c, i, j)

    def establish_roadlet_connection(self, c, i, j):

        if c not in ["<", ">", "^", "v"]:
            return

        self.check_roadlet_position(i, j)

        next_i, next_j = None, None
        previous_i, previous_j = None, None

        if c == "<":
            next_i, next_j = i, j - 1
            previous_i, previous_j = i, j + 1
        elif c == ">":
            next_i, next_j = i, j + 1
            previous_i, previous_j = i, j - 1
        elif c == "^":
            next_i, next_j = i - 1, j
            previous_i, previous_j = i + 1, j
        elif c == "v":
            next_i, next_j = i + 1, j
            previous_i, previous_j = i - 1, j
        else:
            raise Exception(f"No roadlet at ({i}, {j})")

        this_network_part = self.df.iloc[i, j]
        next_network_part = self.df.iloc[next_i, next_j]
        previous_network_part = self.df.iloc[previous_i, previous_j]

        assert next_network_part is not None
        assert previous_network_part is not None

        this_network_part.next = next_network_part
        this_network_part.previous = previous_network_part

    def establish_sourcesink_connection(self, c, i, j):

        if c not in ["s", "x"]:
            return

        neighbor = None
        neighbor_count = 0
        for di in [-1, 0, +1]:
            for dj in [-1, 0, +1]:
                ij_no_shift = di == 0 and dj == 0
                di_out_of_canvas = i + di < 0 or i + di >= self.ni
                dj_out_of_canvas = j + dj < 0 or j + dj >= self.nj
                if ij_no_shift or di_out_of_canvas or dj_out_of_canvas:
                    pass
                else:
                    there_is_a_neighbor = self.df.iloc[i + di, j + dj] is not None
                    if there_is_a_neighbor:
                        neighbor_count += 1
                        neighbor = self.df.iloc[i + di, j + dj]
        assert neighbor_count == 1

        is__source = c == "s"
        is_sink = c == "x"

        this_network_part = self.df.iloc[i, j]
        if is__source:
            self.check_source_position(i, j)
            assert neighbor.previous == this_network_part
            this_network_part.next = neighbor

        elif is_sink:
            self.check_sink_position(i, j)
            assert neighbor.next == this_network_part
            this_network_part.previous = neighbor

        else:
            raise Exception(f"Neither source not sink at ({i}, {j})")

    def establish_junction_connections(self, c, i, j):

        if c != "+":
            return

        self.check_junction_position(i, j)

        this_junction = self.df.iloc[i, j]
        this_junction.incomming, this_junction.outgoing = [], []
        neighbor_count = 0
        for di, dj in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
            di_out_of_canvas = i + di < 0 or i + di >= self.ni
            dj_out_of_canvas = j + dj < 0 or j + dj >= self.nj
            if di_out_of_canvas or dj_out_of_canvas:
                pass
            else:
                if i == 4 and j == 9:
                    print(i + di, j + dj)
                    there_is_a_neighbor = self.df.iloc[i + di, j + dj] is not None
                    print(there_is_a_neighbor)
                    print()
                there_is_a_neighbor = self.df.iloc[i + di, j + dj] is not None
                if there_is_a_neighbor:
                    neighbor_count += 1
                    neighbor = self.df.iloc[i + di, j + dj]
                    this_is_neighbors_next = neighbor.next == this_junction
                    this_is_neighbors_previous = neighbor.previous == this_junction
                    assert this_is_neighbors_next + this_is_neighbors_previous == 1
                    if this_is_neighbors_next:
                        this_junction.incomming.append(neighbor)
                    elif this_is_neighbors_previous:
                        this_junction.outgoing.append(neighbor)

        assert neighbor_count > 1 and neighbor_count <= 4
        n_incomming = len(this_junction.incomming)
        n_outgoing = len(this_junction.outgoing)
        assert n_incomming > 0 and n_incomming <= 2
        assert n_outgoing > 0 and n_outgoing <= 2

    def step(self):

        self.step_sources()
        self.step_sinks()
        self.step_vehicles()

    def step_vehicles(self):
        for vehicle in sorted(
            self.all_vehicles.values(), key=lambda _: random.random()
        ):
            vehicle.step()

    def step_sources(self):
        for s in self.all_sources:
            new_vehicle = s.step()
            if new_vehicle is not None:
                self.all_vehicles[new_vehicle.id] = new_vehicle

    def step_sinks(self):
        for x in self.all_sinks:
            vehicle_to_remove = x.step()
            if vehicle_to_remove is not None:
                assert vehicle_to_remove.id in self.all_vehicles.keys()
                self.all_vehicles.pop(vehicle_to_remove.id)
                assert vehicle_to_remove.id not in self.all_vehicles.keys()
                del vehicle_to_remove


if __name__ == "__main__":

    path = "network/network_test_13x12.csv"
    n = network(path)

    for t in range(100):
        n.step()
        print(n)
        print()
        time.sleep(0.2)

    print()
