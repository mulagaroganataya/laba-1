from uuid import uuid1

class Address:
    def init(
        self,
        country: str = None,
        city: str = None,
        street: str = None,
        house: int = None,
        building: str = None,
        floor: int = None,
        postal_code: str = None,
        latitude: float = None,
        longitude: float = None,
    ):
        try:
            if not all(
                [
                    country is None or isinstance(country, str),
                    city is None or isinstance(city, str),
                    street is None or isinstance(street, str),
                    house is None or isinstance(house, int),
                    building is None or isinstance(building, str),
                    entrance is None or isinstance(entrance, int),
                    floor is None or isinstance(floor, int),
                    postal_code is None or isinstance(postal_code, str),
                    latitude is None or isinstance(latitude, float),
                    longitude is None or isinstance(longitude, float),
                ]
            ):
                raise TypeError
            self.id = str(uuid1())
            self.country = country
            self.city = city
            self.street = street
            self.house = house
            self.building = building
            self.entrance = entrance
            self.floor = floor
            self.postal_code = postal_code
            self.latitude = latitude
            self.longitude = longitude
        except TypeError:
            print("Error: something wrong with types")
            return False
        except:
            print("Error with init Adverstisment")

    def update(
        self,
        country: str = None,
        city: str = None,
        street: str = None,
        house: int = None,
        building: str = None,
        entrance: int = None,
        floor: int = None,
        postal_code: str = None,
        latitude: float = None,
        longitude: float = None,
    ) -> bool:
        result = True
        try:
            if not all(
                [
                    country is None or isinstance(country, str),
                    city is None or isinstance(city, str),
                    street is None or isinstance(street, str),
                    house is None or isinstance(house, int),
                    building is None or isinstance(building, str),
                    entrance is None or isinstance(entrance, int),
                    floor is None or isinstance(floor, int),
                    postal_code is None or isinstance(postal_code, str),
                    latitude is None or isinstance(latitude, float),
                    longitude is None or isinstance(longitude, float),
                ]
            ):
                raise TypeError
            if country:
                self.country = country
            elif city:
                self.city = city
            elif street:
                self.street = street
            elif house:
                self.house = house
            elif building:
                self.building = building
            elif entrance:
                self.entrance = entrance
            elif floor:
                self.floor = floor
            elif postal_code:
                self.postal_code = postal_code
            elif latitude:
                self.latitude = latitude
            elif longitude:
                self.longitude = longitude
            else:
                result = False
        except TypeError:
            print("Error: something wrong with types")
            return False
        except:
            result = False
        return result

    def delete(self):
        result = True
        return result