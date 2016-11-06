from data_parsing.Planet import *
from data_parsing.Star import *
from data_parsing.System import *
from data_comparison.proposed_change import *


class Comparator():
    def __init__(self, obj1, obj2, origin):
        '''(PlanetaryObject, PlanetaryObject, str) -> NoneTye
        sets up the comparator with two objects of PlanetaryObject
        type of two objects must match
        str must be one of {"NASA archive", "exoplanet.eu"}

        raises ObjectTypeMismatchException is objects do not match
        returns NoneType
        '''

        if (type(obj1)) == (type(obj2)):
            self.obj1 = obj1
            self.obj2 = obj2
            self.working_type = type(obj1)
            self.origin = origin
        else:
            raise ObjectTypeMismatchException

    def sqlJoin(self, left_join):
        '''(bool) -> Dictionary
        works similar to joins in sql
        if input bool is true, a left join is performed
        if input bool is false, a right join is performed
        returns a Dictionary containing three keys,
        first with a list of field names
        the rest with lists of data values in the same order
        SQL join logic will determine what is included
        '''

        if (left_join):
            left_data = self.obj1.getData()
            right_data = self.obj2.getData()
        else:
            left_data = self.obj2.getData()
            right_data = self.obj1.getData()

        missing_keys = []
        result_dict = {'data': [], 'left': [], 'right': []}

        for key in left_data:
            if not (key in right_data):
                missing_keys.append(key)
            result_dict['data'].append(key)

        for key in result_dict['data']:
            result_dict['left'].append(left_data[key])
            if key in missing_keys:
                result_dict['right'].append("N/A")
            else:
                result_dict['right'].append(right_data[key])

        return result_dict

    def sqlJoinNewOnly(self, left_join):
        '''(bool) -> Dictionary
        Identical to method sqlJoin except excludes all rows
        which do not have a new or missing data field
        Returns dictionary structured in the same manner as sqlJoin
        '''
        raw_dict = self.sqlJoin(left_join)
        entry_count = len(raw_dict['data'])
        for i in range(0, entry_count):
            if ((raw_dict['right'] == "N/A") or (raw_dict['left'] == "N/A")):
                raw_dict['data'].pop(i)
                raw_dict['left'].pop(i)
                raw_dict['right'].pop(i)
        return raw_dict

    def innerJoinDiff(self):
        '''() -> Dictionary
        Selects fields akin to SQL inner join
        On selected fields, find differing field values
        Returns a dictionary with keys corresponding to any differing field
        values. The keys map to tuples of the values of (obj1, obj2).
        '''

        left_data = self.obj1.getData()
        right_data = self.obj2.getData()

        result_dict = {}

        for key in left_data:
            if key in right_data:
                if (isinstance(left_data[key], str) and isinstance(
                        right_data[key], str)):
                    if (left_data[key].lower() != right_data[key].lower()):
                        result_dict[key] = (left_data[key], right_data[key])
                elif (left_data[key] != right_data[key]):
                    result_dict[key] = (left_data[key], right_data[key])

        return result_dict

    def proposedChangeStarCompare(self):
        '''() -> list
        Similar to starCompare but returns a list of Addition
        and Modification Objects
        '''

        result_dict = []

        main_dictionary = self.starCompare()

        # return list of proposed changes of the planets in star
        for planet in main_dictionary["planetDC"]:
            for field in main_dictionary["planetDC"][planet]:
                result_dict.append(
                    Modification(self.origin,
                                 self.obj2.nameToPlanet[planet], field,
                                 main_dictionary["planetDC"][
                                     planet][field][0],
                                 main_dictionary["planetDC"][
                                     planet][field][1])
                )

        i = 0
        '''
        for data in main_dictionary["starN"]["right"]:
            if (data == "N/A"):
                i += 1
                result_dict.append(Addition(self.origin, None, None,
                main_dictionary["starN"]["data"][i],
                main_dictionary["starN"]["left"][i],
                main_dictionary["starN"]["right"][i]))
        '''
        return result_dict

    def starCompare(self):
        '''() -> Dictionary
        Comparison method for only stars
        Will find differing data for both the star and any planets
        attached to the system

        Returns a dictionary of dictionaries

        Main dictionary contains:
          starC: dict of mismatched/CHANGED star data
            keys: star fields
            generated by innerJoinDiff()
          starN: dict of NEW star data
            keys: star fields
            generated by sqlJoinNewOnly(True)
          planetN: dict of NEW planets
            keys: left, right
          planetDN: dict of NEW planet data
            keys: planet names
            generated by sqlJoinNewOnly(True)
          planetDC: dict of mismatched/CHANGED planet data
            keys: planet names
            generated by innerJoinDiff()

        Raises ObjectTypeIncompatibleException if objects are not
        stars
        '''

        if not (isinstance(self.obj1, Star)):
            # do not call this method for non-stars
            raise ObjectTypeIncompatibleException
        else:
            # starC
            starDataChange = self.innerJoinDiff()

            # starN
            starDataNew = self.sqlJoinNewOnly(True)

            # planetN
            newPlanets = {}
            newPlanets["left"] = list(set(self.obj1.planetObjects) -
                                      set(self.obj2.planetObjects))
            newPlanets["right"] = list(set(self.obj2.planetObjects) -
                                       set(self.obj1.planetObjects))

            # planetDN and DC:
            newPlanetsData = {}
            planetsDataChange = {}

            # examine all planets attached to system
            '''
            print("+++++++++++++++++++++++++++++")
            print(self.obj1.planetObjects)
            print(self.obj1.planetObjects[0])
            print(self.obj1.nameToPlanet)

            print(self.obj2.planetObjects)
            print(self.obj2.planetObjects[0])
            print(self.obj2.nameToPlanet)

            print("+++++++++++++++++++++++++++++")
            '''
            for planet in self.obj1.planetObjects:
                # if (planet in self.obj2.planetObjects):
                if (planet.name in self.obj2.nameToPlanet):
                    # create comparartor instance on planets
                    planetCompare = Comparator(planet,
                                               self.obj2.nameToPlanet[
                                                   planet.name], self.origin)
                    # get dictionary of new planet data for that planet
                    newPlanetsData[planet.name] = planetCompare.sqlJoinNewOnly(
                        True)
                    # get dictionary of changed planet data for that planet
                    planetsDataChange[planet.name] = \
                        planetCompare.innerJoinDiff()

            # generates output
            output_dict = {}
            output_dict["starC"] = starDataChange
            output_dict["starN"] = starDataNew
            output_dict["planetN"] = newPlanets
            output_dict["planetDN"] = newPlanetsData
            output_dict["planetDC"] = planetsDataChange

            return output_dict


