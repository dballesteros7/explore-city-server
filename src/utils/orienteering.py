from geocell import utils

class Place(object):
    def __init__(self, json_place):
        self.original_json = json_place
        self.latitude = float(json_place['geometry']['location']['lat'])
        self.longitude = float(json_place['geometry']['location']['lng'])
        self.value = int(json_place['value'])

class Solver(object):

    def __init__(self, places):
        self.places = places
        self.upper_limit = Solver.submodular_f(self.places)

    @classmethod
    def submodular_f(cls, path):
        path_set = set(path)
        return sum(place.value for place in path_set)

    def rg_pq(self, place_s, place_t, budget, x_set, iterations):
        if int(utils.distance(place_s, place_t)) > budget:
            return []
        path = [place_s, place_t]
        if iterations == 0:
            return path
        m = Solver.submodular_f(set(path) | x_set) - Solver.submodular_f(x_set)
        for place_v in self.places:
            for b1 in xrange(1, budget + 1):
                p1 = self.rg_pq(place_s, place_v, b1, x_set, iterations - 1)
                p2 = self.rg_pq(place_v, place_t, budget - b1, x_set | set(p1), iterations - 1)
                if not p1 or not p2:
                    continue
                p1.extend(p2[1:])
                candidate = Solver.submodular_f(set(p1) | x_set) - Solver.submodular_f(x_set)
                if candidate > m:
                    path = p1
                    m = candidate
        return path
    
    def find_min_b(self, place_s, place_t, budget_low, budget_high, x_set, iterations, a):
        if budget_low == budget_high:
            path_for_budget = self.rg_pq(place_s, place_t, budget_low, x_set, iterations)
            if Solver.submodular_f(path_for_budget) < a:
                return None
            else:
                return budget_low
        middle = (budget_high + budget_low)/2
        path_for_budget = self.rg_pq(place_s, place_t, middle, x_set, iterations)
        value = Solver.submodular_f(path_for_budget)
        if value >= a:
            result = self.find_min_b(place_s, place_t, budget_low, middle, x_set, iterations, a)
            if result is None:
                return middle
            else:
                return result
        else:
            return self.find_min_b(place_s, place_t, middle + 1, budget_high, x_set, iterations, a)