class ObjectTypeMismatchException(Exception):
    pass


class ObjectTypeIncompatibleException(Exception):
    pass


if __name__ == "__main__":
    import data_parsing.XML_data_parser as XML
    import data_parsing.CSV_data_parser as CSV

    EXO_planets = CSV.buildListPlanets("exoplanetEU_csv",
                                       ["mass", "radius", "period",
                                        "semimajoraxis"], "eu")
    a = XML.buildSystemFromXML()
    planets = a[5]
    for planet in EXO_planets:
        if planet.name == "11 Com b":
            b = planet
    b.data["mass"] = 20
    print(b)
    p = planets["11 Com b"]
    print(p)
    c = Comparator(b, p, "eu")
    d = c.sqlJoin(True)
    print(d)
    e = c.innerJoinDiff()
    print(e)

    stars = a[4]
    xml = stars["11 Com"]
    print(xml)
    bob = CSV.buildDictStarExistingField("exoplanetEU_csv", "eu")
    ayy = bob["11 Com"]
    ayy.planetObjects[0].data["mass"] = 21
    z = Comparator(ayy, xml, "eu")
    f = z.starCompare()
    print("STAR COMPARE----------------------------------------")

    print(f)
    print(f["planetN"]["left"][0])
    print(f["planetN"]["right"][0])


    print(ayy.planetObjects[0])
    print(xml.planetObjects[0])
    qq = z.proposedChangeStarCompare()
    print(qq)
    for proposed_change in qq:
        print(proposed_change)
        # print(qq[0])
    print(f)